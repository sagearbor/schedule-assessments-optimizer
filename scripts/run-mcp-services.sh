#!/bin/bash

# Script to run MCP services without Docker

echo "🚀 Starting MCP Services..."

# Function to run a service in background
run_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    
    echo "Starting $service_name on port $port..."
    cd $service_dir
    
    # Create virtual environment if needed
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start the service
    python3 -m uvicorn main:app --host 0.0.0.0 --port $port &
    echo "✓ $service_name started (PID: $!)"
}

# Start both MCP services
run_service "Protocol Complexity Analyzer" "services/mcp_ProtocolComplexityAnalyzer" 8001
run_service "Compliance Knowledge Base" "services/mcp_ComplianceKnowledgeBase" 8002

echo ""
echo "✅ MCP Services are running!"
echo "   Protocol Complexity Analyzer: http://localhost:8001"
echo "   Compliance Knowledge Base: http://localhost:8002"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
wait