from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AssessmentType(str, Enum):
    VITAL_SIGNS = "vital_signs"
    BLOOD_DRAW = "blood_draw"
    IMAGING = "imaging"
    QUESTIONNAIRE = "questionnaire"
    PHYSICAL_EXAM = "physical_exam"
    ECG = "ecg"
    BIOPSY = "biopsy"
    URINALYSIS = "urinalysis"
    PK_SAMPLE = "pk_sample"
    COGNITIVE_TEST = "cognitive_test"


class Assessment(BaseModel):
    id: Optional[str] = None
    name: str
    type: AssessmentType
    duration_minutes: int = Field(ge=0)
    is_invasive: bool = False
    is_fasting_required: bool = False
    equipment_needed: List[str] = []
    staff_required: List[str] = []
    cost_estimate: float = Field(ge=0, default=0)
    patient_discomfort_level: int = Field(ge=1, le=10, default=1)
    can_be_done_remotely: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Complete Blood Count",
                "type": "blood_draw",
                "duration_minutes": 15,
                "is_invasive": True,
                "is_fasting_required": False,
                "equipment_needed": ["phlebotomy_kit"],
                "staff_required": ["nurse", "lab_tech"],
                "cost_estimate": 150.0,
                "patient_discomfort_level": 3,
                "can_be_done_remotely": False
            }
        }


class Visit(BaseModel):
    id: Optional[str] = None
    name: str
    day: int
    window_days_before: int = 0
    window_days_after: int = 0
    assessments: List[Assessment]
    is_screening: bool = False
    is_baseline: bool = False
    is_treatment: bool = False
    is_follow_up: bool = False
    notes: Optional[str] = None
    
    @property
    def total_duration_minutes(self) -> int:
        return sum(a.duration_minutes for a in self.assessments)
    
    @property
    def total_cost(self) -> float:
        return sum(a.cost_estimate for a in self.assessments)
    
    @property
    def invasive_procedure_count(self) -> int:
        return sum(1 for a in self.assessments if a.is_invasive)


class Schedule(BaseModel):
    id: Optional[str] = None
    protocol_name: str
    protocol_version: str = "1.0"
    therapeutic_area: str
    phase: str
    visits: List[Visit]
    total_duration_days: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def total_visits(self) -> int:
        return len(self.visits)
    
    @property
    def total_assessments(self) -> int:
        return sum(len(v.assessments) for v in self.visits)


class BurdenScore(BaseModel):
    patient_time_hours: float
    patient_travel_count: int
    invasive_procedures_count: int
    fasting_requirements_count: int
    average_discomfort_level: float
    total_score: float
    category: str  # Low, Moderate, High, Very High
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_time_hours": 24.5,
                "patient_travel_count": 12,
                "invasive_procedures_count": 8,
                "fasting_requirements_count": 3,
                "average_discomfort_level": 3.2,
                "total_score": 68.5,
                "category": "Moderate"
            }
        }


class SiteBurdenScore(BaseModel):
    total_staff_hours: float
    unique_equipment_count: int
    unique_staff_roles_count: int
    total_cost: float
    complex_procedures_count: int
    total_score: float
    category: str  # Low, Moderate, High, Very High


class OptimizationSuggestion(BaseModel):
    type: str  # consolidation, elimination, rescheduling, remote_conversion
    description: str
    impact: str
    visits_affected: List[str]
    estimated_burden_reduction: float
    implementation_difficulty: str  # Easy, Moderate, Hard


class ComplianceWarning(BaseModel):
    severity: str  # Low, Medium, High, Critical
    type: str  # regulatory, ethical, practical, safety
    description: str
    affected_visits: List[str]
    recommendation: str


class OptimizationResult(BaseModel):
    original_schedule: Schedule
    optimized_schedule: Schedule
    original_patient_burden: BurdenScore
    optimized_patient_burden: BurdenScore
    original_site_burden: SiteBurdenScore
    optimized_site_burden: SiteBurdenScore
    suggestions: List[OptimizationSuggestion]
    warnings: List[ComplianceWarning]
    improvement_percentage: float
    summary: str
    mcp_consensus_info: Optional[Dict[str, Any]] = None


class ScheduleComparison(BaseModel):
    schedule_id: str
    changes_made: List[Dict[str, Any]]
    burden_reduction: Dict[str, float]
    cost_savings: float
    time_savings_hours: float
    visits_consolidated: int
    assessments_eliminated: int
    remote_conversions: int


class DemoDataRequest(BaseModel):
    therapeutic_area: str = "oncology"
    phase: str = "2"
    complexity: str = "moderate"  # simple, moderate, complex


class User(BaseModel):
    id: Optional[str] = None
    email: str
    full_name: str
    organization: Optional[str] = None
    role: str = "user"  # user, admin
    created_at: Optional[datetime] = None
    is_active: bool = True


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    organization: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class OptimizationHistory(BaseModel):
    id: Optional[str] = None
    user_id: str
    original_schedule_id: str
    optimized_schedule_id: str
    created_at: datetime
    suggestions_applied: List[str]
    notes: Optional[str] = None