import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
from sample_data import SampleDataGenerator
import json


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def sample_generator():
    return SampleDataGenerator()


@pytest.fixture
def sample_schedule(sample_generator):
    return sample_generator.generate_oncology_phase2_schedule()


@pytest.fixture
def auth_headers():
    """Create authenticated user and return headers."""
    # Register a test user
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "organization": "Test Org"
    })
    
    # Login to get token
    response = client.post("/login", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAPI:
    
    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
        assert response.json()["name"] == "SoA Optimizer API"
    
    def test_health(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_register(self):
        """Test user registration."""
        response = client.post("/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "organization": "Test Org"
        })
        
        assert response.status_code == 200
        assert "email" in response.json()
        assert response.json()["email"] == "newuser@example.com"
    
    def test_login(self):
        """Test user login."""
        # First register
        client.post("/register", json={
            "email": "logintest@example.com",
            "password": "password123",
            "full_name": "Login Test"
        })
        
        # Then login
        response = client.post("/login", data={
            "username": "logintest@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_get_current_user(self, auth_headers):
        """Test getting current user."""
        response = client.get("/me", headers=auth_headers)
        
        assert response.status_code == 200
        assert "email" in response.json()
        assert response.json()["email"] == "test@example.com"
    
    def test_optimize_schedule(self, sample_schedule):
        """Test schedule optimization endpoint."""
        response = client.post(
            "/optimize-schedule",
            json=json.loads(sample_schedule.json())
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "original_schedule" in result
        assert "optimized_schedule" in result
        assert "original_patient_burden" in result
        assert "optimized_patient_burden" in result
        assert "suggestions" in result
        assert "warnings" in result
        assert "improvement_percentage" in result
    
    def test_get_demo_data(self):
        """Test demo data endpoint."""
        response = client.post("/demo-data", json={
            "therapeutic_area": "oncology",
            "phase": "2"
        })
        
        assert response.status_code == 200
        schedule = response.json()
        
        assert "protocol_name" in schedule
        assert "visits" in schedule
        assert len(schedule["visits"]) > 0
    
    def test_get_complex_demo_data(self):
        """Test complex demo data endpoint."""
        response = client.get("/demo-data/complex")
        
        assert response.status_code == 200
        schedule = response.json()
        
        assert "protocol_name" in schedule
        assert "TEST" in schedule["protocol_name"]
    
    def test_my_schedules(self, auth_headers, sample_schedule):
        """Test getting user's schedules."""
        # First optimize a schedule to create one
        client.post(
            "/optimize-schedule",
            json=json.loads(sample_schedule.json()),
            headers=auth_headers
        )
        
        # Then get schedules
        response = client.get("/my-schedules", headers=auth_headers)
        
        assert response.status_code == 200
        schedules = response.json()
        assert isinstance(schedules, list)
    
    def test_optimization_history(self, auth_headers, sample_schedule):
        """Test getting optimization history."""
        # First optimize a schedule
        client.post(
            "/optimize-schedule",
            json=json.loads(sample_schedule.json()),
            headers=auth_headers
        )
        
        # Then get history
        response = client.get("/optimization-history", headers=auth_headers)
        
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints."""
        response = client.get("/me")
        assert response.status_code == 401
        
        response = client.get("/my-schedules")
        assert response.status_code == 401
        
        response = client.get("/optimization-history")
        assert response.status_code == 401


class TestMCPIntegration:
    """Test MCP service integration (when services are running)."""
    
    @pytest.mark.skipif(True, reason="Requires MCP services to be running")
    def test_mcp_complexity_integration(self, sample_schedule):
        """Test integration with Protocol Complexity Analyzer."""
        # This test would run if MCP services are available
        pass
    
    @pytest.mark.skipif(True, reason="Requires MCP services to be running")
    def test_mcp_compliance_integration(self, sample_schedule):
        """Test integration with Compliance Knowledge Base."""
        # This test would run if MCP services are available
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])