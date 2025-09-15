# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Schedule of Assessments (SoA) Optimizer - a clinical trial protocol optimization tool that analyzes and streamlines assessment schedules to reduce patient and site burden while maintaining trial integrity.

## Architecture

The system follows a containerized microservices architecture:
- **Backend**: FastAPI application (port 8080) with optimization rules engine
- **Frontend**: Web UI (port 3040) for schedule visualization and comparison
- **MCP Services**: Two mock services (`ProtocolComplexityAnalyzer` on port 8001 and `ComplianceKnowledgeBase` on port 8002) that integrate for additional analysis

## Key Development Commands

### Local Development
```bash
# Build and run all services
docker compose up --build -d

# Stop all services
docker compose down
```

### Testing
```bash
# Run backend tests
pytest backend/

# Run specific service tests
pytest services/mcp_ProtocolComplexityAnalyzer/
pytest services/mcp_ComplianceKnowledgeBase/
```

## Core Components

### Data Models (`backend/models.py`)
- `Assessment`: Individual clinical assessments with properties like duration, invasiveness, equipment needs
- `Visit`: Collection of assessments on a specific day
- `Schedule`: Complete set of visits comprising the trial protocol
- `OptimizationResult`: Contains original schedule, optimized version, burden scores, and warnings

### Rules Engine (`backend/rules_engine.py`)
Implements three main optimization rules:
1. **Redundancy Detection**: Identifies repeated assessments within short timeframes
2. **Visit Consolidation**: Suggests merging closely-scheduled visits with low burden
3. **Logistical Feasibility**: Flags impossible schedules based on compliance knowledge

### API Endpoint
- `POST /optimize-schedule`: Main endpoint that accepts a Schedule object and returns optimization suggestions

## Project Status

Currently in early development phase. The development checklist in `development_checklist.md` tracks implementation progress across 5 sprints covering foundation, backend engine, frontend UI, and integration phases.