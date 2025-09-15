#!/usr/bin/env python3
"""
Test script to verify MCP server integration with Schedule Optimizer.

This script tests:
1. MCP server connectivity
2. Schedule conversion functionality
3. Complexity analysis
4. Integration with the optimizer backend

Usage:
    python test_mcp_integration.py
"""

import sys
import json
import httpx
import asyncio
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

MCP_SERVER_URL = "http://localhost:8210"
BACKEND_URL = "http://localhost:8040"

def print_status(message: str, status: str = "info"):
    """Print colored status messages."""
    if status == "success":
        print(f"{GREEN}✓{RESET} {message}")
    elif status == "error":
        print(f"{RED}✗{RESET} {message}")
    elif status == "warning":
        print(f"{YELLOW}⚠{RESET} {message}")
    else:
        print(f"{BLUE}ℹ{RESET} {message}")

async def test_mcp_server_health():
    """Test if MCP server is running and healthy."""
    print("\n" + "="*60)
    print("Testing MCP Server Connectivity")
    print("="*60)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_SERVER_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print_status(f"MCP server is running at {MCP_SERVER_URL}", "success")
                return True
            else:
                print_status(f"MCP server returned status {response.status_code}", "warning")
                return False
    except httpx.ConnectError:
        print_status(f"Cannot connect to MCP server at {MCP_SERVER_URL}", "error")
        print_status("Please start the MCP server first:", "warning")
        print("  cd /dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools")
        print("  source venv/bin/activate")
        print("  python server.py")
        return False
    except Exception as e:
        print_status(f"Error testing MCP server: {e}", "error")
        return False

async def test_schedule_conversion():
    """Test schedule conversion functionality."""
    print("\n" + "="*60)
    print("Testing Schedule Conversion")
    print("="*60)

    # Sample schedule data
    test_schedule = {
        "file_content": """Visit,Day,Assessments
Screening,-14,"Informed Consent, Vital Signs, Blood Draw"
Baseline,0,"Physical Exam, ECG, Blood Draw, Questionnaire"
Week 1,7,"Vital Signs, Blood Draw"
Week 2,14,"Vital Signs, ECG, Blood Draw"
Week 4,28,"Physical Exam, Blood Draw, Questionnaire"
End of Study,56,"Physical Exam, Vital Signs, Blood Draw"
""",
        "file_type": "csv",
        "target_format": "CDISC_SDTM"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/run_tool/schedule_converter",
                json=test_schedule,
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print_status("Schedule conversion successful", "success")
                    print_status(f"Confidence: {result.get('confidence', 'N/A')}%", "info")
                    print_status(f"Output format: {result.get('format', 'N/A')}", "info")

                    # Show sample of converted data
                    if 'data' in result and result['data']:
                        print("\nSample converted data (first domain):")
                        first_key = list(result['data'].keys())[0]
                        print(f"  Domain: {first_key}")
                        print(f"  Records: {len(result['data'][first_key])}")
                    return True
                else:
                    print_status(f"Conversion failed: {result.get('error', 'Unknown error')}", "error")
                    return False
            else:
                print_status(f"MCP server returned status {response.status_code}", "error")
                return False

    except httpx.ConnectError:
        print_status("Cannot connect to MCP server", "error")
        return False
    except Exception as e:
        print_status(f"Error during conversion: {e}", "error")
        return False

async def test_complexity_analysis():
    """Test protocol complexity analysis."""
    print("\n" + "="*60)
    print("Testing Protocol Complexity Analysis")
    print("="*60)

    # Test schedule for complexity analysis
    test_data = {
        "schedule": {
            "protocol_name": "Test Protocol",
            "visits": [
                {
                    "name": "Screening",
                    "day": -14,
                    "assessments": [
                        {"name": "Informed Consent", "duration_minutes": 30},
                        {"name": "Vital Signs", "duration_minutes": 10},
                        {"name": "Blood Draw", "duration_minutes": 15}
                    ]
                },
                {
                    "name": "Baseline",
                    "day": 0,
                    "assessments": [
                        {"name": "Physical Exam", "duration_minutes": 30},
                        {"name": "ECG", "duration_minutes": 20},
                        {"name": "Blood Draw", "duration_minutes": 15}
                    ]
                }
            ]
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/run_tool/study_complexity_calculator",
                json=test_data,
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                print_status("Complexity analysis successful", "success")

                # Display results
                if 'complexity_score' in result:
                    print_status(f"Complexity Score: {result['complexity_score']}", "info")
                if 'category' in result:
                    print_status(f"Category: {result['category']}", "info")
                if 'factors' in result:
                    print("\nComplexity Factors:")
                    for factor, value in result['factors'].items():
                        print(f"  - {factor}: {value}")

                return True
            else:
                print_status(f"Analysis failed with status {response.status_code}", "error")
                return False

    except httpx.ConnectError:
        print_status("Cannot connect to MCP server", "error")
        return False
    except Exception as e:
        print_status(f"Error during analysis: {e}", "error")
        return False

async def test_backend_integration():
    """Test if backend can communicate with MCP server."""
    print("\n" + "="*60)
    print("Testing Backend Integration with MCP")
    print("="*60)

    try:
        # First check if backend is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
                if response.status_code == 200:
                    print_status(f"Backend is running at {BACKEND_URL}", "success")
                else:
                    print_status(f"Backend returned status {response.status_code}", "warning")
            except:
                print_status(f"Backend is not running at {BACKEND_URL}", "warning")
                print_status("Start it with: docker compose up -d", "info")
                return False

            # Test optimization with MCP integration
            print_status("Testing optimization with MCP integration...", "info")

            # Get complex demo data
            response = await client.get(f"{BACKEND_URL}/demo-data/complex", timeout=10.0)
            if response.status_code != 200:
                print_status("Cannot get demo data from backend", "error")
                return False

            demo_schedule = response.json()

            # Run optimization (which should call MCP server)
            response = await client.post(
                f"{BACKEND_URL}/optimize-schedule",
                json=demo_schedule,
                timeout=60.0
            )

            if response.status_code == 200:
                result = response.json()
                print_status("Optimization with MCP successful", "success")

                # Show optimization results
                orig_visits = len(result['original_schedule']['visits'])
                opt_visits = len(result['optimized_schedule']['visits'])

                print_status(f"Original visits: {orig_visits}", "info")
                print_status(f"Optimized visits: {opt_visits}", "info")
                print_status(f"Improvement: {result['improvement_percentage']:.2f}%", "info")
                print_status(f"Suggestions: {len(result['suggestions'])}", "info")

                return True
            else:
                print_status(f"Optimization failed with status {response.status_code}", "error")
                return False

    except Exception as e:
        print_status(f"Error during backend integration test: {e}", "error")
        return False

async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MCP Integration Test Suite")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Test MCP server health
    mcp_healthy = await test_mcp_server_health()
    results.append(("MCP Server Health", mcp_healthy))

    if mcp_healthy:
        # Only run other tests if MCP server is healthy
        results.append(("Schedule Conversion", await test_schedule_conversion()))
        results.append(("Complexity Analysis", await test_complexity_analysis()))
        results.append(("Backend Integration", await test_backend_integration()))
    else:
        print_status("\nSkipping other tests since MCP server is not available", "warning")

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "success" if result else "error"
        print_status(f"{test_name}: {'PASSED' if result else 'FAILED'}", status)

    print("\n" + "-"*60)
    if passed == total:
        print_status(f"All {total} tests PASSED!", "success")
    else:
        print_status(f"{passed}/{total} tests passed", "warning" if passed > 0 else "error")

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)