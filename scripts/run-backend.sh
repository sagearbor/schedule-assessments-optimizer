#!/bin/bash

# Script to run the backend without Docker

echo "🚀 Starting SoA Optimizer Backend..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Initialize database if it doesn't exist
if [ ! -f "soa_optimizer.db" ]; then
    echo "🗄️ Initializing database..."
    python3 -c "from database import init_db; init_db()"
fi

# Start the backend server
echo "✅ Starting backend server on http://localhost:8080"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload