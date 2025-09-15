#!/bin/bash

# Setup script for running SoA Optimizer without Docker

echo "🚀 Setting up SoA Optimizer..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "✓ Python version: $python_version"

# Create virtual environment for backend
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

# Initialize database
python3 -c "from database import init_db; init_db()"
echo "✓ Database initialized"

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

# Check if npm is installed
if command -v npm &> /dev/null; then
    echo "✓ npm found, installing dependencies..."
    npm install
    echo "✓ Frontend dependencies installed"
else
    echo "⚠️  npm not found. Please install Node.js and npm to run the frontend."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Start the backend (Terminal 1):"
echo "   cd backend && source venv/bin/activate && python main.py"
echo ""
echo "2. Start MCP services (Terminal 2 & 3):"
echo "   cd services/mcp_ProtocolComplexityAnalyzer && python main.py"
echo "   cd services/mcp_ComplianceKnowledgeBase && python main.py"
echo ""
if command -v npm &> /dev/null; then
    echo "3. Start the frontend (Terminal 4):"
    echo "   cd frontend && npm start"
else
    echo "3. Install Node.js and npm, then run:"
    echo "   cd frontend && npm install && npm start"
fi
echo ""
echo "Access the application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8080"