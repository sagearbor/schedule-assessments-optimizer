import pytest
from models import Schedule, Visit, Assessment, AssessmentType, OptimizationSuggestion
from rules_engine import RulesEngine
from sample_data import SampleDataGenerator
import uuid


@pytest.fixture
def rules_engine():
    """Create a rules engine instance."""
    return RulesEngine()


@pytest.fixture
def sample_generator():
    """Create a sample data generator."""
    return SampleDataGenerator()


@pytest.fixture
def complex_schedule(sample_generator):
    """Get a complex schedule with optimization opportunities."""
    return sample_generator.generate_complex_schedule_with_issues()


class TestRulesEngine:
    
    def test_optimize_schedule(self, rules_engine, complex_schedule):
        """Test overall schedule optimization."""
        optimized, suggestions, warnings = rules_engine.optimize_schedule(complex_schedule)
        
        # Should return valid results
        assert isinstance(optimized, Schedule)
        assert isinstance(suggestions, list)
        assert isinstance(warnings, list)
        
        # Should have fewer or equal visits
        assert len(optimized.visits) <= len(complex_schedule.visits)
        
        # Should generate suggestions
        assert len(suggestions) > 0
    
    def test_detect_redundancies(self, rules_engine, complex_schedule):
        """Test redundancy detection."""
        suggestions = rules_engine._detect_redundancies(complex_schedule)
        
        assert isinstance(suggestions, list)
        
        # Check suggestion structure
        if suggestions:
            suggestion = suggestions[0]
            assert isinstance(suggestion, OptimizationSuggestion)
            assert suggestion.type in ["elimination", "consolidation", "rescheduling", "remote_conversion"]
            assert suggestion.estimated_burden_reduction > 0
    
    def test_consolidate_visits(self, rules_engine):
        """Test visit consolidation logic."""
        # Create closely scheduled visits
        visits = []
        for day in [1, 3, 7, 14]:  # Days 1 and 3 are close
            visits.append(Visit(
                id=str(uuid.uuid4()),
                name=f"Day {day}",
                day=day,
                assessments=[
                    Assessment(
                        name="Blood Draw",
                        type=AssessmentType.BLOOD_DRAW,
                        duration_minutes=15,
                        is_invasive=True,
                        equipment_needed=["phlebotomy_kit"],
                        staff_required=["nurse"],
                        cost_estimate=150,
                        patient_discomfort_level=3
                    )
                ]
            ))
        
        schedule = Schedule(
            id=str(uuid.uuid4()),
            protocol_name="Test Consolidation",
            protocol_version="1.0",
            therapeutic_area="Test",
            phase="2",
            visits=visits,
            total_duration_days=30
        )
        
        suggestions = rules_engine._consolidate_visits(schedule)
        
        assert len(suggestions) > 0
        # Should suggest consolidating Day 1 and Day 3
        consolidation_suggested = any(
            s.type == "consolidation" for s in suggestions
        )
        assert consolidation_suggested
    
    def test_check_logistical_feasibility(self, rules_engine):
        """Test logistical feasibility checking."""
        # Create a visit with excessive burden
        long_visit = Visit(
            id=str(uuid.uuid4()),
            name="Long Visit",
            day=7,
            assessments=[
                Assessment(
                    name=f"Assessment {i}",
                    type=AssessmentType.BLOOD_DRAW,
                    duration_minutes=60,
                    is_invasive=True,
                    is_fasting_required=True,
                    equipment_needed=["equipment"],
                    staff_required=["staff"],
                    cost_estimate=100,
                    patient_discomfort_level=5
                ) for i in range(8)  # 8 hours of assessments
            ]
        )
        
        schedule = Schedule(
            id=str(uuid.uuid4()),
            protocol_name="Test Feasibility",
            protocol_version="1.0",
            therapeutic_area="Test",
            phase="2",
            visits=[long_visit],
            total_duration_days=30
        )
        
        warnings = rules_engine._check_logistical_feasibility(schedule)
        
        assert len(warnings) > 0
        # Should warn about excessive duration
        duration_warning = any(
            "exceeds 6 hours" in w.description for w in warnings
        )
        assert duration_warning
    
    def test_identify_remote_opportunities(self, rules_engine):
        """Test identification of remote-eligible assessments."""
        visits = [
            Visit(
                id=str(uuid.uuid4()),
                name="Remote Eligible Visit",
                day=14,
                assessments=[
                    Assessment(
                        name="Questionnaire",
                        type=AssessmentType.QUESTIONNAIRE,
                        duration_minutes=20,
                        is_invasive=False,
                        equipment_needed=["tablet"],
                        staff_required=["coordinator"],
                        cost_estimate=50,
                        patient_discomfort_level=1,
                        can_be_done_remotely=True
                    )
                ]
            )
        ]
        
        schedule = Schedule(
            id=str(uuid.uuid4()),
            protocol_name="Test Remote",
            protocol_version="1.0",
            therapeutic_area="Test",
            phase="2",
            visits=visits,
            total_duration_days=30
        )
        
        suggestions = rules_engine._identify_remote_opportunities(schedule)
        
        assert len(suggestions) > 0
        # Should suggest remote conversion
        remote_suggested = any(
            s.type == "remote_conversion" for s in suggestions
        )
        assert remote_suggested
    
    def test_optimize_timing(self, rules_engine):
        """Test visit timing optimization."""
        # Create visits without adequate windows
        visits = [
            Visit(
                id=str(uuid.uuid4()),
                name=f"Visit {i}",
                day=i * 7,
                window_days_before=0,
                window_days_after=0,
                assessments=[
                    Assessment(
                        name="Assessment",
                        type=AssessmentType.VITAL_SIGNS,
                        duration_minutes=10,
                        is_invasive=False,
                        equipment_needed=["equipment"],
                        staff_required=["nurse"],
                        cost_estimate=50,
                        patient_discomfort_level=1
                    )
                ]
            ) for i in range(1, 4)
        ]
        
        schedule = Schedule(
            id=str(uuid.uuid4()),
            protocol_name="Test Timing",
            protocol_version="1.0",
            therapeutic_area="Test",
            phase="2",
            visits=visits,
            total_duration_days=30
        )
        
        suggestions = rules_engine._optimize_timing(schedule)
        
        assert len(suggestions) > 0
        # Should suggest expanding visit windows
        window_suggested = any(
            "window" in s.description.lower() for s in suggestions
        )
        assert window_suggested
    
    def test_generate_optimization_summary(self, rules_engine, complex_schedule):
        """Test optimization summary generation."""
        optimized, suggestions, _ = rules_engine.optimize_schedule(complex_schedule)
        
        summary = rules_engine.generate_optimization_summary(
            complex_schedule,
            optimized,
            suggestions
        )
        
        assert isinstance(summary, dict)
        assert "visits_consolidated" in summary
        assert "assessments_eliminated" in summary
        assert "remote_conversions" in summary
        assert "burden_reduction_percentage" in summary
        assert "time_saved_hours" in summary
        assert summary["total_suggestions"] == len(suggestions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])