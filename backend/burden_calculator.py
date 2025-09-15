from typing import List, Tuple
from models import Schedule, Visit, Assessment, BurdenScore, SiteBurdenScore


class BurdenCalculator:
    """
    Calculate burden scores for patients and sites based on schedule assessments.
    """
    
    # Weight factors for different burden components
    PATIENT_WEIGHTS = {
        "time": 0.25,
        "travel": 0.20,
        "invasiveness": 0.25,
        "fasting": 0.15,
        "discomfort": 0.15
    }
    
    SITE_WEIGHTS = {
        "staff_time": 0.30,
        "equipment": 0.25,
        "complexity": 0.25,
        "cost": 0.20
    }
    
    # Travel time assumptions (in hours)
    AVG_TRAVEL_TIME_PER_VISIT = 2.0  # Round trip
    
    def calculate_patient_burden(self, schedule: Schedule) -> BurdenScore:
        """
        Calculate comprehensive patient burden score.
        """
        total_time_hours = 0
        total_travel_count = 0
        invasive_count = 0
        fasting_count = 0
        discomfort_scores = []
        
        for visit in schedule.visits:
            # Add visit time
            total_time_hours += visit.total_duration_minutes / 60
            
            # Add travel time
            total_travel_count += 1
            total_time_hours += self.AVG_TRAVEL_TIME_PER_VISIT
            
            # Count burden factors
            for assessment in visit.assessments:
                if assessment.is_invasive:
                    invasive_count += 1
                if assessment.is_fasting_required:
                    fasting_count += 1
                discomfort_scores.append(assessment.patient_discomfort_level)
        
        # Calculate average discomfort
        avg_discomfort = sum(discomfort_scores) / len(discomfort_scores) if discomfort_scores else 0
        
        # Calculate component scores (normalized to 0-100)
        # Make scoring more sensitive to changes
        time_score = min(100, (total_time_hours / 30) * 100)  # 30 hours = max score (was 50)
        travel_score = min(100, (total_travel_count / 15) * 100)  # 15 visits = max score (was 20)
        invasive_score = min(100, (invasive_count / 10) * 100)  # 10 procedures = max score (was 15)
        fasting_score = min(100, (fasting_count / 7) * 100)  # 7 fasting = max score (was 10)
        discomfort_score = (avg_discomfort / 10) * 100  # Already on 1-10 scale
        
        # Calculate weighted total score
        total_score = (
            time_score * self.PATIENT_WEIGHTS["time"] +
            travel_score * self.PATIENT_WEIGHTS["travel"] +
            invasive_score * self.PATIENT_WEIGHTS["invasiveness"] +
            fasting_score * self.PATIENT_WEIGHTS["fasting"] +
            discomfort_score * self.PATIENT_WEIGHTS["discomfort"]
        )
        
        # Determine category
        category = self._categorize_burden(total_score)
        
        return BurdenScore(
            patient_time_hours=round(total_time_hours, 2),
            patient_travel_count=total_travel_count,
            invasive_procedures_count=invasive_count,
            fasting_requirements_count=fasting_count,
            average_discomfort_level=round(avg_discomfort, 2),
            total_score=round(total_score, 2),
            category=category
        )
    
    def calculate_site_burden(self, schedule: Schedule) -> SiteBurdenScore:
        """
        Calculate comprehensive site burden score.
        """
        total_staff_hours = 0
        unique_equipment = set()
        unique_staff_roles = set()
        total_cost = 0
        complex_procedures = 0
        
        for visit in schedule.visits:
            visit_staff_hours = 0
            
            for assessment in visit.assessments:
                # Calculate staff time (duration + 15 min prep/cleanup per assessment)
                staff_time = (assessment.duration_minutes + 15) / 60
                visit_staff_hours += staff_time * len(assessment.staff_required)
                
                # Track unique resources
                unique_equipment.update(assessment.equipment_needed)
                unique_staff_roles.update(assessment.staff_required)
                
                # Add cost
                total_cost += assessment.cost_estimate
                
                # Count complex procedures (invasive or requiring special equipment)
                if assessment.is_invasive or len(assessment.equipment_needed) > 2:
                    complex_procedures += 1
            
            total_staff_hours += visit_staff_hours
        
        # Calculate component scores (normalized to 0-100)
        staff_score = min(100, (total_staff_hours / 200) * 100)  # 200 hours = max score
        equipment_score = min(100, (len(unique_equipment) / 20) * 100)  # 20 unique items = max
        roles_score = min(100, (len(unique_staff_roles) / 10) * 100)  # 10 roles = max
        cost_score = min(100, (total_cost / 50000) * 100)  # $50k = max score
        complexity_score = min(100, (complex_procedures / 20) * 100)  # 20 complex = max
        
        # Calculate weighted total score
        total_score = (
            staff_score * self.SITE_WEIGHTS["staff_time"] +
            equipment_score * self.SITE_WEIGHTS["equipment"] +
            complexity_score * self.SITE_WEIGHTS["complexity"] +
            cost_score * self.SITE_WEIGHTS["cost"]
        )
        
        # Determine category
        category = self._categorize_burden(total_score)
        
        return SiteBurdenScore(
            total_staff_hours=round(total_staff_hours, 2),
            unique_equipment_count=len(unique_equipment),
            unique_staff_roles_count=len(unique_staff_roles),
            total_cost=round(total_cost, 2),
            complex_procedures_count=complex_procedures,
            total_score=round(total_score, 2),
            category=category
        )
    
    def _categorize_burden(self, score: float) -> str:
        """
        Categorize burden score into levels.
        """
        if score < 25:
            return "Low"
        elif score < 50:
            return "Moderate"
        elif score < 75:
            return "High"
        else:
            return "Very High"
    
    def compare_burden_scores(
        self, 
        original: BurdenScore, 
        optimized: BurdenScore
    ) -> Tuple[float, str]:
        """
        Compare two burden scores and return improvement percentage and summary.
        """
        if original.total_score > 0:
            improvement = ((original.total_score - optimized.total_score) / original.total_score) * 100
        else:
            improvement = 0
        
        summary_parts = []
        
        # Time reduction
        time_reduction = original.patient_time_hours - optimized.patient_time_hours
        if time_reduction > 0:
            summary_parts.append(f"{time_reduction:.1f} hours saved")
        
        # Visit reduction
        visit_reduction = original.patient_travel_count - optimized.patient_travel_count
        if visit_reduction > 0:
            summary_parts.append(f"{visit_reduction} fewer visits")
        
        # Invasive procedure reduction
        invasive_reduction = original.invasive_procedures_count - optimized.invasive_procedures_count
        if invasive_reduction > 0:
            summary_parts.append(f"{invasive_reduction} fewer invasive procedures")
        
        # Overall improvement
        if improvement > 0:
            summary_parts.append(f"{improvement:.1f}% overall burden reduction")
        
        summary = ". ".join(summary_parts) if summary_parts else "No significant burden reduction achieved"
        
        return improvement, summary
    
    def identify_burden_hotspots(self, schedule: Schedule) -> List[Tuple[str, float, List[str]]]:
        """
        Identify visits with highest burden and their contributing factors.
        Returns list of (visit_name, burden_score, factors)
        """
        hotspots = []
        
        for visit in schedule.visits:
            burden_score = 0
            factors = []
            
            # Calculate visit-specific burden
            visit_time = visit.total_duration_minutes / 60
            if visit_time > 4:
                burden_score += 30
                factors.append(f"Long duration ({visit_time:.1f} hours)")
            
            if visit.invasive_procedure_count > 2:
                burden_score += 25
                factors.append(f"{visit.invasive_procedure_count} invasive procedures")
            
            fasting_count = sum(1 for a in visit.assessments if a.is_fasting_required)
            if fasting_count > 0:
                burden_score += 15
                factors.append(f"Requires fasting")
            
            high_discomfort = [a for a in visit.assessments if a.patient_discomfort_level > 5]
            if high_discomfort:
                burden_score += 20
                factors.append(f"High discomfort procedures")
            
            if burden_score > 40:  # Threshold for hotspot
                hotspots.append((visit.name, burden_score, factors))
        
        # Sort by burden score
        hotspots.sort(key=lambda x: x[1], reverse=True)
        
        return hotspots[:5]  # Return top 5 hotspots