#!/bin/bash

# Simplified script to run all services without virtual environments
# Uses system Python with --user flag for dependencies

echo "🚀 Starting SoA Optimizer Application (Simple Mode)"
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

# Check and install Python dependencies if needed
echo "📦 Checking Python dependencies..."
pip3 install --user --quiet fastapi uvicorn pydantic sqlalchemy python-jose passlib python-multipart httpx 2>/dev/null

# Start MCP Service 1
echo "📡 Starting Protocol Complexity Analyzer..."
cd services/mcp_ProtocolComplexityAnalyzer
python3 main.py > /tmp/mcp1.log 2>&1 &
PIDS+=($!)
cd ../..
sleep 2
echo "   ✓ Running on http://localhost:8001"

# Start MCP Service 2
echo "📡 Starting Compliance Knowledge Base..."
cd services/mcp_ComplianceKnowledgeBase
python3 main.py > /tmp/mcp2.log 2>&1 &
PIDS+=($!)
cd ../..
sleep 2
echo "   ✓ Running on http://localhost:8002"

# Start Backend
echo "🔧 Starting Backend API..."
cd backend

# Initialize database if needed
if [ ! -f "soa_optimizer.db" ]; then
    echo "   Initializing database..."
    python3 -c "from database import init_db; init_db()" 2>/dev/null
fi

python3 main.py > /tmp/backend.log 2>&1 &
PIDS+=($!)
cd ..
sleep 3
echo "   ✓ Running on http://localhost:8080"

# Check if npm is available for frontend
if command -v npm &> /dev/null; then
    echo "🎨 Starting Frontend..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "   Installing dependencies (this may take a minute)..."
        npm install --silent 2>/dev/null
    fi
    
    # Export the API URL for the frontend
    export REACT_APP_API_URL=http://localhost:8080
    
    npm start > /tmp/frontend.log 2>&1 &
    PIDS+=($!)
    cd ..
    sleep 5
    echo "   ✓ Running on http://localhost:3000"
else
    echo "⚠️  npm not found - Frontend will not be started"
    echo "   Install Node.js and npm to run the frontend"
fi

echo ""
echo "=================================================="
echo "✅ Application is starting up!"
echo ""
echo "Checking service status..."

# Check if services are actually running
sleep 3
for port in 8001 8002 8080; do
    if nc -z localhost $port 2>/dev/null; then
        echo "   ✓ Port $port is responding"
    else
        echo "   ⚠️  Port $port is not responding - check logs"
    fi
done

echo ""
echo "Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8080"
echo "   API Docs: http://localhost:8080/docs"
echo ""
echo "View logs if services fail to start:"
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