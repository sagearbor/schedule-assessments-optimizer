#!/usr/bin/env python3
"""
Integration with Schedule Converter MCP Server
For use in the schedule-assessments-optimizer project
"""

import json
import subprocess
import sys
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class MCPScheduleConverter:
    """
    Client for the Schedule Converter MCP Server in dcri-mcp-tools
    """

    def __init__(self):
        """Initialize connection to the MCP server in the adjacent repository"""
        # Path to the MCP server in the dcri-mcp-tools repo
        self.mcp_tools_path = Path("/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools")
        self.server_script = self.mcp_tools_path / "scripts" / "schedule_converter_mcp.py"

        if not self.server_script.exists():
            raise FileNotFoundError(f"MCP server not found at {self.server_script}")

        self.process = None
        self.initialized = False
        self.msg_id = 0

    def start(self) -> bool:
        """Start the MCP server subprocess"""
        print(f"Starting MCP server from {self.server_script}...")

        # Start the server process
        self.process = subprocess.Popen(
            [sys.executable, str(self.server_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(self.mcp_tools_path)  # Run in the MCP tools directory
        )

        # Initialize the connection
        response = self._send_request("initialize", {
            "clientInfo": {
                "name": "schedule-optimizer",
                "version": "1.0.0"
            }
        })

        if response and "result" in response:
            # Send initialized notification
            self._send_notification("initialized", {})
            self.initialized = True
            print("✅ MCP server initialized successfully")

            # Print server info
            server_info = response["result"].get("serverInfo", {})
            print(f"   Server: {server_info.get('name')} v{server_info.get('version')}")
            return True

        print("❌ Failed to initialize MCP server")
        return False

    def stop(self):
        """Stop the MCP server"""
        if self.process:
            print("Stopping MCP server...")
            self._send_request("shutdown", {})
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            self.initialized = False
            print("✅ MCP server stopped")

    def _send_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Send a JSON-RPC request and get response"""
        if not self.process:
            return None

        self.msg_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": method,
            "params": params
        }

        # Send with Content-Length header
        json_str = json.dumps(request)
        content_length = len(json_str.encode('utf-8'))

        try:
            self.process.stdin.write(f"Content-Length: {content_length}\r\n\r\n")
            self.process.stdin.write(json_str)
            self.process.stdin.flush()

            # Read response
            header = self.process.stdout.readline()
            if header.startswith("Content-Length:"):
                self.process.stdout.readline()  # Empty line
                content_length = int(header.split(":")[1].strip())
                response_str = self.process.stdout.read(content_length)
                return json.loads(response_str)
        except Exception as e:
            print(f"Error communicating with MCP server: {e}")

        return None

    def _send_notification(self, method: str, params: Dict[str, Any]):
        """Send a JSON-RPC notification (no response expected)"""
        if not self.process:
            return

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

        json_str = json.dumps(request)
        content_length = len(json_str.encode('utf-8'))

        self.process.stdin.write(f"Content-Length: {content_length}\r\n\r\n")
        self.process.stdin.write(json_str)
        self.process.stdin.flush()

    def convert_schedule(self,
                        file_content: str = None,
                        file_path: str = None,
                        file_type: str = "csv",
                        target_format: str = "CDISC_SDTM",
                        organization_id: str = None) -> Dict[str, Any]:
        """
        Convert a clinical trial schedule to standard format

        Args:
            file_content: Direct content string (if provided)
            file_path: Path to file to read (if content not provided)
            file_type: Type of file (csv, json, text)
            target_format: Target format (CDISC_SDTM, FHIR_R4, OMOP_CDM)
            organization_id: Optional org ID for caching

        Returns:
            Conversion result dictionary with:
            - success: bool
            - data: converted data
            - confidence: conversion confidence percentage
            - llm_mode: whether Azure OpenAI or fallback was used
        """
        # Read file if path provided
        if file_path and not file_content:
            with open(file_path, 'r') as f:
                file_content = f.read()

        if not file_content:
            return {"error": "No content or file path provided"}

        if not self.initialized:
            if not self.start():
                return {"error": "Failed to start MCP server"}

        response = self._send_request("tools/call", {
            "name": "convert_schedule",
            "arguments": {
                "file_content": file_content,
                "file_type": file_type,
                "target_format": target_format,
                "organization_id": organization_id,
                "confidence_threshold": 85
            }
        })

        if response and "result" in response:
            # Extract the result from the MCP response
            content = response["result"]["content"][0]["text"]
            return json.loads(content)

        return {"error": "Failed to get response from MCP server"}

    def optimize_schedule(self, schedule_data: Dict) -> Dict[str, Any]:
        """
        Optimize a schedule after conversion
        This is a placeholder for integration with your optimizer logic

        Args:
            schedule_data: Converted schedule data (e.g., CDISC SDTM format)

        Returns:
            Optimized schedule
        """
        # TODO: Integrate with your existing optimization logic
        # For now, just return the data
        return {
            "optimized": True,
            "original": schedule_data,
            "recommendations": [
                "Consider consolidating visits on Day 7 and Day 8",
                "Lab assessments could be batched to reduce patient burden"
            ]
        }


# Context manager for automatic cleanup
class MCPScheduleConverterContext:
    """Context manager for the MCP converter"""

    def __init__(self):
        self.converter = MCPScheduleConverter()

    def __enter__(self):
        self.converter.start()
        return self.converter

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.converter.stop()


def convert_and_optimize_schedule(file_path: str,
                                 organization: str = "DCRI") -> Dict[str, Any]:
    """
    Main function to convert and optimize a clinical trial schedule

    Args:
        file_path: Path to the schedule file
        organization: Organization name for caching

    Returns:
        Dictionary with converted and optimized schedule
    """
    # Use context manager for automatic cleanup
    with MCPScheduleConverterContext() as converter:
        # Step 1: Convert to CDISC SDTM
        print(f"\nConverting {file_path} to CDISC SDTM...")
        result = converter.convert_schedule(
            file_path=file_path,
            file_type="csv",
            target_format="CDISC_SDTM",
            organization_id=organization
        )

        if not result.get("success"):
            print(f"❌ Conversion failed: {result.get('error')}")
            return result

        print(f"✅ Conversion successful!")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   LLM Mode: {result.get('llm_mode')}")
        print(f"   Rows processed: {result.get('row_count')}")

        # Step 2: Optimize the schedule
        print("\nOptimizing schedule...")
        optimized = converter.optimize_schedule(result['data'])

        # Step 3: Also convert to FHIR for interoperability
        print("\nConverting to FHIR R4 for interoperability...")
        fhir_result = converter.convert_schedule(
            file_path=file_path,
            file_type="csv",
            target_format="FHIR_R4",
            organization_id=organization
        )

        return {
            "success": True,
            "cdisc_sdtm": result['data'],
            "fhir": fhir_result.get('data') if fhir_result.get('success') else None,
            "optimization": optimized,
            "confidence": result.get('confidence'),
            "metadata": {
                "organization": organization,
                "llm_mode": result.get('llm_mode'),
                "arbitration_used": result.get('arbitration_used', False)
            }
        }


# Example usage specifically for schedule-assessments-optimizer
def example_integration():
    """
    Example of how to use this in the schedule-assessments-optimizer project
    """
    print("="*60)
    print("Schedule Assessments Optimizer - MCP Integration")
    print("="*60)

    # Create a sample schedule file
    sample_schedule = """Visit Name,Study Day,Assessments,Window
Screening,-14,Informed Consent|Medical History,-7 to 0
Baseline,0,Vital Signs|ECG|Labs|Physical Exam,-3 to 3
Week 1,7,Vital Signs|Drug Administration,5 to 9
Week 2,14,Vital Signs|Labs|Safety Assessment,12 to 16
Week 4,28,Vital Signs|ECG|Labs|Efficacy Assessment,25 to 31
Week 8,56,Vital Signs|Labs|Physical Exam,53 to 59
End of Study,84,Vital Signs|ECG|Labs|Final Assessment,81 to 87"""

    # Save to a temp file
    temp_file = "/tmp/sample_schedule.csv"
    with open(temp_file, 'w') as f:
        f.write(sample_schedule)

    # Convert and optimize
    result = convert_and_optimize_schedule(temp_file, "DCRI")

    if result.get("success"):
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)

        # Show CDISC SDTM conversion
        print("\n📊 CDISC SDTM Format:")
        tv_records = result['cdisc_sdtm'].get('TV', [])
        print(f"   Trial Visits (TV): {len(tv_records)} records")
        for tv in tv_records[:3]:  # Show first 3
            print(f"   - Visit {tv['VISITNUM']}: {tv['VISIT']} (Day {tv['VISITDY']})")

        # Show FHIR conversion
        if result.get('fhir'):
            print("\n🏥 FHIR R4 Format:")
            activities = result['fhir'].get('activity', [])
            print(f"   Care Plan Activities: {len(activities)}")

        # Show optimization recommendations
        print("\n🚀 Optimization Recommendations:")
        for rec in result['optimization']['recommendations']:
            print(f"   - {rec}")

        # Save results
        output_file = "/tmp/converted_schedule.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full results saved to: {output_file}")

    print("\n" + "="*60)
    print("Integration complete!")
    print("="*60)


if __name__ == "__main__":
    # Run the example
    example_integration()