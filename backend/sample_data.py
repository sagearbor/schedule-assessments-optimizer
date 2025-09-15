from typing import List, Dict, Any
from models import (
    Assessment, Visit, Schedule, AssessmentType,
    DemoDataRequest
)
import random
from datetime import datetime
import uuid


class SampleDataGenerator:
    """
    Generate realistic clinical trial sample data for testing and demos.
    """
    
    def __init__(self):
        self.assessment_templates = self._create_assessment_templates()
    
    def _create_assessment_templates(self) -> Dict[str, Assessment]:
        """Create reusable assessment templates."""
        return {
            "vital_signs": Assessment(
                name="Vital Signs",
                type=AssessmentType.VITAL_SIGNS,
                duration_minutes=10,
                is_invasive=False,
                equipment_needed=["blood_pressure_cuff", "thermometer"],
                staff_required=["nurse"],
                cost_estimate=50,
                patient_discomfort_level=1,
                can_be_done_remotely=False
            ),
            "blood_draw_safety": Assessment(
                name="Safety Labs (CBC, Chemistry)",
                type=AssessmentType.BLOOD_DRAW,
                duration_minutes=15,
                is_invasive=True,
                equipment_needed=["phlebotomy_kit"],
                staff_required=["phlebotomist"],
                cost_estimate=200,
                patient_discomfort_level=3,
                is_fasting_required=True
            ),
            "blood_draw_pk": Assessment(
                name="PK Blood Sample",
                type=AssessmentType.PK_SAMPLE,
                duration_minutes=10,
                is_invasive=True,
                equipment_needed=["phlebotomy_kit", "special_tubes"],
                staff_required=["phlebotomist"],
                cost_estimate=150,
                patient_discomfort_level=3,
                is_fasting_required=False
            ),
            "ct_scan": Assessment(
                name="CT Scan with Contrast",
                type=AssessmentType.IMAGING,
                duration_minutes=45,
                is_invasive=False,
                equipment_needed=["ct_scanner", "contrast_agent"],
                staff_required=["radiologist", "radiology_tech"],
                cost_estimate=1500,
                patient_discomfort_level=3
            ),
            "mri_scan": Assessment(
                name="MRI Brain",
                type=AssessmentType.IMAGING,
                duration_minutes=60,
                is_invasive=False,
                equipment_needed=["mri_scanner"],
                staff_required=["radiologist", "radiology_tech"],
                cost_estimate=2000,
                patient_discomfort_level=4
            ),
            "tumor_biopsy": Assessment(
                name="Tumor Biopsy",
                type=AssessmentType.BIOPSY,
                duration_minutes=90,
                is_invasive=True,
                equipment_needed=["biopsy_kit", "ultrasound", "local_anesthetic"],
                staff_required=["physician", "nurse", "pathologist"],
                cost_estimate=3000,
                patient_discomfort_level=7
            ),
            "ecg": Assessment(
                name="12-Lead ECG",
                type=AssessmentType.ECG,
                duration_minutes=15,
                is_invasive=False,
                equipment_needed=["ecg_machine"],
                staff_required=["nurse"],
                cost_estimate=150,
                patient_discomfort_level=1
            ),
            "questionnaire_qol": Assessment(
                name="Quality of Life Questionnaire (EORTC QLQ-C30)",
                type=AssessmentType.QUESTIONNAIRE,
                duration_minutes=20,
                is_invasive=False,
                equipment_needed=["tablet"],
                staff_required=["study_coordinator"],
                cost_estimate=50,
                patient_discomfort_level=1,
                can_be_done_remotely=True
            ),
            "questionnaire_pain": Assessment(
                name="Pain Assessment (Brief Pain Inventory)",
                type=AssessmentType.QUESTIONNAIRE,
                duration_minutes=10,
                is_invasive=False,
                equipment_needed=["tablet"],
                staff_required=["study_coordinator"],
                cost_estimate=30,
                patient_discomfort_level=1,
                can_be_done_remotely=True
            ),
            "physical_exam": Assessment(
                name="Complete Physical Examination",
                type=AssessmentType.PHYSICAL_EXAM,
                duration_minutes=30,
                is_invasive=False,
                equipment_needed=["exam_table", "medical_kit"],
                staff_required=["physician"],
                cost_estimate=250,
                patient_discomfort_level=2
            ),
            "urinalysis": Assessment(
                name="Urinalysis",
                type=AssessmentType.URINALYSIS,
                duration_minutes=10,
                is_invasive=False,
                equipment_needed=["urine_cup", "test_strips"],
                staff_required=["nurse"],
                cost_estimate=40,
                patient_discomfort_level=1
            ),
            "cognitive_test": Assessment(
                name="Mini-Mental State Exam",
                type=AssessmentType.COGNITIVE_TEST,
                duration_minutes=20,
                is_invasive=False,
                equipment_needed=["assessment_forms"],
                staff_required=["psychologist"],
                cost_estimate=150,
                patient_discomfort_level=2,
                can_be_done_remotely=True
            )
        }
    
    def generate_oncology_phase2_schedule(self) -> Schedule:
        """Generate a realistic Phase 2 oncology trial schedule."""
        visits = []
        
        # Screening Visit (-14 to -1 days)
        screening_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ecg"],
            self.assessment_templates["ct_scan"],
            self.assessment_templates["tumor_biopsy"],
            self.assessment_templates["urinalysis"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Screening",
            day=-7,
            window_days_before=7,
            window_days_after=6,
            assessments=screening_assessments,
            is_screening=True
        ))
        
        # Baseline/Day 1 (First dose)
        baseline_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["blood_draw_pk"],
            self.assessment_templates["questionnaire_qol"],
            self.assessment_templates["questionnaire_pain"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Baseline/Day 1",
            day=1,
            assessments=baseline_assessments,
            is_baseline=True,
            is_treatment=True
        ))
        
        # Week 1 Safety
        week1_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ecg"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 1 Safety",
            day=8,
            window_days_before=1,
            window_days_after=1,
            assessments=week1_assessments
        ))
        
        # Week 2
        week2_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["blood_draw_pk"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 2",
            day=15,
            window_days_before=2,
            window_days_after=2,
            assessments=week2_assessments,
            is_treatment=True
        ))
        
        # Week 4 (End of Cycle 1)
        week4_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ct_scan"],
            self.assessment_templates["questionnaire_qol"],
            self.assessment_templates["urinalysis"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 4/End Cycle 1",
            day=29,
            window_days_before=3,
            window_days_after=3,
            assessments=week4_assessments
        ))
        
        # Week 6
        week6_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["blood_draw_safety"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 6",
            day=43,
            window_days_before=3,
            window_days_after=3,
            assessments=week6_assessments,
            is_treatment=True
        ))
        
        # Week 8 (End of Cycle 2)
        week8_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ct_scan"],
            self.assessment_templates["tumor_biopsy"],
            self.assessment_templates["questionnaire_qol"],
            self.assessment_templates["ecg"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 8/End Cycle 2",
            day=57,
            window_days_before=3,
            window_days_after=3,
            assessments=week8_assessments
        ))
        
        # Week 12 (End of Cycle 3)
        week12_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ct_scan"],
            self.assessment_templates["questionnaire_qol"],
            self.assessment_templates["questionnaire_pain"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 12/End Cycle 3",
            day=85,
            window_days_before=5,
            window_days_after=5,
            assessments=week12_assessments
        ))
        
        # Week 16 (End of Treatment)
        eot_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ct_scan"],
            self.assessment_templates["tumor_biopsy"],
            self.assessment_templates["questionnaire_qol"],
            self.assessment_templates["ecg"],
            self.assessment_templates["urinalysis"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 16/End of Treatment",
            day=113,
            window_days_before=7,
            window_days_after=7,
            assessments=eot_assessments
        ))
        
        # Follow-up Visit (30 days post-treatment)
        followup_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["questionnaire_qol"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="30-Day Follow-up",
            day=143,
            window_days_before=7,
            window_days_after=7,
            assessments=followup_assessments,
            is_follow_up=True
        ))
        
        return Schedule(
            id=str(uuid.uuid4()),
            protocol_name="ONCO-2024-001: Phase 2 Study of Novel TKI in Advanced NSCLC",
            protocol_version="1.0",
            therapeutic_area="Oncology",
            phase="2",
            visits=visits,
            total_duration_days=150,
            created_at=datetime.utcnow()
        )
    
    def generate_cardiology_phase3_schedule(self) -> Schedule:
        """Generate a realistic Phase 3 cardiology trial schedule."""
        visits = []
        
        # Screening
        screening_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ecg"],
            self.assessment_templates["urinalysis"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Screening",
            day=-14,
            window_days_before=14,
            window_days_after=13,
            assessments=screening_assessments,
            is_screening=True
        ))
        
        # Baseline
        baseline_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ecg"],
            self.assessment_templates["questionnaire_qol"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Baseline/Randomization",
            day=1,
            assessments=baseline_assessments,
            is_baseline=True,
            is_treatment=True
        ))
        
        # Month 1
        month1_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ecg"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Month 1",
            day=30,
            window_days_before=5,
            window_days_after=5,
            assessments=month1_assessments
        ))
        
        # Month 3
        month3_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ecg"],
            self.assessment_templates["questionnaire_qol"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Month 3",
            day=90,
            window_days_before=7,
            window_days_after=7,
            assessments=month3_assessments
        ))
        
        # Month 6
        month6_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ecg"],
            self.assessment_templates["questionnaire_qol"],
            self.assessment_templates["urinalysis"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Month 6",
            day=180,
            window_days_before=14,
            window_days_after=14,
            assessments=month6_assessments
        ))
        
        # Month 12
        month12_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["ecg"],
            self.assessment_templates["questionnaire_qol"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Month 12/End of Study",
            day=365,
            window_days_before=14,
            window_days_after=14,
            assessments=month12_assessments
        ))
        
        return Schedule(
            id=str(uuid.uuid4()),
            protocol_name="CARDIO-2024-001: Phase 3 Study of Novel ACE Inhibitor in Heart Failure",
            protocol_version="1.0",
            therapeutic_area="Cardiology",
            phase="3",
            visits=visits,
            total_duration_days=365,
            created_at=datetime.utcnow()
        )
    
    def generate_neurology_phase2_schedule(self) -> Schedule:
        """Generate a realistic Phase 2 neurology (Alzheimer's) trial schedule."""
        visits = []
        
        # Screening
        screening_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["mri_scan"],
            self.assessment_templates["cognitive_test"],
            self.assessment_templates["urinalysis"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Screening",
            day=-28,
            window_days_before=14,
            window_days_after=27,
            assessments=screening_assessments,
            is_screening=True
        ))
        
        # Baseline
        baseline_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["cognitive_test"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["blood_draw_pk"],
            self.assessment_templates["questionnaire_qol"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Baseline",
            day=1,
            assessments=baseline_assessments,
            is_baseline=True,
            is_treatment=True
        ))
        
        # Week 2
        week2_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["blood_draw_pk"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 2",
            day=15,
            window_days_before=2,
            window_days_after=2,
            assessments=week2_assessments
        ))
        
        # Month 1
        month1_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["cognitive_test"],
            self.assessment_templates["blood_draw_safety"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Month 1",
            day=30,
            window_days_before=3,
            window_days_after=3,
            assessments=month1_assessments
        ))
        
        # Month 3
        month3_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["cognitive_test"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["mri_scan"],
            self.assessment_templates["questionnaire_qol"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Month 3",
            day=90,
            window_days_before=7,
            window_days_after=7,
            assessments=month3_assessments
        ))
        
        # Month 6
        month6_assessments = [
            self.assessment_templates["vital_signs"],
            self.assessment_templates["physical_exam"],
            self.assessment_templates["cognitive_test"],
            self.assessment_templates["blood_draw_safety"],
            self.assessment_templates["mri_scan"],
            self.assessment_templates["questionnaire_qol"],
            self.assessment_templates["urinalysis"]
        ]
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Month 6/End of Treatment",
            day=180,
            window_days_before=7,
            window_days_after=7,
            assessments=month6_assessments
        ))
        
        return Schedule(
            id=str(uuid.uuid4()),
            protocol_name="NEURO-2024-001: Phase 2 Study of Monoclonal Antibody in Early Alzheimer's",
            protocol_version="1.0",
            therapeutic_area="Neurology",
            phase="2",
            visits=visits,
            total_duration_days=180,
            created_at=datetime.utcnow()
        )
    
    def generate_sample_schedule(self, request: DemoDataRequest) -> Schedule:
        """Generate sample schedule based on request parameters."""
        if request.therapeutic_area.lower() == "oncology":
            return self.generate_oncology_phase2_schedule()
        elif request.therapeutic_area.lower() == "cardiology":
            return self.generate_cardiology_phase3_schedule()
        elif request.therapeutic_area.lower() == "neurology":
            return self.generate_neurology_phase2_schedule()
        else:
            # Default to oncology
            return self.generate_oncology_phase2_schedule()
    
    def generate_complex_schedule_with_issues(self) -> Schedule:
        """Generate a schedule with many deliberate optimization opportunities."""
        visits = []

        # Screening visit
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Screening",
            day=-14,
            window_days_before=3,
            window_days_after=3,
            assessments=[
                self.assessment_templates["vital_signs"],
                self.assessment_templates["blood_draw_safety"],
                self.assessment_templates["ecg"],
                self.assessment_templates["physical_exam"],
                self.assessment_templates["ct_scan"]
            ]
        ))

        # Baseline - duplicates screening unnecessarily
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Baseline",
            day=0,
            assessments=[
                self.assessment_templates["vital_signs"],
                self.assessment_templates["blood_draw_safety"],
                self.assessment_templates["ecg"],  # Redundant - just done at screening
                self.assessment_templates["ct_scan"]  # Redundant - just done at screening
            ]
        ))

        # PROBLEM 1: Back-to-back visits that could be combined
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Day 3 Safety",
            day=3,
            assessments=[
                self.assessment_templates["vital_signs"],
                self.assessment_templates["blood_draw_safety"]
            ]
        ))

        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Day 5 PK",
            day=5,
            assessments=[
                self.assessment_templates["vital_signs"],  # Duplicate from Day 3
                self.assessment_templates["blood_draw_pk"]
            ]
        ))

        # PROBLEM 2: Weekly visits with identical assessments
        for week in [1, 2, 3, 4]:
            visits.append(Visit(
                id=str(uuid.uuid4()),
                name=f"Week {week}",
                day=week * 7,
                window_days_before=1,  # Too restrictive
                window_days_after=1,   # Too restrictive
                assessments=[
                    self.assessment_templates["vital_signs"],
                    self.assessment_templates["blood_draw_safety"],
                    self.assessment_templates["ecg"],  # ECG every week is excessive
                    self.assessment_templates["urinalysis"]  # Urinalysis every week is excessive
                ]
            ))

        # PROBLEM 3: Multiple imaging studies too close together
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 5 Imaging",
            day=35,
            assessments=[
                self.assessment_templates["ct_scan"],
                self.assessment_templates["mri_scan"],  # Both CT and MRI same day
                self.assessment_templates["tumor_biopsy"],
                self.assessment_templates["blood_draw_safety"]
            ]
        ))

        # PROBLEM 4: Another imaging visit too soon after Week 5
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="Week 6 Follow-up",
            day=42,
            assessments=[
                self.assessment_templates["ct_scan"],  # CT again after just 1 week
                self.assessment_templates["blood_draw_safety"],
                self.assessment_templates["vital_signs"]
            ]
        ))

        # PROBLEM 5: Excessive safety monitoring with redundant tests
        for week in range(8, 16):  # 8 consecutive weeks of identical visits
            assessments_list = [
                self.assessment_templates["vital_signs"],
                self.assessment_templates["blood_draw_safety"]
            ]
            if week % 2 == 0:  # ECG every other week
                assessments_list.append(self.assessment_templates["ecg"])
            if week % 3 == 0:  # Urinalysis every 3rd week
                assessments_list.append(self.assessment_templates["urinalysis"])

            visits.append(Visit(
                id=str(uuid.uuid4()),
                name=f"Week {week} Safety",
                day=week * 7,
                assessments=assessments_list
            ))

        # PROBLEM 6: End of study with unnecessary repeat of all tests
        visits.append(Visit(
            id=str(uuid.uuid4()),
            name="End of Study",
            day=120,
            assessments=[
                self.assessment_templates["vital_signs"],
                self.assessment_templates["blood_draw_safety"],
                self.assessment_templates["ecg"],
                self.assessment_templates["ct_scan"],
                self.assessment_templates["mri_scan"],  # Both imaging again
                self.assessment_templates["physical_exam"],
                self.assessment_templates["questionnaire_qol"],
                self.assessment_templates["urinalysis"],
                self.assessment_templates["cognitive_test"]  # Excessive assessments
            ]
        ))

        return Schedule(
            id=str(uuid.uuid4()),
            protocol_name="COMPLEX-UNOPT-2024: Protocol with Many Optimization Opportunities",
            protocol_version="1.0",
            therapeutic_area="Oncology",
            phase="2",
            visits=visits,
            total_duration_days=120,
            created_at=datetime.utcnow()
        )