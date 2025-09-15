#!/bin/bash

# Script to run all services without Docker
# This script runs all services in the background and provides a simple management interface

echo "🚀 Starting SoA Optimizer Application (Non-Docker Mode)"
echo "=================================================="

# Store PIDs
PIDS=()

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    for pid in "${PIDS[@]}"; do
        kill $pid 2>/dev/null
    done
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Start MCP Service 1
echo "📡 Starting Protocol Complexity Analyzer..."
cd services/mcp_ProtocolComplexityAnalyzer
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/mcp1.log 2>&1 &
PIDS+=($!)
cd ../..
echo "   ✓ Running on http://localhost:8001"

# Start MCP Service 2
echo "📡 Starting Compliance Knowledge Base..."
cd services/mcp_ComplianceKnowledgeBase
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi
python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 > /tmp/mcp2.log 2>&1 &
PIDS+=($!)
cd ../..
echo "   ✓ Running on http://localhost:8002"

# Start Backend
echo "🔧 Starting Backend API..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

# Initialize database if needed
if [ ! -f "soa_optimizer.db" ]; then
    python3 -c "from database import init_db; init_db()" 2>/dev/null
fi

python3 -m uvicorn main:app --host 0.0.0.0 --port 8080 > /tmp/backend.log 2>&1 &
PIDS+=($!)
cd ..
echo "   ✓ Running on http://localhost:8080"

# Check if npm is available for frontend
if command -v npm &> /dev/null; then
    echo "🎨 Starting Frontend..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "   Installing dependencies (this may take a minute)..."
        npm install --silent 2>/dev/null
    fi
    npm start > /tmp/frontend.log 2>&1 &
    PIDS+=($!)
    cd ..
    echo "   ✓ Running on http://localhost:3000"
else
    echo "⚠️  npm not found - Frontend will not be started"
    echo "   Install Node.js and npm to run the frontend"
fi

echo ""
echo "=================================================="
echo "✅ All services are running!"
echo ""
echo "Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8080"
echo "   API Docs: http://localhost:8080/docs"
echo ""
echo "View logs:"
echo "   Backend: tail -f /tmp/backend.log"
echo "   MCP1: tail -f /tmp/mcp1.log"
echo "   MCP2: tail -f /tmp/mcp2.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================================="

# Wait indefinitely
while true; do
    sleep 1
done