#!/usr/bin/env python3
"""
Start all SoA Optimizer services without Docker
This script handles dependency issues and starts services in a controlled manner
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

# Store process references
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Stopping all services...")
    for proc in processes:
        try:
            proc.terminate()
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def check_dependencies():
    """Check and install required Python packages"""
    print("📦 Checking Python dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'sqlalchemy', 
        'python-jose', 'passlib', 'python-multipart', 'httpx',
        'pytest', 'bcrypt'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"   Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', '--quiet', package], 
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

def start_service(name, directory, port, main_file='main.py'):
    """Start a Python service"""
    print(f"📡 Starting {name}...")
    
    # Change to service directory
    original_dir = os.getcwd()
    os.chdir(directory)
    
    # Start the service
    log_file = open(f'/tmp/{name.lower().replace(" ", "_")}.log', 'w')
    proc = subprocess.Popen(
        [sys.executable, main_file],
        stdout=log_file,
        stderr=log_file,
        env={**os.environ, 'PYTHONPATH': directory}
    )
    
    processes.append(proc)
    os.chdir(original_dir)
    
    # Wait a bit for service to start
    time.sleep(2)
    
    # Check if service started
    if proc.poll() is None:
        print(f"   ✓ {name} running on http://localhost:{port}")
        return True
    else:
        print(f"   ⚠️  {name} failed to start - check logs")
        return False

def init_database():
    """Initialize the database if needed"""
    db_path = Path('backend/soa_optimizer.db')
    if not db_path.exists():
        print("   Initializing database...")
        os.chdir('backend')
        try:
            subprocess.run([sys.executable, '-c', 
                          'from database import init_db; init_db()'],
                         capture_output=True, text=True)
        except Exception as e:
            print(f"   Warning: Database initialization issue: {e}")
        os.chdir('..')

def start_frontend():
    """Start the React frontend if npm is available"""
    # Check if npm exists
    npm_check = subprocess.run(['which', 'npm'], capture_output=True)
    if npm_check.returncode != 0:
        print("⚠️  npm not found - Frontend will not be started")
        print("   Install Node.js and npm to run the frontend")
        return False
    
    print("🎨 Starting Frontend...")
    os.chdir('frontend')
    
    # Check if node_modules exists
    if not Path('node_modules').exists():
        print("   Installing frontend dependencies (this may take a minute)...")
        subprocess.run(['npm', 'install'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    
    # Start frontend
    log_file = open('/tmp/frontend.log', 'w')
    proc = subprocess.Popen(
        ['npm', 'start'],
        stdout=log_file,
        stderr=log_file,
        env={**os.environ, 'REACT_APP_API_URL': 'http://localhost:8080'}
    )
    processes.append(proc)
    os.chdir('..')
    
    print("   ✓ Frontend starting on http://localhost:3000")
    return True

def main():
    """Main function to start all services"""
    print("🚀 Starting SoA Optimizer Application")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    # Start services
    services_started = []
    
    # Start MCP services
    if start_service("Protocol Complexity Analyzer", 
                    "services/mcp_ProtocolComplexityAnalyzer", 8001):
        services_started.append("MCP1")
    
    if start_service("Compliance Knowledge Base", 
                    "services/mcp_ComplianceKnowledgeBase", 8002):
        services_started.append("MCP2")
    
    # Initialize database
    init_database()
    
    # Start backend
    if start_service("Backend API", "backend", 8080):
        services_started.append("Backend")
    
    # Start frontend
    if start_frontend():
        services_started.append("Frontend")
    
    # Summary
    print("")
    print("=" * 50)
    
    if len(services_started) > 0:
        print("✅ Services started successfully!")
        print("")
        print("Access the application:")
        if "Frontend" in services_started:
            print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8080")
        print("   API Docs: http://localhost:8080/docs")
        print("")
        print("View logs:")
        print("   Backend: tail -f /tmp/backend_api.log")
        print("   MCP1: tail -f /tmp/protocol_complexity_analyzer.log")
        print("   MCP2: tail -f /tmp/compliance_knowledge_base.log")
        if "Frontend" in services_started:
            print("   Frontend: tail -f /tmp/frontend.log")
    else:
        print("❌ No services could be started. Check the error messages above.")
    
    print("")
    print("Press Ctrl+C to stop all services")
    print("=" * 50)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            # Check if any critical service has died
            for proc in processes:
                if proc.poll() is not None:
                    # Service has stopped
                    pass
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()