#!/bin/bash

echo "🔧 Installing all dependencies for SoA Optimizer"
echo "================================================"

# Install Python dependencies
echo ""
echo "📦 Installing Python packages..."
pip3 install --user \
    fastapi \
    uvicorn[standard] \
    pydantic \
    sqlalchemy \
    python-jose[cryptography] \
    passlib[bcrypt] \
    python-multipart \
    httpx \
    pytest \
    pytest-asyncio \
    bcrypt

# Check if installation was successful
echo ""
echo "✓ Python packages installed"

# Install frontend dependencies
echo ""
echo "📦 Installing Frontend dependencies..."
cd frontend

if command -v npm &> /dev/null; then
    npm install
    echo "✓ Frontend dependencies installed"
else
    echo "⚠️  npm not found - cannot install frontend dependencies"
    echo "   To install Node.js and npm:"
    echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
fi

cd ..

echo ""
echo "================================================"
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Run the diagnostic: python3 ../utils/diagnose.py"
echo "2. Start services: python3 ../utils/start-services.py"
echo "================================================"