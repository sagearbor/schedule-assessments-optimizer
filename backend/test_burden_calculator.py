import pytest
from models import Schedule, Visit, Assessment, AssessmentType
from burden_calculator import BurdenCalculator
import uuid


@pytest.fixture
def sample_schedule():
    """Create a sample schedule for testing."""
    assessments = [
        Assessment(
            name="Blood Draw",
            type=AssessmentType.BLOOD_DRAW,
            duration_minutes=15,
            is_invasive=True,
            is_fasting_required=True,
            equipment_needed=["phlebotomy_kit"],
            staff_required=["nurse"],
            cost_estimate=150,
            patient_discomfort_level=3
        ),
        Assessment(
            name="Vital Signs",
            type=AssessmentType.VITAL_SIGNS,
            duration_minutes=10,
            is_invasive=False,
            equipment_needed=["blood_pressure_cuff"],
            staff_required=["nurse"],
            cost_estimate=50,
            patient_discomfort_level=1
        ),
        Assessment(
            name="CT Scan",
            type=AssessmentType.IMAGING,
            duration_minutes=45,
            is_invasive=False,
            equipment_needed=["ct_scanner"],
            staff_required=["radiologist", "tech"],
            cost_estimate=1200,
            patient_discomfort_level=2
        )
    ]
    
    visits = [
        Visit(
            id=str(uuid.uuid4()),
            name="Screening",
            day=-7,
            window_days_before=3,
            window_days_after=3,
            assessments=assessments,
            is_screening=True
        ),
        Visit(
            id=str(uuid.uuid4()),
            name="Baseline",
            day=1,
            assessments=assessments[:2],
            is_baseline=True
        ),
        Visit(
            id=str(uuid.uuid4()),
            name="Week 4",
            day=28,
            window_days_before=2,
            window_days_after=2,
            assessments=assessments
        )
    ]
    
    return Schedule(
        id=str(uuid.uuid4()),
        protocol_name="Test Protocol",
        protocol_version="1.0",
        therapeutic_area="Oncology",
        phase="2",
        visits=visits,
        total_duration_days=56
    )


@pytest.fixture
def burden_calculator():
    """Create a burden calculator instance."""
    return BurdenCalculator()


class TestBurdenCalculator:
    
    def test_calculate_patient_burden(self, burden_calculator, sample_schedule):
        """Test patient burden calculation."""
        burden_score = burden_calculator.calculate_patient_burden(sample_schedule)
        
        # Verify all fields are populated
        assert burden_score.patient_time_hours > 0
        assert burden_score.patient_travel_count == 3  # 3 visits
        assert burden_score.invasive_procedures_count == 2  # 2 blood draws
        assert burden_score.fasting_requirements_count == 2
        assert burden_score.average_discomfort_level > 0
        assert burden_score.total_score > 0
        assert burden_score.category in ["Low", "Moderate", "High", "Very High"]
    
    def test_calculate_site_burden(self, burden_calculator, sample_schedule):
        """Test site burden calculation."""
        burden_score = burden_calculator.calculate_site_burden(sample_schedule)
        
        # Verify all fields are populated
        assert burden_score.total_staff_hours > 0
        assert burden_score.unique_equipment_count > 0
        assert burden_score.unique_staff_roles_count > 0
        assert burden_score.total_cost > 0
        assert burden_score.complex_procedures_count >= 0
        assert burden_score.total_score > 0
        assert burden_score.category in ["Low", "Moderate", "High", "Very High"]
    
    def test_burden_categorization(self, burden_calculator):
        """Test burden score categorization."""
        assert burden_calculator._categorize_burden(10) == "Low"
        assert burden_calculator._categorize_burden(30) == "Moderate"
        assert burden_calculator._categorize_burden(60) == "High"
        assert burden_calculator._categorize_burden(80) == "Very High"
    
    def test_compare_burden_scores(self, burden_calculator, sample_schedule):
        """Test burden score comparison."""
        original_burden = burden_calculator.calculate_patient_burden(sample_schedule)
        
        # Create a simpler schedule
        simple_schedule = Schedule(
            id=str(uuid.uuid4()),
            protocol_name="Simple Protocol",
            protocol_version="1.0",
            therapeutic_area="Oncology",
            phase="2",
            visits=sample_schedule.visits[:1],  # Only first visit
            total_duration_days=14
        )
        
        optimized_burden = burden_calculator.calculate_patient_burden(simple_schedule)
        
        improvement, summary = burden_calculator.compare_burden_scores(
            original_burden, 
            optimized_burden
        )
        
        assert improvement > 0  # Should show improvement
        assert len(summary) > 0  # Should have a summary message
    
    def test_identify_burden_hotspots(self, burden_calculator, sample_schedule):
        """Test identification of high-burden visits."""
        hotspots = burden_calculator.identify_burden_hotspots(sample_schedule)
        
        assert isinstance(hotspots, list)
        if hotspots:
            # Check structure of hotspot data
            visit_name, burden_score, factors = hotspots[0]
            assert isinstance(visit_name, str)
            assert isinstance(burden_score, (int, float))
            assert isinstance(factors, list)
    
    def test_empty_schedule(self, burden_calculator):
        """Test handling of empty schedule."""
        empty_schedule = Schedule(
            id=str(uuid.uuid4()),
            protocol_name="Empty Protocol",
            protocol_version="1.0",
            therapeutic_area="Oncology",
            phase="2",
            visits=[],
            total_duration_days=0
        )
        
        burden_score = burden_calculator.calculate_patient_burden(empty_schedule)
        
        assert burden_score.patient_time_hours == 0
        assert burden_score.patient_travel_count == 0
        assert burden_score.total_score == 0
        assert burden_score.category == "Low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])