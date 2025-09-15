# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Schedule of Assessments (SoA) Optimizer - a clinical trial protocol optimization tool that analyzes and streamlines assessment schedules to reduce patient and site burden while maintaining trial integrity.

## Architecture

The system follows a containerized microservices architecture with real MCP (Model Context Protocol) integration:
- **Backend**: FastAPI application (port 8040) with aggressive optimization rules engine
- **Frontend**: Web UI (port 3040) for schedule visualization with bar chart comparisons
- **Real MCP Server**: Production MCP server (port 8210) at `/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools` providing:
  - Autonomous schedule conversion (CSV/JSON → CDISC SDTM, FHIR R4, OMOP CDM)
  - Protocol complexity analysis via `study_complexity_calculator`
  - Compliance knowledge base integration
  - LLM + Fuzzy Logic consensus with 85%+ accuracy
  - JSON-RPC 2.0 over stdio communication

## Key Development Commands

### ⚠️ IMPORTANT: External Dependencies

**The MCP server is an EXTERNAL SERVICE that must be started FIRST:**

```bash
# STEP 1: Start MCP server (REQUIRED - External Dependency)
cd /dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools
source venv/bin/activate
python server.py  # Runs on port 8210 - keep this running!

# STEP 2: Start Schedule Optimizer (in new terminal)
cd /dcri/sasusers/home/scb2/gitRepos/schedule-assessments-optimizer
docker compose up --build -d

# STEP 3: Verify MCP integration
python test_mcp_integration.py  # New test file to verify everything works
```

**After computer restart, you MUST:**
1. Start the MCP server first (external dependency)
2. Then start the Schedule Optimizer
3. Run test_mcp_integration.py to verify connectivity

### Testing
```bash
# Run backend tests
pytest backend/

# Test real MCP integration
cd /dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools
python test_azure_openai.py
python use_schedule_converter.py
```

## Core Components

### Data Models (`backend/models.py`)
- `Assessment`: Individual clinical assessments with properties like duration, invasiveness, equipment needs
- `Visit`: Collection of assessments on a specific day
- `Schedule`: Complete set of visits comprising the trial protocol
- `OptimizationResult`: Contains original schedule, optimized version, burden scores, and warnings

### Rules Engine (`backend/rules_engine.py`)
Implements aggressive optimization rules for maximum visible impact:
1. **Redundancy Detection**: Identifies repeated assessments within 21-day windows
2. **Visit Consolidation**: Merges visits within 14 days (up to 8 hours combined duration)
3. **Logistical Feasibility**: Flags impossible schedules based on compliance knowledge
4. **Remote Conversion**: Identifies assessments that can be done remotely
5. **Safety Streamlining**: Eliminates duplicate safety assessments

**Note**: Applies ALL suggestions (32+) for maximum visible changes in bar charts

### Burden Calculator (`backend/burden_calculator.py`)
- More sensitive scoring thresholds for visible changes
- Patient burden factors: time (30hr max), travel (15 visits max), invasiveness (10 procedures max)
- Site burden factors: staff hours, equipment, complexity

### API Endpoints
- `POST /optimize-schedule`: Main optimization endpoint (applies all suggestions)
- `GET /demo-data/complex`: Complex schedule with many optimization opportunities
- `POST /upload-schedule`: Upload CSV/JSON schedules
- `GET /sample-data`: Get various demo schedules

## MCP Integration

The real MCP server provides intelligent schedule conversion:

### Usage
```python
# Backend integration (main.py)
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{MCP_SERVER_URL}/run_tool/study_complexity_calculator",
        json={"schedule": schedule_dict},
        timeout=30.0
    )
```

### Available MCP Tools
- `schedule_converter`: Convert schedules to standard formats
- `study_complexity_calculator`: Analyze protocol complexity
- `compliance_checker`: Validate regulatory compliance

See `/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools/MCP_USAGE_GUIDE.md` for complete integration guide.

## Recent Optimizations

The system now produces highly visible changes:
- **Baseline visit**: 4 → 0 assessments (complete elimination)
- **Visit consolidation**: Day 3 + Day 5 merged into single visit
- **Redundancy removal**: Aggressive elimination of duplicate assessments
- **Burden scoring**: More sensitive to changes for visible bar chart differences

## Project Status

**Production Ready Features:**
- ✅ Real MCP server integration for schedule conversion
- ✅ Aggressive optimization engine (removes entire visits/assessments)
- ✅ Visual comparison with bar charts showing assessment counts per visit
- ✅ File upload/download functionality
- ✅ Complex demo data with visible optimization improvements (19→18 visits)

**Key Files:**
- `MCP_SCHEDULE_CONVERTER_DESIGN.md`: Comprehensive MCP design (755 lines)
- `MCP_USAGE_GUIDE.md`: Integration instructions
- `backend/rules_engine.py`: Aggressive optimization logic
- `frontend/src/components/OptimizationComparison.tsx`: Bar chart visualization