#!/usr/bin/env python3
"""Test script to verify optimization logic."""

import sys
import os
sys.path.append('/app/backend')

from models import Schedule, Visit, Assessment
from rules_engine import RulesEngine
from burden_calculator import BurdenCalculator
import json
from datetime import datetime

# Create a sample schedule with redundancies
def create_test_schedule():
    visits = []
    
    # Visit 1 - Screening (Day -14)
    visits.append(Visit(
        id="v1",
        name="Screening",
        day=-14,
        window_days_before=0,
        window_days_after=7,
        is_screening=True,
        assessments=[
            Assessment(
                id="a1",
                name="Physical Exam",
                type="physical_exam",
                duration_minutes=30
            ),
            Assessment(
                id="a2",
                name="Blood Draw",
                type="blood_draw",
                duration_minutes=15,
                is_fasting_required=True
            ),
            Assessment(
                id="a3",
                name="ECG",
                type="ecg",
                duration_minutes=15
            ),
            Assessment(
                id="a4",
                name="Urinalysis",
                type="urinalysis",
                duration_minutes=10
            )
        ]
    ))
    
    # Visit 2 - Baseline (Day 1)
    visits.append(Visit(
        id="v2",
        name="Baseline",
        day=1,
        window_days_before=0,
        window_days_after=0,
        is_baseline=True,
        assessments=[
            Assessment(
                id="a5",
                name="Physical Exam",
                type="physical_exam",
                duration_minutes=30
            ),
            Assessment(
                id="a6",
                name="Blood Draw",
                type="blood_draw",
                duration_minutes=15,
                is_fasting_required=True
            ),
            Assessment(
                id="a7",
                name="ECG",
                type="ecg",
                duration_minutes=15
            )
        ]
    ))
    
    # Visit 3 - Week 1 (Day 7) - Close to Visit 4
    visits.append(Visit(
        id="v3",
        name="Week 1",
        day=7,
        window_days_before=1,
        window_days_after=1,
        assessments=[
            Assessment(
                id="a8",
                name="Blood Draw",
                type="blood_draw",
                duration_minutes=15
            ),
            Assessment(
                id="a9",
                name="Vital Signs",
                type="vital_signs",
                duration_minutes=10,
                can_be_done_remotely=True
            )
        ]
    ))
    
    # Visit 4 - Day 10 - Close to Visit 3, could be consolidated
    visits.append(Visit(
        id="v4",
        name="Day 10",
        day=10,
        window_days_before=1,
        window_days_after=1,
        assessments=[
            Assessment(
                id="a10",
                name="ECG",
                type="ecg",
                duration_minutes=15
            ),
            Assessment(
                id="a11",
                name="Questionnaire",
                type="questionnaire",
                duration_minutes=20,
                can_be_done_remotely=True
            )
        ]
    ))
    
    # Visit 5 - Week 2 (Day 14) with redundant safety labs
    visits.append(Visit(
        id="v5",
        name="Week 2",
        day=14,
        window_days_before=2,
        window_days_after=2,
        assessments=[
            Assessment(
                id="a12",
                name="Blood Draw",
                type="blood_draw",
                duration_minutes=15
            ),
            Assessment(
                id="a13",
                name="Urinalysis",
                type="urinalysis",
                duration_minutes=10
            ),
            Assessment(
                id="a14",
                name="ECG",
                type="ecg",
                duration_minutes=15
            ),
            Assessment(
                id="a15",
                name="Physical Exam",
                type="physical_exam",
                duration_minutes=30
            )
        ]
    ))
    
    return Schedule(
        id="test-schedule",
        protocol_name="Test Protocol",
        protocol_version="1.0",
        therapeutic_area="Oncology",
        phase="2",
        total_duration_days=28,
        visits=visits
    )

def main():
    # Create test schedule
    original_schedule = create_test_schedule()
    print(f"Original schedule has {len(original_schedule.visits)} visits")
    print(f"Original visits: {[v.name for v in original_schedule.visits]}")
    
    # Apply optimization
    rules_engine = RulesEngine()
    optimized_schedule, suggestions, warnings = rules_engine.optimize_schedule(original_schedule)
    
    print(f"\nOptimized schedule has {len(optimized_schedule.visits)} visits")
    print(f"Optimized visits: {[v.name for v in optimized_schedule.visits]}")
    
    print(f"\nGenerated {len(suggestions)} suggestions:")
    for i, sugg in enumerate(suggestions[:5]):  # Show top 5 applied
        print(f"  {i+1}. {sugg.type}: {sugg.description}")
    
    print(f"\nGenerated {len(warnings)} warnings")
    
    # Calculate burden scores
    burden_calc = BurdenCalculator()
    original_burden = burden_calc.calculate_patient_burden(original_schedule)
    optimized_burden = burden_calc.calculate_patient_burden(optimized_schedule)
    
    print(f"\nOriginal burden score: {original_burden.total_score:.1f}")
    print(f"Optimized burden score: {optimized_burden.total_score:.1f}")
    
    # Compare specific details
    print("\n=== Detailed Comparison ===")
    for orig_visit in original_schedule.visits:
        opt_visit = next((v for v in optimized_schedule.visits if v.id == orig_visit.id), None)
        if opt_visit:
            if len(orig_visit.assessments) != len(opt_visit.assessments):
                print(f"{orig_visit.name}: {len(orig_visit.assessments)} -> {len(opt_visit.assessments)} assessments")
            if orig_visit.name != opt_visit.name:
                print(f"Name changed: {orig_visit.name} -> {opt_visit.name}")
        else:
            print(f"{orig_visit.name}: REMOVED")
    
    # Check for new visits
    for opt_visit in optimized_schedule.visits:
        if not any(v.id == opt_visit.id for v in original_schedule.visits):
            print(f"NEW VISIT: {opt_visit.name}")
    
    # Save results for inspection
    result = {
        "original": original_schedule.dict(),
        "optimized": optimized_schedule.dict(),
        "suggestions": [s.dict() for s in suggestions],
        "warnings": [w.dict() for w in warnings]
    }
    
    with open('/app/test_optimization_result.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("\nResults saved to test_optimization_result.json")
    
    # Check if schedules are identical
    if original_schedule.dict() == optimized_schedule.dict():
        print("\n⚠️ WARNING: Original and optimized schedules are IDENTICAL!")
        return 1
    else:
        print("\n✓ Schedules are different - optimization applied successfully")
        return 0

if __name__ == "__main__":
    sys.exit(main())