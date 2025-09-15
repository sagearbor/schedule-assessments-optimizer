from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import json
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./soa_optimizer.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    schedules = relationship("DBSchedule", back_populates="user", cascade="all, delete-orphan")
    optimization_history = relationship("DBOptimizationHistory", back_populates="user", cascade="all, delete-orphan")


class DBSchedule(Base):
    __tablename__ = "schedules"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    protocol_name = Column(String, nullable=False)
    protocol_version = Column(String, default="1.0")
    therapeutic_area = Column(String, nullable=False)
    phase = Column(String, nullable=False)
    total_duration_days = Column(Integer, nullable=False)
    visits_json = Column(Text, nullable=False)  # JSON string of visits
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_optimized = Column(Boolean, default=False)
    parent_schedule_id = Column(String, nullable=True)  # Reference to original if this is optimized version
    
    user = relationship("DBUser", back_populates="schedules")
    optimization_results = relationship("DBOptimizationHistory", foreign_keys="DBOptimizationHistory.original_schedule_id", back_populates="original_schedule")
    
    @property
    def visits(self):
        return json.loads(self.visits_json) if self.visits_json else []
    
    @visits.setter
    def visits(self, value):
        self.visits_json = json.dumps(value, default=str)


class DBOptimizationHistory(Base):
    __tablename__ = "optimization_history"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    original_schedule_id = Column(String, ForeignKey("schedules.id"), nullable=False)
    optimized_schedule_id = Column(String, ForeignKey("schedules.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Burden scores
    original_patient_burden_score = Column(Float)
    optimized_patient_burden_score = Column(Float)
    original_site_burden_score = Column(Float)
    optimized_site_burden_score = Column(Float)
    
    # Optimization details
    suggestions_json = Column(Text)  # JSON string of suggestions
    warnings_json = Column(Text)  # JSON string of warnings
    improvement_percentage = Column(Float)
    summary = Column(Text)
    
    # Statistics
    visits_consolidated = Column(Integer, default=0)
    assessments_eliminated = Column(Integer, default=0)
    remote_conversions = Column(Integer, default=0)
    cost_savings = Column(Float, default=0)
    time_savings_hours = Column(Float, default=0)
    
    notes = Column(Text, nullable=True)
    
    user = relationship("DBUser", back_populates="optimization_history")
    original_schedule = relationship("DBSchedule", foreign_keys=[original_schedule_id], back_populates="optimization_results")
    
    @property
    def suggestions(self):
        return json.loads(self.suggestions_json) if self.suggestions_json else []
    
    @suggestions.setter
    def suggestions(self, value):
        self.suggestions_json = json.dumps(value, default=str)
    
    @property
    def warnings(self):
        return json.loads(self.warnings_json) if self.warnings_json else []
    
    @warnings.setter
    def warnings(self, value):
        self.warnings_json = json.dumps(value, default=str)


class DBAssessmentTemplate(Base):
    __tablename__ = "assessment_templates"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_invasive = Column(Boolean, default=False)
    is_fasting_required = Column(Boolean, default=False)
    equipment_needed_json = Column(Text)
    staff_required_json = Column(Text)
    cost_estimate = Column(Float, default=0)
    patient_discomfort_level = Column(Integer, default=1)
    can_be_done_remotely = Column(Boolean, default=False)
    therapeutic_area = Column(String, nullable=True)
    
    @property
    def equipment_needed(self):
        return json.loads(self.equipment_needed_json) if self.equipment_needed_json else []
    
    @equipment_needed.setter
    def equipment_needed(self, value):
        self.equipment_needed_json = json.dumps(value)
    
    @property
    def staff_required(self):
        return json.loads(self.staff_required_json) if self.staff_required_json else []
    
    @staff_required.setter
    def staff_required(self, value):
        self.staff_required_json = json.dumps(value)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed assessment templates if empty
    db = SessionLocal()
    try:
        if db.query(DBAssessmentTemplate).count() == 0:
            seed_assessment_templates(db)
    finally:
        db.close()


def seed_assessment_templates(db: Session):
    templates = [
        {
            "id": "vital-signs-basic",
            "name": "Vital Signs",
            "type": "vital_signs",
            "duration_minutes": 10,
            "is_invasive": False,
            "equipment_needed": ["blood_pressure_cuff", "thermometer", "pulse_oximeter"],
            "staff_required": ["nurse"],
            "cost_estimate": 50,
            "patient_discomfort_level": 1
        },
        {
            "id": "cbc-blood-draw",
            "name": "Complete Blood Count",
            "type": "blood_draw",
            "duration_minutes": 15,
            "is_invasive": True,
            "equipment_needed": ["phlebotomy_kit"],
            "staff_required": ["phlebotomist", "lab_tech"],
            "cost_estimate": 150,
            "patient_discomfort_level": 3
        },
        {
            "id": "ct-scan-chest",
            "name": "CT Scan - Chest",
            "type": "imaging",
            "duration_minutes": 30,
            "is_invasive": False,
            "equipment_needed": ["ct_scanner"],
            "staff_required": ["radiologist", "radiology_tech"],
            "cost_estimate": 1200,
            "patient_discomfort_level": 2
        },
        {
            "id": "tumor-biopsy",
            "name": "Tumor Biopsy",
            "type": "biopsy",
            "duration_minutes": 60,
            "is_invasive": True,
            "equipment_needed": ["biopsy_kit", "ultrasound", "local_anesthetic"],
            "staff_required": ["physician", "nurse", "pathologist"],
            "cost_estimate": 2500,
            "patient_discomfort_level": 7
        },
        {
            "id": "ecg-12lead",
            "name": "12-Lead ECG",
            "type": "ecg",
            "duration_minutes": 15,
            "is_invasive": False,
            "equipment_needed": ["ecg_machine"],
            "staff_required": ["nurse", "cardiologist"],
            "cost_estimate": 200,
            "patient_discomfort_level": 1
        },
        {
            "id": "pk-blood-sample",
            "name": "Pharmacokinetic Blood Sample",
            "type": "pk_sample",
            "duration_minutes": 10,
            "is_invasive": True,
            "is_fasting_required": True,
            "equipment_needed": ["phlebotomy_kit", "special_tubes"],
            "staff_required": ["phlebotomist"],
            "cost_estimate": 100,
            "patient_discomfort_level": 3
        },
        {
            "id": "quality-life-questionnaire",
            "name": "Quality of Life Questionnaire",
            "type": "questionnaire",
            "duration_minutes": 20,
            "is_invasive": False,
            "can_be_done_remotely": True,
            "equipment_needed": ["tablet", "questionnaire_app"],
            "staff_required": ["study_coordinator"],
            "cost_estimate": 75,
            "patient_discomfort_level": 1
        },
        {
            "id": "physical-exam-complete",
            "name": "Complete Physical Examination",
            "type": "physical_exam",
            "duration_minutes": 30,
            "is_invasive": False,
            "equipment_needed": ["exam_table", "basic_medical_kit"],
            "staff_required": ["physician", "nurse"],
            "cost_estimate": 250,
            "patient_discomfort_level": 2
        },
        {
            "id": "urinalysis",
            "name": "Urinalysis",
            "type": "urinalysis",
            "duration_minutes": 10,
            "is_invasive": False,
            "equipment_needed": ["urine_cup", "test_strips"],
            "staff_required": ["nurse", "lab_tech"],
            "cost_estimate": 80,
            "patient_discomfort_level": 1
        },
        {
            "id": "cognitive-assessment",
            "name": "Montreal Cognitive Assessment",
            "type": "cognitive_test",
            "duration_minutes": 30,
            "is_invasive": False,
            "can_be_done_remotely": True,
            "equipment_needed": ["assessment_forms", "timer"],
            "staff_required": ["psychologist", "study_coordinator"],
            "cost_estimate": 200,
            "patient_discomfort_level": 2
        }
    ]
    
    for template_data in templates:
        template = DBAssessmentTemplate(**template_data)
        db.add(template)
    
    db.commit()