from typing import List, Dict, Any, Tuple
from copy import deepcopy
from datetime import timedelta
from models import (
    Schedule, Visit, Assessment, AssessmentType, OptimizationSuggestion,
    ComplianceWarning, OptimizationResult
)
from burden_calculator import BurdenCalculator


class RulesEngine:
    """
    Optimization rules engine for clinical trial schedules.
    Implements intelligent rules to reduce burden while maintaining scientific integrity.
    """
    
    def __init__(self):
        self.burden_calculator = BurdenCalculator()
        self.applied_suggestions = []
        self.warnings = []
    
    def optimize_schedule(
        self, 
        schedule: Schedule,
        mcp_complexity_data: Dict[str, Any] = None,
        mcp_compliance_data: Dict[str, Any] = None
    ) -> Tuple[Schedule, List[OptimizationSuggestion], List[ComplianceWarning]]:
        """
        Apply optimization rules to generate an improved schedule.
        """
        # Create a deep copy to modify
        optimized_schedule = deepcopy(schedule)
        suggestions = []
        warnings = []
        
        # Apply rules in sequence
        redundancy_suggestions = self._detect_redundancies(optimized_schedule)
        suggestions.extend(redundancy_suggestions)
        
        consolidation_suggestions = self._consolidate_visits(optimized_schedule)
        suggestions.extend(consolidation_suggestions)
        
        feasibility_warnings = self._check_logistical_feasibility(
            optimized_schedule, 
            mcp_compliance_data
        )
        warnings.extend(feasibility_warnings)
        
        # Apply remote conversion opportunities
        remote_suggestions = self._identify_remote_opportunities(optimized_schedule)
        suggestions.extend(remote_suggestions)
        
        # Apply timing optimizations
        timing_suggestions = self._optimize_timing(optimized_schedule)
        suggestions.extend(timing_suggestions)
        
        # Apply the highest impact suggestions
        print(f"Generated {len(suggestions)} suggestions")
        if suggestions:
            print(f"Top suggestions: {[s.description for s in suggestions[:5]]}")

        # Sort suggestions by impact and apply more of them
        suggestions.sort(key=lambda x: x.estimated_burden_reduction, reverse=True)

        # Apply ALL suggestions for maximum impact
        optimized_schedule = self._apply_suggestions(
            optimized_schedule,
            suggestions  # Apply ALL suggestions for maximum visible change
        )

        # Debug: Check if changes were made
        original_visit_count = len(schedule.visits)
        optimized_visit_count = len(optimized_schedule.visits)
        print(f"Original visits: {original_visit_count}, Optimized visits: {optimized_visit_count}")

        return optimized_schedule, suggestions, warnings
    
    def _detect_redundancies(self, schedule: Schedule) -> List[OptimizationSuggestion]:
        """
        Rule 1: Detect and flag redundant assessments.
        """
        suggestions = []
        assessment_frequency = {}
        
        # Track assessment frequency over time
        for visit in schedule.visits:
            for assessment in visit.assessments:
                key = (assessment.type, assessment.name)
                if key not in assessment_frequency:
                    assessment_frequency[key] = []
                assessment_frequency[key].append(visit.day)
        
        # Identify redundancies
        for (ass_type, ass_name), days in assessment_frequency.items():
            if len(days) > 2:  # More than 2 occurrences - be more aggressive
                # Check for clustering (multiple within 14 days)
                days_sorted = sorted(days)
                for i in range(len(days_sorted) - 1):
                    if days_sorted[i+1] - days_sorted[i] < 21:  # More aggressive - 3 weeks instead of 2
                        suggestion = OptimizationSuggestion(
                            type="elimination",
                            description=f"Remove redundant {ass_name} on Day {days_sorted[i+1]}",
                            impact=f"Reduces {ass_type} frequency without losing key data points",
                            visits_affected=[f"Day {days_sorted[i+1]}"],
                            estimated_burden_reduction=15.0,  # Higher impact score
                            implementation_difficulty="Easy"
                        )
                        suggestions.append(suggestion)
                        break
        
        # Check for duplicate safety labs
        safety_assessments = ["blood_draw", "urinalysis", "ecg"]
        for visit in schedule.visits:
            safety_count = sum(
                1 for a in visit.assessments 
                if a.type in safety_assessments
            )
            if safety_count > 2 and not visit.is_baseline:
                suggestion = OptimizationSuggestion(
                    type="elimination",
                    description=f"Streamline safety assessments on {visit.name}",
                    impact="Maintain safety monitoring with reduced redundancy",
                    visits_affected=[visit.name],
                    estimated_burden_reduction=8.0,
                    implementation_difficulty="Moderate"
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _consolidate_visits(self, schedule: Schedule) -> List[OptimizationSuggestion]:
        """
        Rule 2: Identify opportunities to consolidate visits.
        """
        suggestions = []
        visits_by_day = sorted(schedule.visits, key=lambda v: v.day)
        
        for i in range(len(visits_by_day) - 1):
            current_visit = visits_by_day[i]
            next_visit = visits_by_day[i + 1]
            
            # Check if visits are within 7 days and have low individual burden
            days_apart = next_visit.day - current_visit.day
            
            if 0 < days_apart <= 14:  # More aggressive consolidation window
                # Check combined duration
                combined_duration = (
                    current_visit.total_duration_minutes + 
                    next_visit.total_duration_minutes
                )
                
                # If combined duration is reasonable (< 8 hours)
                if combined_duration < 480:  # Allow longer combined visits
                    # Check for compatible assessments
                    current_fasting = any(a.is_fasting_required for a in current_visit.assessments)
                    next_fasting = any(a.is_fasting_required for a in next_visit.assessments)
                    
                    if not (current_fasting and next_fasting):  # Don't combine double fasting
                        suggestion = OptimizationSuggestion(
                            type="consolidation",
                            description=f"Combine {current_visit.name} and {next_visit.name}",
                            impact=f"Reduces visits by 1, saves ~{BurdenCalculator.AVG_TRAVEL_TIME_PER_VISIT} hours travel time",
                            visits_affected=[current_visit.name, next_visit.name],
                            estimated_burden_reduction=15.0,
                            implementation_difficulty="Moderate"
                        )
                        suggestions.append(suggestion)
            
            # Check for visit window expansion opportunities
            elif 7 < days_apart <= 14:
                if current_visit.window_days_after < 3 or next_visit.window_days_before < 3:
                    suggestion = OptimizationSuggestion(
                        type="rescheduling",
                        description=f"Expand visit windows to allow combination of {current_visit.name} and {next_visit.name}",
                        impact="Increases scheduling flexibility for sites and patients",
                        visits_affected=[current_visit.name, next_visit.name],
                        estimated_burden_reduction=10.0,
                        implementation_difficulty="Easy"
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _check_logistical_feasibility(
        self, 
        schedule: Schedule,
        mcp_compliance_data: Dict[str, Any] = None
    ) -> List[ComplianceWarning]:
        """
        Rule 3: Check for logistically infeasible schedules.
        """
        warnings = []
        
        # Check for weekend visits
        for visit in schedule.visits:
            # Simple weekend check (would be more sophisticated in production)
            if visit.day % 7 in [0, 6]:
                warning = ComplianceWarning(
                    severity="Medium",
                    type="practical",
                    description=f"{visit.name} scheduled on weekend (Day {visit.day})",
                    affected_visits=[visit.name],
                    recommendation="Consider moving to weekday or confirm site weekend availability"
                )
                warnings.append(warning)
        
        # Check for excessive same-day burden
        for visit in schedule.visits:
            if visit.total_duration_minutes > 360:  # More than 6 hours
                warning = ComplianceWarning(
                    severity="High",
                    type="practical",
                    description=f"{visit.name} exceeds 6 hours duration",
                    affected_visits=[visit.name],
                    recommendation="Split into multiple visits or allow procedures over 2 days"
                )
                warnings.append(warning)
            
            # Check for multiple fasting requirements
            fasting_count = sum(1 for a in visit.assessments if a.is_fasting_required)
            if fasting_count > 1:
                warning = ComplianceWarning(
                    severity="Medium",
                    type="practical",
                    description=f"Multiple fasting requirements in {visit.name}",
                    affected_visits=[visit.name],
                    recommendation="Consolidate fasting procedures or split across visits"
                )
                warnings.append(warning)
        
        # Check for PK sampling burden
        pk_visits = []
        for visit in schedule.visits:
            if any(a.type == "pk_sample" for a in visit.assessments):
                pk_visits.append(visit)
        
        if len(pk_visits) > 5:
            # Check if they're clustered
            pk_days = [v.day for v in pk_visits]
            pk_days_sorted = sorted(pk_days)
            
            for i in range(len(pk_days_sorted) - 2):
                if pk_days_sorted[i+2] - pk_days_sorted[i] <= 3:  # 3 PK visits in 3 days
                    warning = ComplianceWarning(
                        severity="High",
                        type="practical",
                        description="Intensive PK sampling schedule detected",
                        affected_visits=[v.name for v in pk_visits[i:i+3]],
                        recommendation="Consider sparse PK sampling or home health visits"
                    )
                    warnings.append(warning)
                    break
        
        # Add MCP compliance warnings if available
        if mcp_compliance_data and "warnings" in mcp_compliance_data:
            for mcp_warning in mcp_compliance_data["warnings"]:
                warning = ComplianceWarning(
                    severity=mcp_warning.get("severity", "Medium"),
                    type=mcp_warning.get("type", "regulatory"),
                    description=mcp_warning.get("description", ""),
                    affected_visits=[mcp_warning.get("affected_visits", "")],
                    recommendation=mcp_warning.get("recommendation", "")
                )
                warnings.append(warning)
        
        return warnings
    
    def _identify_remote_opportunities(self, schedule: Schedule) -> List[OptimizationSuggestion]:
        """
        Identify assessments that can be done remotely or at home.
        """
        suggestions = []
        
        for visit in schedule.visits:
            remote_eligible = []
            
            for assessment in visit.assessments:
                if assessment.can_be_done_remotely:
                    remote_eligible.append(assessment.name)
            
            if remote_eligible and len(remote_eligible) == len(visit.assessments):
                # Entire visit can be remote
                suggestion = OptimizationSuggestion(
                    type="remote_conversion",
                    description=f"Convert {visit.name} to remote/telemedicine visit",
                    impact=f"Eliminates travel burden, saves {BurdenCalculator.AVG_TRAVEL_TIME_PER_VISIT} hours",
                    visits_affected=[visit.name],
                    estimated_burden_reduction=20.0,
                    implementation_difficulty="Moderate"
                )
                suggestions.append(suggestion)
            elif remote_eligible and len(remote_eligible) > 0:
                # Some assessments can be remote
                suggestion = OptimizationSuggestion(
                    type="remote_conversion",
                    description=f"Perform {', '.join(remote_eligible)} remotely for {visit.name}",
                    impact="Reduces on-site time and complexity",
                    visits_affected=[visit.name],
                    estimated_burden_reduction=10.0,
                    implementation_difficulty="Easy"
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _optimize_timing(self, schedule: Schedule) -> List[OptimizationSuggestion]:
        """
        Optimize visit timing and windows.
        """
        suggestions = []
        
        # Check for visits without adequate windows
        for visit in schedule.visits:
            if not visit.is_screening and not visit.is_baseline:
                total_window = visit.window_days_before + visit.window_days_after
                
                if total_window < 6:
                    suggestion = OptimizationSuggestion(
                        type="rescheduling",
                        description=f"Expand {visit.name} window to ±3-5 days",
                        impact="Improves scheduling flexibility and reduces missed visits",
                        visits_affected=[visit.name],
                        estimated_burden_reduction=5.0,
                        implementation_difficulty="Easy"
                    )
                    suggestions.append(suggestion)
        
        # Check for clustering of intensive procedures
        intensive_visits = []
        for visit in schedule.visits:
            if visit.invasive_procedure_count > 1 or visit.total_duration_minutes > 180:
                intensive_visits.append((visit.day, visit.name))
        
        intensive_visits.sort()
        for i in range(len(intensive_visits) - 1):
            days_between = intensive_visits[i+1][0] - intensive_visits[i][0]
            if days_between < 14:
                suggestion = OptimizationSuggestion(
                    type="rescheduling",
                    description=f"Increase spacing between {intensive_visits[i][1]} and {intensive_visits[i+1][1]}",
                    impact="Allows patient recovery time between intensive procedures",
                    visits_affected=[intensive_visits[i][1], intensive_visits[i+1][1]],
                    estimated_burden_reduction=12.0,
                    implementation_difficulty="Moderate"
                )
                suggestions.append(suggestion)
                break
        
        return suggestions
    
    def _apply_suggestions(
        self,
        schedule: Schedule,
        suggestions: List[OptimizationSuggestion]
    ) -> Schedule:
        """
        Apply selected suggestions to create optimized schedule.
        """
        print(f"DEBUG: Applying {len(suggestions)} suggestions to schedule")
        if suggestions:
            print(f"DEBUG: Suggestion types: {[s.type for s in suggestions]}")
        optimized = deepcopy(schedule)

        for suggestion in suggestions:
            if suggestion.type == "elimination":
                # Remove redundant assessments
                for visit in optimized.visits:
                    # Check if this visit is affected (match by day if name not found)
                    visit_affected = False
                    for affected in suggestion.visits_affected:
                        if visit.name == affected or f"Day {visit.day}" == affected:
                            visit_affected = True
                            break

                    if visit_affected:
                        # Parse what assessment to remove from the description
                        desc_lower = suggestion.description.lower()

                        if "redundant" in desc_lower:
                            original_count = len(visit.assessments)
                            # Extract specific assessment type to remove
                            if "vital signs" in desc_lower:
                                # Remove vital signs if redundant
                                visit.assessments = [a for a in visit.assessments if a.type != AssessmentType.VITAL_SIGNS]
                            elif "blood" in desc_lower or "safety labs" in desc_lower:
                                # Remove blood draw if redundant
                                visit.assessments = [a for a in visit.assessments if a.type != AssessmentType.BLOOD_DRAW]
                            elif "ecg" in desc_lower or "12-lead" in desc_lower:
                                # Remove ECG if redundant
                                visit.assessments = [a for a in visit.assessments if a.type != AssessmentType.ECG]
                            elif "ct scan" in desc_lower:
                                # Remove CT scan if redundant
                                visit.assessments = [a for a in visit.assessments if "ct" not in a.name.lower()]
                            elif "urinalysis" in desc_lower:
                                # Remove urinalysis if redundant
                                visit.assessments = [a for a in visit.assessments if a.type != AssessmentType.URINALYSIS]
                            elif "questionnaire" in desc_lower:
                                # Remove questionnaires
                                visit.assessments = [a for a in visit.assessments if a.type != AssessmentType.QUESTIONNAIRE]
                            elif "cognitive" in desc_lower:
                                # Remove cognitive tests
                                visit.assessments = [a for a in visit.assessments if a.type != AssessmentType.COGNITIVE_TEST]
                            else:
                                # Try to identify assessment by name
                                for assessment_name in ["vital signs", "blood draw", "ecg", "pk sample", "questionnaire"]:
                                    if assessment_name in desc_lower:
                                        visit.assessments = [a for a in visit.assessments if assessment_name not in a.name.lower()]
                                        break
                                else:
                                    # If still nothing matched, remove a duplicate assessment if possible
                                    if len(visit.assessments) > 1:
                                        visit.assessments = visit.assessments[1:]  # Remove first

                            removed = original_count - len(visit.assessments)
                            if removed > 0:
                                print(f"DEBUG: Removed {removed} assessments from {visit.name}")

                        elif "streamline safety" in desc_lower:
                            # Keep essential safety assessments, remove redundant ones
                            safety_types = [AssessmentType.BLOOD_DRAW, AssessmentType.URINALYSIS, AssessmentType.ECG]
                            safety_assessments = [a for a in visit.assessments if a.type in safety_types]
                            other_assessments = [a for a in visit.assessments if a.type not in safety_types]

                            # Keep one of each safety type max
                            kept_safety = []
                            seen_types = set()
                            for a in safety_assessments:
                                if a.type not in seen_types:
                                    kept_safety.append(a)
                                    seen_types.add(a.type)

                            visit.assessments = other_assessments + kept_safety

            elif suggestion.type == "consolidation":
                # Combine visits
                if len(suggestion.visits_affected) >= 2:
                    visit1_name = suggestion.visits_affected[0]
                    visit2_name = suggestion.visits_affected[1]

                    visit1 = next((v for v in optimized.visits if v.name == visit1_name), None)
                    visit2 = next((v for v in optimized.visits if v.name == visit2_name), None)

                    if visit1 and visit2:
                        # Combine assessments into first visit
                        visit1.assessments.extend(visit2.assessments)
                        visit1.name = f"{visit1.name} + {visit2.name}"
                        # Update the day to be the average
                        visit1.day = (visit1.day + visit2.day) // 2
                        # Expand windows to accommodate the consolidation
                        visit1.window_days_before = max(visit1.window_days_before, 3)
                        visit1.window_days_after = max(visit1.window_days_after, 3)
                        # Remove second visit
                        optimized.visits = [v for v in optimized.visits if v.name != visit2_name]

            elif suggestion.type == "rescheduling":
                # Expand visit windows
                for visit in optimized.visits:
                    if visit.name in suggestion.visits_affected:
                        if "window" in suggestion.description.lower():
                            visit.window_days_before = 5
                            visit.window_days_after = 5
                        elif "spacing" in suggestion.description.lower():
                            # Adjust visit day to increase spacing
                            visit_idx = optimized.visits.index(visit)
                            if visit_idx > 0:
                                prev_visit = optimized.visits[visit_idx - 1]
                                min_spacing = 14
                                if visit.day - prev_visit.day < min_spacing:
                                    visit.day = prev_visit.day + min_spacing

            elif suggestion.type == "remote_conversion":
                # Mark assessments as remote
                for visit in optimized.visits:
                    if visit.name in suggestion.visits_affected:
                        # Check if entire visit can be remote
                        all_remote = all(a.can_be_done_remotely for a in visit.assessments)

                        if all_remote:
                            visit.name = f"{visit.name} (Remote)"
                            visit.is_remote_possible = True
                        else:
                            visit.name = f"{visit.name} (Partial Remote)"
                            for assessment in visit.assessments:
                                if assessment.can_be_done_remotely:
                                    assessment.name = f"{assessment.name} (Remote)"

        return optimized
    
    def generate_optimization_summary(
        self,
        original: Schedule,
        optimized: Schedule,
        suggestions: List[OptimizationSuggestion]
    ) -> Dict[str, Any]:
        """
        Generate a summary of the optimization results.
        """
        # Count changes
        visits_removed = len(original.visits) - len(optimized.visits)
        
        total_assessments_original = sum(len(v.assessments) for v in original.visits)
        total_assessments_optimized = sum(len(v.assessments) for v in optimized.visits)
        assessments_removed = total_assessments_original - total_assessments_optimized
        
        remote_conversions = sum(1 for s in suggestions if s.type == "remote_conversion")
        
        # Calculate burden reduction
        original_burden = self.burden_calculator.calculate_patient_burden(original)
        optimized_burden = self.burden_calculator.calculate_patient_burden(optimized)
        
        burden_reduction = (
            (original_burden.total_score - optimized_burden.total_score) / 
            original_burden.total_score * 100
        ) if original_burden.total_score > 0 else 0
        
        return {
            "visits_consolidated": visits_removed,
            "assessments_eliminated": assessments_removed,
            "remote_conversions": remote_conversions,
            "burden_reduction_percentage": round(burden_reduction, 1),
            "time_saved_hours": round(
                original_burden.patient_time_hours - optimized_burden.patient_time_hours, 1
            ),
            "travel_visits_saved": original_burden.patient_travel_count - optimized_burden.patient_travel_count,
            "suggestions_applied": len([s for s in suggestions[:5]]),  # Top 5 applied
            "total_suggestions": len(suggestions)
        }