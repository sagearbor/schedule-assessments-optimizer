#!/usr/bin/env python3
"""
MCP Server for Compliance Knowledge Base
Provides regulatory compliance checking and validation for clinical trial schedules
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, '/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools')

from mcp_server import MCPServer


class ComplianceChecker:
    """Checks clinical trial schedules for regulatory compliance"""

    def __init__(self):
        # Initialize compliance rules database
        self.ich_gcp_rules = self._load_ich_gcp_rules()
        self.fda_rules = self._load_fda_rules()
        self.eu_rules = self._load_eu_rules()

    def _load_ich_gcp_rules(self) -> Dict[str, Any]:
        """Load ICH-GCP compliance rules"""
        return {
            "informed_consent": {
                "required_before": "any_procedure",
                "reconsent_triggers": ["protocol_amendment", "new_risks"],
                "documentation": "written_signed_dated"
            },
            "safety_reporting": {
                "sae_reporting_timeline": "24_hours",
                "susar_reporting": "7_days_fatal_15_days_other"
            },
            "monitoring": {
                "frequency": "risk_based",
                "documentation": "monitoring_plan_required"
            }
        }

    def _load_fda_rules(self) -> Dict[str, Any]:
        """Load FDA compliance rules"""
        return {
            "21_cfr_part_11": {
                "electronic_signatures": "required",
                "audit_trail": "required",
                "system_validation": "required"
            },
            "ind_requirements": {
                "annual_report": "required",
                "safety_reports": "15_days",
                "protocol_amendments": "submission_required"
            },
            "vulnerable_populations": {
                "pediatric": "special_protections",
                "pregnant_women": "additional_safeguards",
                "prisoners": "restricted"
            }
        }

    def _load_eu_rules(self) -> Dict[str, Any]:
        """Load EU Clinical Trial Regulation rules"""
        return {
            "eu_ctr_536_2014": {
                "transparency": "results_posting_required",
                "timelines": {
                    "initial_assessment": "45_days",
                    "substantial_modification": "38_days"
                }
            },
            "gdpr_compliance": {
                "consent_for_data": "explicit_required",
                "right_to_withdraw": "must_be_honored",
                "data_retention": "25_years_adult_studies"
            }
        }

    def check_compliance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check schedule for compliance issues"""

        schedule_data = params.get('schedule_data', {})
        region = params.get('region', 'US')  # Default to US regulations
        include_warnings = params.get('include_warnings', True)

        findings = []
        warnings = []
        recommendations = []

        # Check visit compliance
        visits = schedule_data.get('visits', [])
        if visits:
            visit_findings = self._check_visit_compliance(visits)
            findings.extend(visit_findings['errors'])
            warnings.extend(visit_findings['warnings'])

        # Check informed consent timing
        consent_check = self._check_informed_consent(visits)
        if consent_check['issues']:
            findings.extend(consent_check['issues'])

        # Check safety monitoring requirements
        safety_check = self._check_safety_monitoring(schedule_data)
        if safety_check['missing']:
            findings.extend(safety_check['missing'])
        recommendations.extend(safety_check['recommendations'])

        # Check vulnerable population requirements if applicable
        population = schedule_data.get('population', 'adult')
        if population != 'adult':
            pop_check = self._check_vulnerable_population_requirements(population, schedule_data)
            findings.extend(pop_check['issues'])
            recommendations.extend(pop_check['recommendations'])

        # Region-specific checks
        if region == 'US':
            fda_check = self._check_fda_specific(schedule_data)
            findings.extend(fda_check['issues'])
        elif region == 'EU':
            eu_check = self._check_eu_specific(schedule_data)
            findings.extend(eu_check['issues'])

        # Generate compliance score
        compliance_score = 100 - (len(findings) * 10) - (len(warnings) * 5)
        compliance_score = max(0, compliance_score)

        # Determine compliance status
        if compliance_score >= 90:
            status = "Compliant"
        elif compliance_score >= 70:
            status = "Minor Issues"
        elif compliance_score >= 50:
            status = "Major Issues"
        else:
            status = "Non-Compliant"

        result = {
            "compliance_score": compliance_score,
            "status": status,
            "findings": findings,
            "recommendations": recommendations,
            "checked_regulations": self._get_checked_regulations(region)
        }

        if include_warnings:
            result["warnings"] = warnings

        return result

    def _check_visit_compliance(self, visits: List[Dict]) -> Dict[str, Any]:
        """Check individual visits for compliance"""
        errors = []
        warnings = []

        for i, visit in enumerate(visits):
            visit_name = visit.get('name', f'Visit {i+1}')
            day = visit.get('day', 0)

            # Check for required assessments
            assessments = visit.get('assessments', [])
            assessment_names = [a.get('name', '').lower() for a in assessments]

            # Screening visit checks
            if 'screening' in visit_name.lower() and i == 0:
                if 'informed consent' not in ' '.join(assessment_names):
                    errors.append({
                        "type": "missing_consent",
                        "severity": "High",
                        "visit": visit_name,
                        "description": "Informed consent must be obtained at screening visit"
                    })

            # Check visit windows
            if i > 0:
                prev_day = visits[i-1].get('day', 0)
                gap = day - prev_day
                if gap < 3 and 'safety' not in visit_name.lower():
                    warnings.append({
                        "type": "visit_spacing",
                        "severity": "Medium",
                        "visit": visit_name,
                        "description": f"Visit spacing of {gap} days may be too short for patient burden"
                    })

            # Check for safety assessments
            if any('treatment' in v_name.lower() for v_name in [visit_name]):
                if not any('safety' in a or 'adverse' in a or 'ae' in a for a in assessment_names):
                    errors.append({
                        "type": "missing_safety",
                        "severity": "High",
                        "visit": visit_name,
                        "description": "Treatment visits must include safety assessments"
                    })

        return {"errors": errors, "warnings": warnings}

    def _check_informed_consent(self, visits: List[Dict]) -> Dict[str, Any]:
        """Check informed consent compliance"""
        issues = []

        if not visits:
            return {"issues": issues}

        first_visit = visits[0]
        assessments = first_visit.get('assessments', [])
        assessment_names = [a.get('name', '').lower() for a in assessments]

        consent_found = False
        consent_position = -1

        for i, name in enumerate(assessment_names):
            if 'consent' in name or 'icf' in name:
                consent_found = True
                consent_position = i
                break

        if not consent_found:
            issues.append({
                "type": "missing_consent",
                "severity": "Critical",
                "description": "No informed consent process found in schedule"
            })
        elif consent_position > 0:
            # Check if any procedures come before consent
            procedures_before = assessment_names[:consent_position]
            if any('procedure' in p or 'test' in p for p in procedures_before):
                issues.append({
                    "type": "consent_timing",
                    "severity": "Critical",
                    "description": "Procedures scheduled before informed consent"
                })

        return {"issues": issues}

    def _check_safety_monitoring(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check safety monitoring requirements"""
        missing = []
        recommendations = []

        phase = schedule_data.get('phase', '2')
        visits = schedule_data.get('visits', [])

        # Count safety assessments
        safety_count = 0
        for visit in visits:
            assessments = visit.get('assessments', [])
            for assessment in assessments:
                name = assessment.get('name', '').lower()
                if any(term in name for term in ['safety', 'adverse', 'ae', 'vital', 'lab']):
                    safety_count += 1

        # Phase-specific requirements
        if phase in ['1', '2']:
            if safety_count < len(visits) * 0.8:
                missing.append({
                    "type": "insufficient_safety_monitoring",
                    "severity": "High",
                    "description": f"Phase {phase} studies require more frequent safety monitoring"
                })
                recommendations.append("Add safety assessments to all treatment visits")

        # Check for safety run-in period
        if phase == '1' and len(visits) > 0:
            first_treatment_visit = next((v for v in visits if 'treatment' in v.get('name', '').lower()), None)
            if first_treatment_visit:
                recommendations.append("Consider adding safety run-in period for Phase 1 study")

        # Check for DSMB requirements
        duration = schedule_data.get('total_duration_days', 0)
        if duration > 365 or phase in ['2', '3']:
            recommendations.append("Establish Data Safety Monitoring Board (DSMB) for long-duration or late-phase study")

        return {"missing": missing, "recommendations": recommendations}

    def _check_vulnerable_population_requirements(self, population: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check requirements for vulnerable populations"""
        issues = []
        recommendations = []

        if population == 'pediatric':
            issues.append({
                "type": "vulnerable_population",
                "severity": "Medium",
                "description": "Pediatric study requires additional safeguards and assent process"
            })
            recommendations.extend([
                "Implement age-appropriate assent process",
                "Include parental/guardian consent",
                "Consider age-appropriate assessment tools",
                "Plan for DSMB with pediatric expertise"
            ])

        elif population == 'elderly':
            recommendations.extend([
                "Consider cognitive assessment requirements",
                "Plan for potential caregiver involvement",
                "Adjust visit frequency for patient burden"
            ])

        elif population == 'pregnant':
            issues.append({
                "type": "vulnerable_population",
                "severity": "High",
                "description": "Studies in pregnant women require additional FDA review"
            })
            recommendations.extend([
                "Include fetal monitoring requirements",
                "Plan for obstetric consultant involvement",
                "Implement pregnancy registry"
            ])

        return {"issues": issues, "recommendations": recommendations}

    def _check_fda_specific(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check FDA-specific requirements"""
        issues = []

        # Check for required FDA elements
        protocol_name = schedule_data.get('protocol_name', '')
        if 'IND' not in protocol_name and schedule_data.get('phase') in ['1', '2', '3']:
            issues.append({
                "type": "regulatory",
                "severity": "Medium",
                "description": "IND number should be referenced for interventional studies"
            })

        return {"issues": issues}

    def _check_eu_specific(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check EU-specific requirements"""
        issues = []

        # GDPR requirements
        visits = schedule_data.get('visits', [])
        data_consent_found = False

        for visit in visits:
            assessments = visit.get('assessments', [])
            for assessment in assessments:
                if 'data' in assessment.get('name', '').lower() and 'consent' in assessment.get('name', '').lower():
                    data_consent_found = True
                    break

        if not data_consent_found:
            issues.append({
                "type": "gdpr",
                "severity": "High",
                "description": "GDPR requires explicit consent for data processing"
            })

        return {"issues": issues}

    def _get_checked_regulations(self, region: str) -> List[str]:
        """Get list of regulations checked"""
        base_regs = ["ICH-GCP", "Declaration of Helsinki"]

        if region == 'US':
            base_regs.extend(["FDA 21 CFR Part 11", "FDA 21 CFR Part 50", "FDA 21 CFR Part 56"])
        elif region == 'EU':
            base_regs.extend(["EU CTR 536/2014", "GDPR", "EU GCP Directive"])
        elif region == 'Global':
            base_regs.extend(["FDA Regulations", "EU CTR", "GDPR", "Local Regulations"])

        return base_regs

    def get_regulations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get applicable regulations for a study"""

        region = params.get('region', 'US')
        phase = params.get('phase', '2')
        population = params.get('population', 'adult')

        regulations = {
            "primary_regulations": self._get_checked_regulations(region),
            "phase_specific": self._get_phase_specific_regulations(phase),
            "population_specific": self._get_population_specific_regulations(population),
            "documentation_requirements": [
                "Protocol",
                "Informed Consent Form",
                "Investigator's Brochure",
                "Case Report Forms",
                "Safety Reporting Plan"
            ]
        }

        if region == 'US':
            regulations["fda_submissions"] = [
                "IND Application",
                "Annual Reports",
                "Safety Reports",
                "Protocol Amendments"
            ]
        elif region == 'EU':
            regulations["eu_submissions"] = [
                "Clinical Trial Application",
                "Substantial Modifications",
                "Annual Safety Reports",
                "End of Trial Notification"
            ]

        return regulations

    def _get_phase_specific_regulations(self, phase: str) -> List[str]:
        """Get phase-specific regulations"""
        if phase == '1':
            return ["First-in-human guidelines", "Dose escalation rules", "Stopping rules"]
        elif phase == '2':
            return ["Efficacy monitoring requirements", "Futility analysis requirements"]
        elif phase == '3':
            return ["Pivotal trial requirements", "Multiple site coordination", "DSMB charter"]
        elif phase == '4':
            return ["Post-marketing surveillance", "REMS requirements (if applicable)"]
        return []

    def _get_population_specific_regulations(self, population: str) -> List[str]:
        """Get population-specific regulations"""
        if population == 'pediatric':
            return ["FDA Pediatric Research Equity Act", "EU Pediatric Regulation", "Assent requirements"]
        elif population == 'elderly':
            return ["Geriatric-specific guidelines", "Cognitive assessment requirements"]
        elif population == 'pregnant':
            return ["FDA Pregnancy and Lactation Labeling Rule", "Pregnancy registry requirements"]
        return []

    def validate_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a schedule against compliance rules"""

        schedule_data = params.get('schedule_data', {})
        validation_level = params.get('validation_level', 'standard')  # standard, strict, or minimal

        validation_results = {
            "is_valid": True,
            "validation_level": validation_level,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }

        # Check required fields
        required_fields = ['protocol_name', 'phase', 'visits']
        for field in required_fields:
            if field not in schedule_data or not schedule_data[field]:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["is_valid"] = False

        # Validate visits
        visits = schedule_data.get('visits', [])
        if visits:
            visit_validation = self._validate_visits(visits, validation_level)
            validation_results["errors"].extend(visit_validation["errors"])
            validation_results["warnings"].extend(visit_validation["warnings"])
            if visit_validation["errors"]:
                validation_results["is_valid"] = False

        # Validate phase
        phase = schedule_data.get('phase', '')
        if phase and phase not in ['1', '2', '3', '4']:
            validation_results["warnings"].append(f"Non-standard phase designation: {phase}")

        # Validate duration
        duration = schedule_data.get('total_duration_days', 0)
        if duration > 1825:  # 5 years
            validation_results["warnings"].append("Study duration exceeds 5 years - consider interim analyses")

        # Add suggestions based on validation
        if validation_level == 'strict':
            validation_results["suggestions"].append("Consider adding more safety monitoring points")
            validation_results["suggestions"].append("Review visit windows for flexibility")
        elif validation_level == 'minimal':
            validation_results["suggestions"].append("Consider upgrading to standard validation for better compliance")

        return validation_results

    def _validate_visits(self, visits: List[Dict], validation_level: str) -> Dict[str, Any]:
        """Validate visit structure and timing"""
        errors = []
        warnings = []

        for i, visit in enumerate(visits):
            # Check visit structure
            if 'name' not in visit:
                errors.append(f"Visit {i+1} missing name")
            if 'day' not in visit:
                errors.append(f"Visit {i+1} missing day")

            # Check visit timing
            if i > 0 and 'day' in visit and 'day' in visits[i-1]:
                if visit['day'] <= visits[i-1]['day']:
                    errors.append(f"Visit {visit.get('name', i+1)} has invalid timing sequence")

            # Check assessments
            if validation_level in ['standard', 'strict']:
                assessments = visit.get('assessments', [])
                if not assessments:
                    warnings.append(f"Visit {visit.get('name', i+1)} has no assessments defined")

                for assessment in assessments:
                    if 'name' not in assessment:
                        warnings.append(f"Assessment in visit {visit.get('name', i+1)} missing name")

        return {"errors": errors, "warnings": warnings}


def create_compliance_server():
    """Create MCP server for Compliance Knowledge Base"""

    server = MCPServer(name="compliance-knowledge-base", version="1.0.0")
    checker = ComplianceChecker()

    # Register check-compliance tool
    server.register_tool(
        name="check-compliance",
        description="Check schedule for regulatory compliance issues",
        input_schema={
            "type": "object",
            "properties": {
                "schedule_data": {
                    "type": "object",
                    "description": "The schedule data to check"
                },
                "region": {
                    "type": "string",
                    "enum": ["US", "EU", "Global"],
                    "description": "Regulatory region",
                    "default": "US"
                },
                "include_warnings": {
                    "type": "boolean",
                    "description": "Include warnings in addition to errors",
                    "default": True
                }
            },
            "required": ["schedule_data"]
        },
        handler=lambda args: checker.check_compliance(args)
    )

    # Register get-regulations tool
    server.register_tool(
        name="get-regulations",
        description="Get applicable regulations for a study",
        input_schema={
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "enum": ["US", "EU", "Global"],
                    "description": "Regulatory region"
                },
                "phase": {
                    "type": "string",
                    "description": "Clinical trial phase"
                },
                "population": {
                    "type": "string",
                    "description": "Study population",
                    "default": "adult"
                }
            },
            "required": ["region"]
        },
        handler=lambda args: checker.get_regulations(args)
    )

    # Register validate-schedule tool
    server.register_tool(
        name="validate-schedule",
        description="Validate schedule structure and compliance",
        input_schema={
            "type": "object",
            "properties": {
                "schedule_data": {
                    "type": "object",
                    "description": "The schedule data to validate"
                },
                "validation_level": {
                    "type": "string",
                    "enum": ["minimal", "standard", "strict"],
                    "description": "Level of validation to apply",
                    "default": "standard"
                }
            },
            "required": ["schedule_data"]
        },
        handler=lambda args: checker.validate_schedule(args)
    )

    # Register resources
    server.register_resource(
        uri="compliance://ich-gcp",
        name="ICH-GCP Guidelines",
        description="International Conference on Harmonisation - Good Clinical Practice guidelines",
        mime_type="text/plain"
    )

    server.register_resource(
        uri="compliance://fda-regulations",
        name="FDA Regulations",
        description="US FDA regulations for clinical trials",
        mime_type="text/plain"
    )

    server.register_resource(
        uri="compliance://eu-ctr",
        name="EU Clinical Trial Regulation",
        description="European Union Clinical Trial Regulation 536/2014",
        mime_type="text/plain"
    )

    return server


if __name__ == "__main__":
    # Create and run the server
    server = create_compliance_server()
    server.run()