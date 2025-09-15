#!/usr/bin/env python3
"""
MCP Server for Protocol Complexity Analyzer
Analyzes clinical trial protocol complexity and provides optimization recommendations
"""

import sys
import os
import json
from typing import Dict, Any, List

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, '/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools')

from mcp_server import MCPServer


class ComplexityAnalyzer:
    """Analyzes protocol complexity based on various factors"""

    @staticmethod
    def calculate_complexity_score(params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall complexity score for a protocol"""

        # Extract parameters
        num_visits = params.get('num_visits', 0)
        num_procedures = params.get('num_procedures', 0)
        duration_days = params.get('duration_days', 0)
        phase = params.get('phase', '2')
        num_sites = params.get('num_sites', 1)

        # Calculate base complexity score
        visit_complexity = min(num_visits * 2, 30)  # Max 30 points
        procedure_complexity = min(num_procedures * 0.5, 25)  # Max 25 points
        duration_complexity = min(duration_days / 30, 20)  # Max 20 points

        # Phase multiplier
        phase_multipliers = {
            '1': 1.5,  # Phase 1 is most complex
            '2': 1.2,
            '3': 1.0,
            '4': 0.8   # Phase 4 is least complex
        }
        phase_multiplier = phase_multipliers.get(str(phase), 1.0)

        # Site complexity
        site_complexity = min(num_sites * 0.1, 10)  # Max 10 points

        # Calculate total score
        base_score = visit_complexity + procedure_complexity + duration_complexity + site_complexity
        total_score = min(base_score * phase_multiplier, 100)

        # Determine complexity level
        if total_score < 30:
            complexity_level = "Low"
            recommendations = [
                "Protocol has low complexity, suitable for most sites",
                "Consider bundling with other studies if capacity allows"
            ]
        elif total_score < 60:
            complexity_level = "Moderate"
            recommendations = [
                "Protocol has moderate complexity",
                "Ensure adequate site training and support",
                "Consider simplifying procedures where possible"
            ]
        elif total_score < 80:
            complexity_level = "High"
            recommendations = [
                "Protocol has high complexity",
                "Recommend experienced sites only",
                "Consider protocol simplification",
                "Implement robust monitoring plan"
            ]
        else:
            complexity_level = "Very High"
            recommendations = [
                "Protocol has very high complexity",
                "Strong recommendation to simplify protocol",
                "Consider splitting into multiple studies",
                "Requires specialized sites with extensive experience"
            ]

        return {
            "complexity_score": round(total_score, 2),
            "complexity_level": complexity_level,
            "breakdown": {
                "visit_complexity": round(visit_complexity, 2),
                "procedure_complexity": round(procedure_complexity, 2),
                "duration_complexity": round(duration_complexity, 2),
                "site_complexity": round(site_complexity, 2),
                "phase_multiplier": phase_multiplier
            },
            "recommendations": recommendations
        }

    @staticmethod
    def analyze_visit_burden(params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze burden of individual visits"""

        visits = params.get('visits', [])

        if not visits:
            return {
                "total_visits": 0,
                "high_burden_visits": [],
                "recommendations": ["No visit data provided"]
            }

        high_burden_visits = []
        total_burden = 0

        for visit in visits:
            # Calculate visit burden
            num_assessments = len(visit.get('assessments', []))
            visit_duration = sum(a.get('duration_minutes', 30) for a in visit.get('assessments', []))

            burden_score = num_assessments * 10 + visit_duration / 60 * 5
            total_burden += burden_score

            if burden_score > 50:
                high_burden_visits.append({
                    "visit_name": visit.get('name', 'Unknown'),
                    "day": visit.get('day', 0),
                    "burden_score": round(burden_score, 2),
                    "num_assessments": num_assessments,
                    "duration_hours": round(visit_duration / 60, 1)
                })

        avg_burden = total_burden / len(visits) if visits else 0

        recommendations = []
        if high_burden_visits:
            recommendations.append(f"Found {len(high_burden_visits)} high-burden visits that should be reviewed")
        if avg_burden > 40:
            recommendations.append("Consider splitting high-burden visits into multiple sessions")
        if len(visits) > 20:
            recommendations.append("High number of visits may impact retention")

        return {
            "total_visits": len(visits),
            "average_burden_score": round(avg_burden, 2),
            "high_burden_visits": high_burden_visits,
            "recommendations": recommendations
        }

    @staticmethod
    def get_complexity_metrics(params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed complexity metrics"""

        protocol_name = params.get('protocol_name', 'Unknown')

        # Generate sample metrics (in production, these would be calculated from actual data)
        metrics = {
            "protocol_name": protocol_name,
            "complexity_dimensions": {
                "operational": {
                    "score": 65,
                    "factors": [
                        "Multi-site coordination required",
                        "Complex randomization scheme",
                        "Specialized equipment needed"
                    ]
                },
                "clinical": {
                    "score": 72,
                    "factors": [
                        "Invasive procedures",
                        "Frequent safety monitoring",
                        "Complex inclusion/exclusion criteria"
                    ]
                },
                "regulatory": {
                    "score": 45,
                    "factors": [
                        "Standard regulatory requirements",
                        "No special populations"
                    ]
                },
                "data_management": {
                    "score": 58,
                    "factors": [
                        "Electronic data capture required",
                        "Real-time data monitoring",
                        "Complex derived variables"
                    ]
                }
            },
            "risk_assessment": {
                "enrollment_risk": "Moderate",
                "retention_risk": "High",
                "data_quality_risk": "Low",
                "timeline_risk": "Moderate"
            },
            "optimization_opportunities": [
                "Combine screening and baseline visits",
                "Implement remote monitoring for safety assessments",
                "Simplify inclusion criteria where possible",
                "Use central labs to reduce site burden"
            ]
        }

        return metrics


def create_complexity_analyzer_server():
    """Create MCP server for Protocol Complexity Analyzer"""

    server = MCPServer(name="protocol-complexity-analyzer", version="1.0.0")
    analyzer = ComplexityAnalyzer()

    # Register analyze-complexity tool
    server.register_tool(
        name="analyze-complexity",
        description="Analyze protocol complexity and provide recommendations",
        input_schema={
            "type": "object",
            "properties": {
                "protocol_name": {
                    "type": "string",
                    "description": "Name of the protocol"
                },
                "phase": {
                    "type": "string",
                    "description": "Clinical trial phase (1, 2, 3, or 4)"
                },
                "num_visits": {
                    "type": "integer",
                    "description": "Number of visits in the protocol"
                },
                "num_procedures": {
                    "type": "integer",
                    "description": "Total number of procedures across all visits"
                },
                "duration_days": {
                    "type": "integer",
                    "description": "Total duration of the trial in days"
                },
                "num_sites": {
                    "type": "integer",
                    "description": "Number of sites (optional)",
                    "default": 1
                }
            },
            "required": ["num_visits", "num_procedures", "duration_days"]
        },
        handler=lambda args: analyzer.calculate_complexity_score(args)
    )

    # Register analyze-visit-burden tool
    server.register_tool(
        name="analyze-visit-burden",
        description="Analyze the burden of individual visits",
        input_schema={
            "type": "object",
            "properties": {
                "visits": {
                    "type": "array",
                    "description": "Array of visit objects",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "day": {"type": "integer"},
                            "assessments": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "duration_minutes": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "required": ["visits"]
        },
        handler=lambda args: analyzer.analyze_visit_burden(args)
    )

    # Register get-complexity-metrics tool
    server.register_tool(
        name="get-complexity-metrics",
        description="Get detailed complexity metrics for a protocol",
        input_schema={
            "type": "object",
            "properties": {
                "protocol_name": {
                    "type": "string",
                    "description": "Name of the protocol"
                }
            },
            "required": ["protocol_name"]
        },
        handler=lambda args: analyzer.get_complexity_metrics(args)
    )

    # Register resources
    server.register_resource(
        uri="complexity://guidelines",
        name="Complexity Assessment Guidelines",
        description="Guidelines for assessing protocol complexity",
        mime_type="text/plain"
    )

    server.register_resource(
        uri="complexity://benchmarks",
        name="Industry Benchmarks",
        description="Industry benchmarks for protocol complexity by phase and indication",
        mime_type="application/json"
    )

    return server


if __name__ == "__main__":
    # Create and run the server
    server = create_complexity_analyzer_server()
    server.run()