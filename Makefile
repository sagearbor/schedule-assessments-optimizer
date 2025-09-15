.PHONY: help build up down logs test clean install dev

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies for local development"
	@echo "  make build      - Build Docker containers"
	@echo "  make up         - Start all services with Docker Compose"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs from all services"
	@echo "  make test       - Run all tests"
	@echo "  make clean      - Clean up generated files and containers"
	@echo "  make dev        - Run in development mode"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

build:
	docker compose build

up:
	docker compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3040"
	@echo "Backend API: http://localhost:8040"
	@echo "MCP Complexity Analyzer: http://localhost:8041"
	@echo "MCP Compliance KB: http://localhost:8042"

down:
	docker compose down

logs:
	docker compose logs -f

test:
	cd backend && pytest -v
	cd services/mcp_ProtocolComplexityAnalyzer && pytest -v 2>/dev/null || true
	cd services/mcp_ComplianceKnowledgeBase && pytest -v 2>/dev/null || true

clean:
	docker compose down -v
	rm -rf backend/__pycache__
	rm -rf backend/*.db
	rm -rf backend/.pytest_cache
	rm -rf frontend/node_modules
	rm -rf frontend/build
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete

dev:
	@echo "Starting development servers..."
	@echo "Please run these commands in separate terminals:"
	@echo "1. Backend: cd backend && uvicorn main:app --reload --port 8040"
	@echo "2. Frontend: cd frontend && npm start"
	@echo "3. MCP Complexity: cd services/mcp_ProtocolComplexityAnalyzer && uvicorn main:app --reload --port 8041"
	@echo "4. MCP Compliance: cd services/mcp_ComplianceKnowledgeBase && uvicorn main:app --reload --port 8042"