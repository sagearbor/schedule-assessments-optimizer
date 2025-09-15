# Frontend MCP Integration Testing Guide

## How to Test MCP Integration from the Frontend

### 1. Access the Frontend
Open your browser and navigate to: http://localhost:3040

### 2. Test File Upload with MCP Conversion

#### Prepare a Test CSV File
Create a file called `test_schedule.csv` with this content:

```csv
Visit,Day,Procedure,Duration
Screening,-14,Informed Consent,30
Screening,-14,Vital Signs,10
Screening,-14,Blood Draw,15
Baseline,0,Physical Exam,30
Baseline,0,ECG,20
Baseline,0,Blood Draw,15
Baseline,0,Questionnaire,20
Week 1,7,Vital Signs,10
Week 1,7,Blood Draw,15
Week 2,14,Vital Signs,10
Week 2,14,ECG,20
Week 2,14,Blood Draw,15
```

#### Upload and Monitor
1. Click "Upload Schedule" in the frontend
2. Drag and drop or select the CSV file
3. Open browser Developer Tools (F12)
4. Go to Network tab
5. Look for requests to:
   - `/upload-schedule` (file upload)
   - `/optimize-schedule` (optimization with MCP)

### 3. Monitor MCP Server Logs

Open a new terminal and watch the MCP server logs:

```bash
# In the MCP tools directory
cd /dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools
# Find the server process and check its output
```

### 4. Check Backend Logs for MCP Calls

```bash
docker compose logs -f backend | grep -E "MCP|study_complexity|schedule_converter"
```

### 5. Test Complex Demo with Full MCP Analysis

1. In the frontend, click "Load Demo Data"
2. Select "Complex Unoptimized"
3. Click "Optimize Schedule"
4. Watch for:
   - Bar charts showing assessment count changes
   - Visit consolidation (Day 3 + Day 5)
   - Baseline elimination (4→0 assessments)

### 6. Verify MCP Features in Browser Console

Open browser console (F12) and run:

```javascript
// Check if optimization results include MCP analysis
fetch('http://localhost:8040/demo-data/complex')
  .then(r => r.json())
  .then(schedule => {
    return fetch('http://localhost:8040/optimize-schedule', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(schedule)
    })
  })
  .then(r => r.json())
  .then(result => {
    console.log('MCP Analysis Present:', {
      hasComplexityScore: !!result.complexity_score,
      hasComplianceWarnings: !!result.warnings,
      suggestionCount: result.suggestions?.length,
      visitReduction: result.original_schedule.visits.length - result.optimized_schedule.visits.length
    });
    return result;
  });
```

## Expected Results

### ✅ MCP is Working If You See:

1. **In Network Tab:**
   - POST requests to `localhost:8210/run_tool/study_complexity_calculator`
   - POST requests to `localhost:8210/run_tool/schedule_converter`
   - Response times of 3-5 seconds (LLM processing)

2. **In Console:**
   - Complexity scores from MCP
   - Compliance warnings
   - 32+ optimization suggestions

3. **In UI:**
   - Bar charts showing dramatic changes:
     - Baseline: 4→0 assessments
     - Visit consolidation visible
   - Burden score improvements
   - Detailed suggestions list

### ❌ MCP is NOT Working If:

1. Optimization is instant (<1 second)
2. No requests to port 8210
3. Generic suggestions only
4. No complexity scoring

## Debug Commands

```bash
# Check if MCP server is receiving requests
curl http://localhost:8210/health

# Test MCP directly
curl -X POST http://localhost:8210/run_tool/study_complexity_calculator \
  -H "Content-Type: application/json" \
  -d '{"schedule": {"visits": [{"name": "Test", "day": 1, "assessments": []}]}}'

# Check if backend is calling MCP
docker compose logs backend | grep "8210"
```

## Understanding LLM Consensus

The MCP server uses two-phase validation:

1. **First Pass**: Regex/pattern matching (80% accuracy)
2. **LLM Check**: Azure OpenAI validates if configured
3. **Arbitration**: If disagreement >20%, a third LLM acts as judge

To see this in action, check MCP server logs while uploading a file:
- Look for "Pattern match confidence: X%"
- Look for "LLM validation: Y%"
- Look for "Arbitration needed" if they disagree