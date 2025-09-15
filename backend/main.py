from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List
import httpx
import json
import uuid
import csv
import io
import os
from datetime import datetime, timedelta

from database import init_db, get_db, DBSchedule, DBOptimizationHistory, DBUser
from models import (
    Schedule, OptimizationResult, DemoDataRequest, 
    User, UserCreate, UserLogin, Token, 
    BurdenScore, SiteBurdenScore, ScheduleComparison
)
from auth import AuthService, get_optional_current_user
from burden_calculator import BurdenCalculator
from rules_engine import RulesEngine
from sample_data import SampleDataGenerator
# from mcp_integration import get_mcp_integration  # Commented out - module not available

app = FastAPI(
    title="Schedule of Assessments Optimizer",
    version="1.0.0",
    description="Optimize clinical trial schedules to reduce patient and site burden"
)

# MCP server URL
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8210")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3040", "http://localhost:8040", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Initialize services
burden_calculator = BurdenCalculator()
rules_engine = RulesEngine()
sample_generator = SampleDataGenerator()
auth_service = AuthService()
# mcp_integration = get_mcp_integration() if USE_MCP else None  # Commented out - module not available


@app.get("/")
def read_root():
    return {
        "name": "SoA Optimizer API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "optimize": "/optimize-schedule",
            "demo": "/demo-data",
            "auth": "/register, /login",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Authentication endpoints
@app.post("/register", response_model=User)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = auth_service.create_user(db, user_create)
    return User(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        organization=db_user.organization,
        role=db_user.role,
        created_at=db_user.created_at,
        is_active=db_user.is_active
    )


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and receive access token."""
    # Special case for demo user
    if form_data.username == "demo@example.com" and form_data.password == "demo123":
        access_token_expires = timedelta(minutes=1440)  # 24 hours
        access_token = auth_service.create_access_token(
            data={"sub": "demo@example.com"}, 
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=1440)  # 24 hours
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.get("/me", response_model=User)
def get_current_user(current_user: User = Depends(AuthService.get_current_active_user)):
    """Get current user information."""
    return current_user


# Main optimization endpoint
@app.post("/optimize-schedule", response_model=OptimizationResult)
async def optimize_schedule(
    schedule: Schedule,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Main endpoint to optimize a clinical trial schedule.
    Accepts a schedule and returns optimization suggestions.
    """
    try:
        # Log the incoming schedule for debugging
        print(f"Received schedule: {schedule.protocol_name}")
        print(f"Number of visits: {len(schedule.visits)}")
        if schedule.visits:
            print(f"First visit data: {schedule.visits[0].dict()}")
        # Save original schedule to database
        original_schedule_id = str(uuid.uuid4())
        db_schedule = DBSchedule(
            id=original_schedule_id,
            user_id=current_user.id if current_user else None,
            protocol_name=schedule.protocol_name,
            protocol_version=schedule.protocol_version,
            therapeutic_area=schedule.therapeutic_area,
            phase=schedule.phase,
            total_duration_days=schedule.total_duration_days,
            visits=[v.dict() for v in schedule.visits],
            is_optimized=False
        )
        db.add(db_schedule)
        
        # Calculate original burden scores
        original_patient_burden = burden_calculator.calculate_patient_burden(schedule)
        original_site_burden = burden_calculator.calculate_site_burden(schedule)
        
        # Call real MCP server for additional analysis
        mcp_complexity_data = None
        mcp_compliance_data = None

        try:
            async with httpx.AsyncClient() as client:
                # Call Study Complexity Calculator tool
                complexity_response = await client.post(
                    f"{MCP_SERVER_URL}/run_tool/study_complexity_calculator",
                    json={
                        "protocol_name": schedule.protocol_name,
                        "phase": schedule.phase,
                        "therapeutic_area": schedule.therapeutic_area,
                        "duration_days": schedule.total_duration_days,
                        "num_visits": len(schedule.visits),
                        "num_procedures": sum(len(v.assessments) for v in schedule.visits),
                        "num_sites": 10  # Default estimate
                    },
                    timeout=30.0
                )
                if complexity_response.status_code == 200:
                    mcp_complexity_data = complexity_response.json()
                    print(f"MCP Complexity score: {mcp_complexity_data.get('complexity_score', 0)}")

                # Call Compliance Knowledge Base tool
                compliance_response = await client.post(
                    f"{MCP_SERVER_URL}/run_tool/compliance_knowledge_base",
                    json={
                        "schedule_data": schedule.dict(),
                        "schema_type": "generic",
                        "include_warnings": True
                    },
                    timeout=30.0
                )
                if compliance_response.status_code == 200:
                    mcp_compliance_data = compliance_response.json()
                    print(f"MCP Compliance findings: {len(mcp_compliance_data.get('findings', []))} issues found")
        except Exception as e:
            print(f"MCP server call failed: {e}")
            # Continue without MCP data
        
        # Apply optimization rules
        optimized_schedule, suggestions, warnings = rules_engine.optimize_schedule(
            schedule,
            mcp_complexity_data,
            mcp_compliance_data
        )
        
        # Calculate optimized burden scores
        optimized_patient_burden = burden_calculator.calculate_patient_burden(optimized_schedule)
        optimized_site_burden = burden_calculator.calculate_site_burden(optimized_schedule)
        
        # Calculate improvement
        improvement_percentage, summary = burden_calculator.compare_burden_scores(
            original_patient_burden,
            optimized_patient_burden
        )
        
        # Save optimized schedule
        optimized_schedule_id = str(uuid.uuid4())
        optimized_db_schedule = DBSchedule(
            id=optimized_schedule_id,
            user_id=current_user.id if current_user else None,
            protocol_name=optimized_schedule.protocol_name,
            protocol_version=optimized_schedule.protocol_version,
            therapeutic_area=optimized_schedule.therapeutic_area,
            phase=optimized_schedule.phase,
            total_duration_days=optimized_schedule.total_duration_days,
            visits=[v.dict() for v in optimized_schedule.visits],
            is_optimized=True,
            parent_schedule_id=original_schedule_id
        )
        db.add(optimized_db_schedule)
        
        # Save optimization history
        optimization_stats = rules_engine.generate_optimization_summary(
            schedule, optimized_schedule, suggestions
        )
        
        history = DBOptimizationHistory(
            id=str(uuid.uuid4()),
            user_id=current_user.id if current_user else None,
            original_schedule_id=original_schedule_id,
            optimized_schedule_id=optimized_schedule_id,
            original_patient_burden_score=original_patient_burden.total_score,
            optimized_patient_burden_score=optimized_patient_burden.total_score,
            original_site_burden_score=original_site_burden.total_score,
            optimized_site_burden_score=optimized_site_burden.total_score,
            suggestions=[s.dict() for s in suggestions],
            warnings=[w.dict() for w in warnings],
            improvement_percentage=improvement_percentage,
            summary=summary,
            visits_consolidated=optimization_stats["visits_consolidated"],
            assessments_eliminated=optimization_stats["assessments_eliminated"],
            remote_conversions=optimization_stats["remote_conversions"],
            time_savings_hours=optimization_stats["time_saved_hours"]
        )
        db.add(history)
        db.commit()
        
        # Create response
        result = OptimizationResult(
            original_schedule=schedule,
            optimized_schedule=optimized_schedule,
            original_patient_burden=original_patient_burden,
            optimized_patient_burden=optimized_patient_burden,
            original_site_burden=original_site_burden,
            optimized_site_burden=optimized_site_burden,
            suggestions=suggestions,
            warnings=warnings,
            improvement_percentage=improvement_percentage,
            summary=summary
        )
        
        return result
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"ERROR in optimize_schedule: {str(e)}")
        print(f"TRACEBACK: {error_detail}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Demo data endpoint
@app.post("/demo-data", response_model=Schedule)
def get_demo_data(request: DemoDataRequest = None):
    """
    Get sample clinical trial schedule data for testing.
    """
    if request is None:
        request = DemoDataRequest()
    
    schedule = sample_generator.generate_sample_schedule(request)
    return schedule


@app.get("/demo-data/complex", response_model=Schedule)
def get_complex_demo_data():
    """
    Get a complex schedule with many optimization opportunities.
    """
    return sample_generator.generate_complex_schedule_with_issues()


# File upload endpoint
@app.post("/upload-schedule", response_model=Schedule)
async def upload_schedule(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Upload a schedule from CSV or JSON file.
    """
    print(f"Upload request received - filename: {file.filename}")
    print(f"File content type: {file.content_type}")
    print(f"User authenticated: {current_user is not None}")

    if not file.filename:
        print("Error: No filename provided")
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    if not file.filename.endswith(('.csv', '.json')):
        print(f"Error: Invalid file format - {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="File must be CSV or JSON format"
        )
    
    content = await file.read()
    print(f"File size: {len(content)} bytes")

    try:
        if file.filename.endswith('.json'):
            print("Parsing JSON file...")
            data = json.loads(content)
            print(f"JSON data keys: {list(data.keys())}")

            # Ensure visits is a list
            if 'visits' in data and data['visits']:
                print(f"Number of visits in JSON: {len(data['visits'])}")
                # Convert visit data to Visit objects if needed
                from models import Visit, Assessment
                visits = []
                for v in data['visits']:
                    assessments = []
                    for a in v.get('assessments', []):
                        assessments.append(Assessment(**a))
                    visit = Visit(
                        name=v['name'],
                        day=v['day'],
                        visit_type=v.get('visit_type', 'regular'),
                        assessments=assessments
                    )
                    visits.append(visit)
                data['visits'] = visits

            schedule = Schedule(**data)
            print(f"Successfully created schedule: {schedule.protocol_name}")
        else:
            # Parse CSV
            print("Parsing CSV file...")
            csv_data = csv.DictReader(io.StringIO(content.decode()))
            visits = []

            # This is a simplified CSV parser - in production would be more robust
            for row in csv_data:
                # Parse visit and assessment data from CSV
                # Implementation would depend on CSV format specification
                pass

            schedule = Schedule(
                protocol_name="Uploaded Schedule",
                protocol_version="1.0",
                therapeutic_area="Unknown",
                phase="2",
                visits=visits,
                total_duration_days=180
            )

        return schedule

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON format: {str(e)}"
        )
    except Exception as e:
        print(f"Error parsing file: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=400,
            detail=f"Error parsing file: {str(e)}"
        )


# History endpoints
@app.get("/my-schedules", response_model=List[Schedule])
def get_my_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    """Get all schedules for the current user."""
    db_schedules = db.query(DBSchedule).filter(
        DBSchedule.user_id == current_user.id
    ).order_by(DBSchedule.created_at.desc()).all()
    
    schedules = []
    for db_schedule in db_schedules:
        schedule = Schedule(
            id=db_schedule.id,
            protocol_name=db_schedule.protocol_name,
            protocol_version=db_schedule.protocol_version,
            therapeutic_area=db_schedule.therapeutic_area,
            phase=db_schedule.phase,
            visits=db_schedule.visits,
            total_duration_days=db_schedule.total_duration_days,
            created_at=db_schedule.created_at,
            updated_at=db_schedule.updated_at
        )
        schedules.append(schedule)
    
    return schedules


@app.get("/optimization-history")
def get_optimization_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_active_user)
):
    """Get optimization history for the current user."""
    history = db.query(DBOptimizationHistory).filter(
        DBOptimizationHistory.user_id == current_user.id
    ).order_by(DBOptimizationHistory.created_at.desc()).all()
    
    results = []
    for h in history:
        results.append({
            "id": h.id,
            "created_at": h.created_at,
            "original_schedule_id": h.original_schedule_id,
            "optimized_schedule_id": h.optimized_schedule_id,
            "improvement_percentage": h.improvement_percentage,
            "summary": h.summary,
            "time_savings_hours": h.time_savings_hours,
            "visits_consolidated": h.visits_consolidated,
            "assessments_eliminated": h.assessments_eliminated
        })
    
    return results


@app.get("/schedule/{schedule_id}", response_model=Schedule)
def get_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get a specific schedule by ID."""
    db_schedule = db.query(DBSchedule).filter(DBSchedule.id == schedule_id).first()
    
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check if user has access (if authenticated)
    if current_user and db_schedule.user_id and db_schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Schedule(
        id=db_schedule.id,
        protocol_name=db_schedule.protocol_name,
        protocol_version=db_schedule.protocol_version,
        therapeutic_area=db_schedule.therapeutic_area,
        phase=db_schedule.phase,
        visits=db_schedule.visits,
        total_duration_days=db_schedule.total_duration_days,
        created_at=db_schedule.created_at,
        updated_at=db_schedule.updated_at
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)