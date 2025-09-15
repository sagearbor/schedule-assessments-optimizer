#!/usr/bin/env python3
"""
Diagnostic script to test each component and identify issues
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)

def test_python_imports():
    """Test if all Python imports work"""
    print_header("Testing Python Dependencies")
    
    issues = []
    
    # Test backend imports
    print("\n📦 Testing Backend imports...")
    os.chdir('backend')
    
    modules_to_test = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', None),
        ('pydantic', 'BaseModel'),
        ('sqlalchemy', 'create_engine'),
        ('jose', 'jwt'),
        ('passlib.context', 'CryptContext'),
        ('httpx', None)
    ]
    
    for module, obj in modules_to_test:
        try:
            if obj:
                exec(f"from {module} import {obj}")
            else:
                exec(f"import {module}")
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            issues.append(f"Missing: {module}")
    
    # Test local imports
    print("\n📦 Testing local Backend modules...")
    local_modules = ['models', 'database', 'auth', 'burden_calculator', 'rules_engine', 'sample_data']
    
    for module in local_modules:
        try:
            exec(f"import {module}")
            print(f"  ✓ {module}.py")
        except Exception as e:
            print(f"  ❌ {module}.py: {e}")
            issues.append(f"Error in {module}.py: {str(e)[:50]}")
    
    os.chdir('..')
    return issues

def test_database():
    """Test database initialization"""
    print_header("Testing Database")
    
    os.chdir('backend')
    try:
        result = subprocess.run(
            [sys.executable, '-c', '''
from database import init_db, SessionLocal, DBUser
init_db()
db = SessionLocal()
count = db.query(DBUser).count()
print(f"Database OK - {count} users")
db.close()
'''],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  ✓ Database: {result.stdout.strip()}")
            os.chdir('..')
            return []
        else:
            print(f"  ❌ Database error: {result.stderr}")
            os.chdir('..')
            return ["Database initialization failed"]
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        os.chdir('..')
        return [f"Database error: {e}"]

def test_backend_startup():
    """Test if backend can start"""
    print_header("Testing Backend Startup")
    
    os.chdir('backend')
    try:
        # Try to import and create the app
        result = subprocess.run(
            [sys.executable, '-c', '''
from main import app
print("FastAPI app created successfully")
print(f"Endpoints: {len(app.routes)} routes")
'''],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  ✓ {result.stdout.strip()}")
            os.chdir('..')
            return []
        else:
            print(f"  ❌ Backend startup error:\n{result.stderr}")
            os.chdir('..')
            return ["Backend won't start: " + result.stderr[:100]]
    except Exception as e:
        print(f"  ❌ Backend error: {e}")
        os.chdir('..')
        return [f"Backend error: {e}"]

def test_mcp_services():
    """Test MCP services"""
    print_header("Testing MCP Services")
    
    issues = []
    services = [
        ('services/mcp_ProtocolComplexityAnalyzer', 'Protocol Complexity Analyzer'),
        ('services/mcp_ComplianceKnowledgeBase', 'Compliance Knowledge Base')
    ]
    
    for path, name in services:
        print(f"\n📡 Testing {name}...")
        if not Path(path).exists():
            print(f"  ❌ Directory not found: {path}")
            issues.append(f"{name} directory missing")
            continue
            
        os.chdir(path)
        try:
            result = subprocess.run(
                [sys.executable, '-c', 'from main import app; print("OK")'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  ✓ {name} OK")
            else:
                print(f"  ❌ {name} error: {result.stderr[:100]}")
                issues.append(f"{name} import error")
        except Exception as e:
            print(f"  ❌ {name} error: {e}")
            issues.append(f"{name}: {e}")
        os.chdir('../..')
    
    return issues

def test_frontend():
    """Test frontend setup"""
    print_header("Testing Frontend")
    
    issues = []
    
    # Check if frontend directory exists
    if not Path('frontend').exists():
        print("  ❌ Frontend directory not found")
        return ["Frontend directory missing"]
    
    os.chdir('frontend')
    
    # Check package.json
    if Path('package.json').exists():
        print("  ✓ package.json found")
        with open('package.json') as f:
            pkg = json.load(f)
            print(f"    Name: {pkg.get('name')}")
            print(f"    Dependencies: {len(pkg.get('dependencies', {}))}")
    else:
        print("  ❌ package.json not found")
        issues.append("package.json missing")
    
    # Check if node_modules exists
    if Path('node_modules').exists():
        print("  ✓ node_modules exists")
    else:
        print("  ⚠️  node_modules not found - run 'npm install'")
        issues.append("Frontend dependencies not installed")
    
    # Check key source files
    src_files = ['src/index.tsx', 'src/App.tsx', 'public/index.html']
    for file in src_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} missing")
            issues.append(f"Missing {file}")
    
    os.chdir('..')
    return issues

def run_pytest():
    """Run pytest tests"""
    print_header("Running PyTest")
    
    os.chdir('backend')
    
    # Check if test files exist
    test_files = ['test_burden_calculator.py', 'test_rules_engine.py', 'test_main.py']
    found_tests = []
    
    for test_file in test_files:
        if Path(test_file).exists():
            found_tests.append(test_file)
            print(f"  ✓ Found {test_file}")
        else:
            print(f"  ❌ Missing {test_file}")
    
    if found_tests:
        print("\n  Running tests...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'PASSED' in line:
                    print(f"  ✓ {line}")
                elif 'FAILED' in line:
                    print(f"  ❌ {line}")
                elif 'ERROR' in line:
                    print(f"  ⚠️  {line}")
            
            if result.returncode != 0:
                print("\n  Test failures detected:")
                print(result.stderr[:500])
        except subprocess.TimeoutExpired:
            print("  ⚠️  Tests timed out")
        except Exception as e:
            print(f"  ❌ Could not run tests: {e}")
    
    os.chdir('..')

def suggest_fixes(all_issues):
    """Suggest fixes for found issues"""
    print_header("Suggested Fixes")
    
    if not all_issues:
        print("  ✅ No issues found!")
        return
    
    print("\n🔧 To fix the issues:\n")
    
    # Check for missing packages
    missing_packages = [i for i in all_issues if 'Missing:' in i]
    if missing_packages:
        packages = [i.replace('Missing: ', '') for i in missing_packages]
        print(f"1. Install missing Python packages:")
        print(f"   pip3 install --user {' '.join(packages)}\n")
    
    # Check for frontend issues
    if any('Frontend dependencies' in i for i in all_issues):
        print("2. Install frontend dependencies:")
        print("   cd frontend && npm install\n")
    
    # Check for database issues
    if any('Database' in i for i in all_issues):
        print("3. Initialize database:")
        print("   cd backend")
        print("   python3 -c 'from database import init_db; init_db()'\n")
    
    # Import errors
    import_errors = [i for i in all_issues if 'import error' in i.lower() or 'error in' in i.lower()]
    if import_errors:
        print("4. Fix import errors in these modules:")
        for error in import_errors:
            print(f"   - {error}")

def main():
    print("\n" + "="*60)
    print("  🔍 SoA Optimizer Diagnostic Tool")
    print("="*60)
    
    all_issues = []
    
    # Run all tests
    all_issues.extend(test_python_imports())
    all_issues.extend(test_database())
    all_issues.extend(test_backend_startup())
    all_issues.extend(test_mcp_services())
    all_issues.extend(test_frontend())
    
    # Run pytest if everything else is OK
    if len(all_issues) == 0:
        run_pytest()
    else:
        print_header("Skipping PyTest")
        print("  ⚠️  Fix the above issues before running tests")
    
    # Summary
    print_header("Summary")
    if all_issues:
        print(f"\n  ❌ Found {len(all_issues)} issues:\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n  ✅ All components appear to be working!")
    
    # Suggest fixes
    suggest_fixes(all_issues)
    
    print("\n" + "="*60)
    print("  Diagnostic complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()