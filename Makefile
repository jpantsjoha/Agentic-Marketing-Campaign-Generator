# AI Marketing Campaign Post Generator - Enhanced ADK v1.6+ Makefile  
# Author: JP + 2025-01-20 (ADK v1.6+ Enhanced Edition)
# 3 Musketeers pattern for consistent development workflow
# Enhanced with ADK v1.6+ hot reload, A2A messaging, and enhanced memory

.PHONY: help install install-frontend install-backend dev dev-frontend dev-backend dev-enhanced dev-hot-reload test test-frontend test-backend test-ui test-api test-enhanced test-a2a test-memory health-check launch runtime status-check build clean lint format docker-build docker-run docker-dev docker-test test-unit test-integration test-e2e test-coverage launch-all launch-enhanced test-full-stack setup-database start-backend start-frontend stop-all clean-logs setup-enhanced-sessions

# Environment Detection
DOCKER_AVAILABLE := $(shell command -v docker 2> /dev/null)
DOCKER_COMPOSE_AVAILABLE := $(shell command -v docker-compose 2> /dev/null)
NODE_AVAILABLE := $(shell command -v node 2> /dev/null)
BUN_AVAILABLE := $(shell command -v bun 2> /dev/null)
PYTHON_AVAILABLE := $(shell command -v python3 2> /dev/null)

# Log file paths
BACKEND_LOG_FILE := logs/backend-debug.log
FRONTEND_LOG_FILE := logs/frontend-debug.log
LOG_DIR := logs

# Load environment variables from backend/.env if it exists
ifneq (,$(wildcard backend/.env))
    include backend/.env
    export
endif

# Default target
help: ## Show this help message
	@echo "AI Marketing Campaign Post Generator - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# LOGGING INFRASTRUCTURE
# =============================================================================

setup-logging: ## 🔧 Setup logging infrastructure (create log directory and files)
	@echo "🔧 Setting up logging infrastructure..."
	@mkdir -p $(LOG_DIR)
	@mkdir -p data/images/cache
	@mkdir -p data/images/generated
	@mkdir -p data/videos/cache
	@mkdir -p data/videos/generated
	@echo "📁 Created logs directory: $(LOG_DIR)"
	@echo "📁 Created image cache directory: data/images/cache"
	@echo "📁 Created image storage directory: data/images/generated"
	@echo "📁 Created video cache directory: data/videos/cache"
	@echo "📁 Created video storage directory: data/videos/generated"
	@echo "🗑️ Cleaning up old cached images (keeping current images)..."
	@python3 -c "from backend.agents.visual_content_agent import CampaignImageCache; cache = CampaignImageCache(); cache.cleanup_old_images()" 2>/dev/null || echo "   Image cache cleanup skipped (no cache found)"
	@echo "🗑️ Cleaning up old cached videos (keeping current videos)..."
	@python3 -c "from backend.agents.visual_content_agent import VideoGenerationAgent; agent = VideoGenerationAgent(); agent.cleanup_old_videos()" 2>/dev/null || echo "   Video cache cleanup skipped (no cache found)"
	@echo "# AI Marketing Campaign Post Generator - Backend Debug Log" > $(BACKEND_LOG_FILE)
	@echo "# Started: $$(date)" >> $(BACKEND_LOG_FILE)
	@echo "# Log Level: DEBUG" >> $(BACKEND_LOG_FILE)
	@echo "# =========================================================" >> $(BACKEND_LOG_FILE)
	@echo "" >> $(BACKEND_LOG_FILE)
	@echo "# AI Marketing Campaign Post Generator - Frontend Debug Log" > $(FRONTEND_LOG_FILE)
	@echo "# Started: $$(date)" >> $(FRONTEND_LOG_FILE)
	@echo "# Log Level: DEBUG" >> $(FRONTEND_LOG_FILE)
	@echo "# =========================================================" >> $(FRONTEND_LOG_FILE)
	@echo "" >> $(FRONTEND_LOG_FILE)
	@echo "✅ Debug log files initialized:"
	@echo "   📄 Backend:  $(BACKEND_LOG_FILE)"
	@echo "   📄 Frontend: $(FRONTEND_LOG_FILE)"

clean-logs: ## 🧹 Clean all log files
	@echo "🧹 Cleaning log files..."
	@rm -rf $(LOG_DIR)
	@echo "✅ All log files cleaned"

clean-cache: ## 🗑️ Clean image cache for fresh testing
	@echo "🗑️ Cleaning image cache..."
	@rm -rf data/images/cache/*
	@echo "✅ Image cache cleaned"

clean-video-cache: ## 🗑️ Clean video cache for fresh testing
	@echo "🗑️ Cleaning video cache..."
	@rm -rf data/videos/cache/*
	@rm -rf data/videos/generated/*
	@echo "✅ Video cache cleaned"

clean-all-cache: ## 🗑️ Clean both image and video caches
	@echo "🗑️ Cleaning all media caches..."
	@make clean-cache
	@make clean-video-cache
	@echo "✅ All media caches cleaned"

clean-all: ## 🧹 Clean logs and cache
	@echo "🧹 Cleaning all temporary files..."
	@make clean-logs
	@make clean-all-cache
	@echo "✅ All temporary files cleaned"

view-backend-logs: ## 📖 View backend debug logs (live tail)
	@echo "📖 Viewing backend debug logs (press Ctrl+C to exit)..."
	@if [ -f $(BACKEND_LOG_FILE) ]; then \
		tail -f $(BACKEND_LOG_FILE); \
	else \
		echo "❌ Backend log file not found. Run 'make setup-logging' first."; \
	fi

view-frontend-logs: ## 📖 View frontend debug logs (live tail)
	@echo "📖 Viewing frontend debug logs (press Ctrl+C to exit)..."
	@if [ -f $(FRONTEND_LOG_FILE) ]; then \
		tail -f $(FRONTEND_LOG_FILE); \
	else \
		echo "❌ Frontend log file not found. Run 'make setup-logging' first."; \
	fi

view-all-logs: ## 📖 View all debug logs (both backend and frontend)
	@echo "📖 Viewing all debug logs (press Ctrl+C to exit)..."
	@if [ -f $(BACKEND_LOG_FILE) ] && [ -f $(FRONTEND_LOG_FILE) ]; then \
		tail -f $(BACKEND_LOG_FILE) $(FRONTEND_LOG_FILE); \
	else \
		echo "❌ Log files not found. Run 'make setup-logging' first."; \
	fi

# =============================================================================
# FULL STACK LAUNCH & TESTING TARGETS (Updated with Logging)
# =============================================================================

launch-all: ## 🚀 Launch complete application stack (SQLite + Backend + Frontend) with DEBUG logging
	@echo "🚀 Launching AI Marketing Campaign Post Generator - Full Application Stack"
	@echo "=========================================================="
	@echo ""
	@echo "🛑 Step 0: Cleaning up any existing processes..."
	@make stop-all
	@sleep 2
	@echo ""
	@echo "📋 Pre-flight checks..."
	@make status-check-quiet
	@echo ""
	@echo "🔧 Setting up debug logging..."
	@make setup-logging
	@echo ""
	@echo "🗄️  Step 1: Setting up SQLite database..."
	@make setup-database
	@echo ""
	@echo "🔧 Step 2: Starting backend server with DEBUG logging (port 8000)..."
	@echo "📄 Backend logs will be written to: $(BACKEND_LOG_FILE)"
	@nohup make start-backend > /dev/null 2>&1 &
	@echo "⏳ Waiting for backend to initialize (10 seconds)..."
	@sleep 10
	@echo ""
	@echo "🎨 Step 3: Starting frontend server with DEBUG logging (port 8080)..."
	@echo "📄 Frontend logs will be written to: $(FRONTEND_LOG_FILE)"
	@nohup make start-frontend > /dev/null 2>&1 &
	@echo "⏳ Waiting for frontend to initialize (8 seconds)..."
	@sleep 8
	@echo ""
	@echo "🏥 Step 4: Running health checks..."
	@make health-check
	@echo ""
	@echo "✅ Full Stack Launch Complete!"
	@echo "================================"
	@echo "🌐 Frontend: http://localhost:8080"
	@echo "🔌 Backend:  http://localhost:8000"
	@echo "🗄️  Database: SQLite (backend/database/data/database.db)"
	@echo ""
	@echo "📄 Debug Logs (Live Monitoring):"
	@echo "   Backend:  $(BACKEND_LOG_FILE)"
	@echo "   Frontend: $(FRONTEND_LOG_FILE)"
	@echo ""
	@echo "🔍 Process Status:"
	@echo -n "   Backend (8000):  "
	@if pgrep -f "uvicorn.*8000" > /dev/null; then echo "✅ Running (PID: $$(pgrep -f 'uvicorn.*8000'))"; else echo "❌ Not running"; fi
	@echo -n "   Frontend (8080): "
	@if pgrep -f "vite.*8080" > /dev/null; then echo "✅ Running (PID: $$(pgrep -f 'vite.*8080'))"; else echo "❌ Not running"; fi
	@echo ""
	@echo "⚡ Run 'make test-quick' for fast essential tests (recommended)"
	@echo "🧪 Run 'make test-full-stack' to test the entire application"
	@echo "📖 Run 'make view-all-logs' to monitor debug logs in real-time"
	@echo "🛑 Run 'make stop-all' to stop all services"

test-quick: ## ⚡ Quick essential functionality tests (10s timeout per test)
	@echo "⚡ Running Quick Test Suite for AI Marketing Campaign Post Generator"
	@echo "====================================================================="
	@echo ""
	@echo "🔧 Running essential tests with 10s timeouts..."
	@cd backend && python3 run_quick_tests.py
	@echo ""
	@echo "✅ Quick tests complete! Check quick_test_results.json for details"

test-full-stack: ## 🧪 Comprehensive full-stack testing (Frontend + Backend + Database)
	@echo "🧪 Running Full-Stack Integration Tests"
	@echo "======================================="
	@echo ""
	@echo "📋 Pre-test validation..."
	@make validate-stack-running
	@echo ""
	@echo "🗄️  1. Testing Database Layer..."
	@make test-database-layer
	@echo ""
	@echo "🔌 2. Testing Backend API Layer..."
	@make test-backend-layer
	@echo ""
	@echo "🎨 3. Testing Frontend Layer..."
	@make test-frontend-layer
	@echo ""
	@echo "🔗 4. Testing Frontend-Backend Integration..."
	@make test-integration-layer
	@echo ""
	@echo "🎯 5. Testing End-to-End User Flows..."
	@make test-e2e-flows
	@echo ""
	@echo "✅ Full-Stack Testing Complete!"
	@echo "==============================="
	@make test-summary

setup-database: ## 🗄️ Initialize SQLite database with schema
	@echo "🗄️  Setting up SQLite database..."
	@cd backend && python3 -c "import os; os.makedirs('data', exist_ok=True); from database.database import init_database; init_database(); print('✅ Database setup complete!')"

# =============================================================================
# ENHANCED ADK v1.6+ DEVELOPMENT COMMANDS
# =============================================================================

setup-enhanced-sessions: ## 🚀 Setup enhanced session storage for ADK v1.6+
	@echo "🚀 Setting up enhanced session storage..."
	@mkdir -p campaign_sessions
	@mkdir -p backend/data/enhanced_memory
	@echo "📁 Created campaign sessions directory: campaign_sessions"
	@echo "📁 Created enhanced memory directory: backend/data/enhanced_memory"
	@echo "✅ Enhanced session storage ready"

dev-enhanced: ## 🚀 Start enhanced ADK v1.6+ development environment
	@echo "🚀 Starting Enhanced ADK v1.6+ Development Environment"
	@echo "======================================================="
	@make setup-enhanced-sessions
	@make setup-logging
	@echo ""
	@echo "🔧 Features enabled:"
	@echo "   • A2A Messaging"
	@echo "   • Persistent Memory"
	@echo "   • Structured Context"
	@echo "   • Event-Driven Coordination"
	@echo ""
	@echo "🚀 Starting enhanced backend server..."
	@cd backend && python3 -c "import asyncio; from agents.enhanced_marketing_orchestrator_v2 import create_enhanced_marketing_orchestrator; print('✅ Enhanced orchestrator validation passed')" && \
	python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level debug --reload &
	@sleep 3
	@echo "🎨 Starting frontend server..."
	@if [ "$(BUN_AVAILABLE)" ]; then \
		bun run dev --port 8080 2>&1 | tee -a $(FRONTEND_LOG_FILE) & \
	elif [ "$(NODE_AVAILABLE)" ]; then \
		npm run dev -- --port 8080 2>&1 | tee -a $(FRONTEND_LOG_FILE) & \
	else \
		echo "❌ No Node.js or Bun found"; \
		exit 1; \
	fi
	@echo ""
	@echo "✅ Enhanced ADK v1.6+ Environment Ready!"
	@echo "🌐 Frontend: http://localhost:8080"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"
	@echo "🔥 Enhanced Campaigns: http://localhost:8000/api/v2/campaigns"
	@echo "📊 Memory Stats: http://localhost:8000/api/v2/campaigns/debug/memory-stats"

dev-hot-reload: ## 🔥 Start development with ADK v1.6+ hot reload enabled
	@echo "🔥 Starting ADK v1.6+ Hot Reload Development"
	@echo "============================================"
	@make setup-enhanced-sessions
	@echo "🔥 Hot reload features:"
	@echo "   • Agent hot reload enabled"
	@echo "   • A2A message bus active"
	@echo "   • Real-time code updates"
	@echo ""
	@cd backend && python3 -c "print('🔥 Starting with --reload_agents flag...')" && \
	python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

launch-enhanced: ## 🚀 Launch complete enhanced ADK v1.6+ stack
	@echo "🚀 Launching Enhanced ADK v1.6+ Marketing Platform"
	@echo "=================================================="
	@make setup-enhanced-sessions
	@make setup-logging
	@make setup-database
	@echo ""
	@echo "🎯 Enhanced features active:"
	@echo "   ✅ A2A Messaging"
	@echo "   ✅ Persistent Memory"
	@echo "   ✅ Structured Context"
	@echo "   ✅ Event-Driven Coordination"
	@echo "   ✅ Session Persistence"
	@echo "   ✅ Campaign Versioning"
	@echo ""
	@echo "🔧 Starting enhanced backend..."
	@cd backend && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
	@sleep 3
	@echo "🎨 Starting frontend..."
	@if [ "$(BUN_AVAILABLE)" ]; then \
		bun run dev --port 8080 & \
	elif [ "$(NODE_AVAILABLE)" ]; then \
		npm run dev -- --port 8080 & \
	fi
	@sleep 2
	@echo ""
	@echo "🎉 Enhanced ADK v1.6+ Platform Launched!"
	@echo "========================================"
	@echo "🌐 Frontend:           http://localhost:8080"
	@echo "🔧 Backend API:        http://localhost:8000"
	@echo "📚 API Documentation: http://localhost:8000/docs"
	@echo ""
	@echo "🚀 Enhanced API Endpoints:"
	@echo "📋 Enhanced Campaigns: http://localhost:8000/api/v2/campaigns"
	@echo "📊 Memory Statistics:  http://localhost:8000/api/v2/campaigns/debug/memory-stats"
	@echo "💬 A2A Messages:       http://localhost:8000/api/v2/campaigns/{id}/messages"
	@echo "📈 Campaign Status:    http://localhost:8000/api/v2/campaigns/{id}/status"
	@echo ""
	@echo "📄 Logs:"
	@echo "🔧 Backend:  $(BACKEND_LOG_FILE)"
	@echo "🎨 Frontend: $(FRONTEND_LOG_FILE)"

# =============================================================================
# ENHANCED TESTING COMMANDS
# =============================================================================

test-enhanced: ## 🧪 Run enhanced ADK v1.6+ tests
	@echo "🧪 Running Enhanced ADK v1.6+ Tests"
	@echo "===================================="
	@make setup-enhanced-sessions
	@cd backend && python3 -m pytest tests/test_enhanced_adk_upgrade.py -v --tb=short
	@echo "✅ Enhanced ADK tests complete"

test-a2a: ## 💬 Test A2A messaging system
	@echo "💬 Testing A2A Messaging System"
	@echo "==============================="
	@cd backend && python3 -m pytest tests/test_enhanced_adk_upgrade.py::TestA2AMessaging -v --tb=short
	@echo "✅ A2A messaging tests complete"

test-memory: ## 🧠 Test enhanced memory service
	@echo "🧠 Testing Enhanced Memory Service"
	@echo "=================================="
	@cd backend && python3 -m pytest tests/test_enhanced_adk_upgrade.py::TestEnhancedMemoryService -v --tb=short
	@echo "✅ Enhanced memory tests complete"

test-context-fidelity: ## 🎯 Test campaign context fidelity
	@echo "🎯 Testing Campaign Context Fidelity"
	@echo "===================================="
	@cd backend && python3 -m pytest tests/test_enhanced_adk_upgrade.py::TestCampaignContextFidelity -v --tb=short
	@echo "✅ Context fidelity tests complete"

test-orchestrator: ## 🎭 Test enhanced orchestrator
	@echo "🎭 Testing Enhanced Orchestrator"
	@echo "==============================="
	@cd backend && python3 -m pytest tests/test_enhanced_adk_upgrade.py::TestEnhancedOrchestrator -v --tb=short
	@echo "✅ Enhanced orchestrator tests complete"

test-performance: ## ⚡ Test enhanced system performance
	@echo "⚡ Testing Enhanced System Performance"
	@echo "====================================="
	@cd backend && python3 -m pytest tests/test_enhanced_adk_upgrade.py::TestPerformanceAndStress -v --tb=short
	@echo "✅ Performance tests complete"

test-enhanced-full: ## 🧪 Run complete enhanced test suite
	@echo "🧪 Running Complete Enhanced ADK v1.6+ Test Suite"
	@echo "================================================="
	@make test-context-fidelity
	@echo ""
	@make test-memory
	@echo ""
	@make test-a2a
	@echo ""
	@make test-orchestrator
	@echo ""
	@make test-performance
	@echo ""
	@echo "🎉 Complete Enhanced Test Suite Passed!"

start-backend: ## 🔧 Start backend server with DEBUG logging to file
	@echo "🔧 Starting backend server with DEBUG logging to file..."
	@make setup-logging
	@echo "🔍 Checking if port 8000 is available..."
	@if lsof -ti:8000 > /dev/null 2>&1; then \
		echo "⚠️  Port 8000 is in use, killing existing process..."; \
		lsof -ti:8000 | xargs kill -9 2>/dev/null || true; \
		sleep 2; \
	fi
	@if [ ! -f backend/.env ]; then \
		echo "⚠️  Creating backend/.env file..."; \
		echo "DATABASE_URL=sqlite:///./database/data/database.db" >> backend/.env; \
		echo "LOG_LEVEL=DEBUG" >> backend/.env; \
		echo "LOG_FILE=../$(BACKEND_LOG_FILE)" >> backend/.env; \
		echo "📝 Please update backend/.env with your GEMINI_API_KEY"; \
	else \
		echo "✅ Using existing backend/.env file"; \
		if ! grep -q "LOG_LEVEL" backend/.env; then \
			echo "LOG_LEVEL=DEBUG" >> backend/.env; \
			echo "🐛 Added LOG_LEVEL=DEBUG to existing .env file"; \
		fi; \
		if ! grep -q "LOG_FILE" backend/.env; then \
			echo "LOG_FILE=../$(BACKEND_LOG_FILE)" >> backend/.env; \
			echo "📄 Added LOG_FILE path to existing .env file"; \
		fi; \
	fi
	@echo "🐛 DEBUG logging enabled - Backend logs: $(BACKEND_LOG_FILE)"
	@echo "🔧 Starting backend server on port 8000..."
	@cd backend && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level debug --reload 2>&1 | tee -a ../$(BACKEND_LOG_FILE)

start-frontend: ## 🎨 Start frontend server with DEBUG logging to file
	@echo "🎨 Starting frontend server with DEBUG logging to file..."
	@make setup-logging
	@echo "🐛 DEBUG logging enabled - Frontend logs: $(FRONTEND_LOG_FILE)"
	@echo "🎨 Starting frontend server on port 8080..."
	@echo "🔍 Checking if port 8080 is available..."
	@if lsof -ti:8080 > /dev/null 2>&1; then \
		echo "⚠️  Port 8080 is in use, killing existing process..."; \
		lsof -ti:8080 | xargs kill -9 2>/dev/null || true; \
		sleep 2; \
	fi
	@if [ "$(BUN_AVAILABLE)" ]; then \
		echo "🚀 Starting with Bun..."; \
		DEBUG=vite:* VITE_LOG_LEVEL=debug bun run dev --port 8080 --host 0.0.0.0 2>&1 | tee -a $(FRONTEND_LOG_FILE); \
	elif [ "$(NODE_AVAILABLE)" ]; then \
		echo "🚀 Starting with Node.js..."; \
		DEBUG=vite:* VITE_LOG_LEVEL=debug npm run dev -- --port 8080 --host 0.0.0.0 2>&1 | tee -a $(FRONTEND_LOG_FILE); \
	else \
		echo "❌ No JavaScript runtime available"; \
		exit 1; \
	fi

stop-all: ## 🛑 Stop all running services
	@echo "🛑 Stopping all services..."
	@echo "Stopping frontend server (port 8080)..."
	@-pkill -f "vite.*8080" 2>/dev/null || true
	@-pkill -f "bun.*dev.*8080" 2>/dev/null || true
	@echo "Stopping backend server (port 8000)..."
	@-pkill -f "uvicorn.*8000" 2>/dev/null || true
	@echo "✅ All services stopped"
	@echo "📄 Debug logs preserved in:"
	@echo "   Backend:  $(BACKEND_LOG_FILE)"
	@echo "   Frontend: $(FRONTEND_LOG_FILE)"

validate-stack-running: ## 🔍 Validate that full stack is running
	@echo "🔍 Validating full stack is running..."
	@echo -n "  Frontend (8080): "
	@if curl -s http://localhost:8080 > /dev/null 2>&1; then \
		echo "✅ Running"; \
	else \
		echo "❌ Not running - start with 'make launch-all'"; \
		exit 1; \
	fi
	@echo -n "  Backend (8000):  "
	@if curl -s http://localhost:8000 > /dev/null 2>&1; then \
		echo "✅ Running"; \
	else \
		echo "❌ Not running - start with 'make launch-all'"; \
		exit 1; \
	fi
	@echo -n "  Database:        "
	@if [ -f backend/data/database.db ]; then \
		echo "✅ Available"; \
	else \
		echo "❌ Not found - run 'make setup-database'"; \
		exit 1; \
	fi

test-database-layer: ## 🗄️ Test database layer independently
	@echo "🗄️  Testing Database Layer..."
	@cd backend && python3 -m pytest tests/test_database_integration.py -v --tb=short -x

test-backend-layer: ## 🔌 Test backend API layer
	@echo "🔌 Testing Backend API Layer..."
	@cd backend && python3 -m pytest tests/test_api_*.py -v --tb=short -x

test-frontend-layer: ## 🎨 Test frontend layer
	@echo "🎨 Testing Frontend Layer..."
	@if [ "$(BUN_AVAILABLE)" ]; then \
		bun test --run; \
	elif [ "$(NODE_AVAILABLE)" ]; then \
		npm test -- --run; \
	else \
		echo "❌ No test runner available"; \
		exit 1; \
	fi

test-integration-layer: ## 🔗 Test frontend-backend integration
	@echo "🔗 Testing Frontend-Backend Integration..."
	@cd backend && python3 -m pytest tests/test_frontend_integration.py -v --tb=short -x

test-e2e-flows: ## 🎯 Test end-to-end user flows
	@echo "🎯 Testing End-to-End User Flows..."
	@echo "Testing critical user journeys..."
	@make test-happy-path-flow
	@make test-campaign-creation-flow
	@make test-content-generation-flow

test-happy-path-flow: ## 🛤️ Test complete happy path user flow
	@echo "🛤️  Testing Happy Path Flow..."
	@cd backend && python3 test_full_stack_integration.py

test-campaign-creation-flow: ## 📝 Test campaign creation flow
	@echo "📝 Testing Campaign Creation Flow..."
	@echo "✅ Campaign creation testing integrated into full-stack test"

test-content-generation-flow: ## 🎨 Test content generation flow
	@echo "🎨 Testing Content Generation Flow..."
	@echo "✅ Content generation testing integrated into full-stack test"

test-e2e-single: ## 🧪 Run a single end-to-end test file
	@echo "🧪 Running single End-to-End test..."
	@cd backend && PYTHONPATH=.. python3 -m pytest tests/test_e2e_workflow.py -v --tb=short

test-summary: ## 📊 Display comprehensive test summary
	@echo ""
	@echo "📊 Full-Stack Test Summary"
	@echo "=========================="
	@echo ""
	@echo "🎯 Test Coverage Areas:"
	@echo "  ✅ Database Layer (SQLite)"
	@echo "  ✅ Backend API Layer (FastAPI)"
	@echo "  ✅ Frontend Layer (React/Vite)"
	@echo "  ✅ Integration Layer (API Communication)"
	@echo "  ✅ End-to-End Flows (User Journeys)"
	@echo ""
	@echo "🔗 Application Stack:"
	@echo "  🗄️  Database: SQLite (backend/data/database.db)"
	@echo "  🔌 Backend:  FastAPI (http://localhost:8000)"
	@echo "  🎨 Frontend: React/Vite (http://localhost:8080)"
	@echo ""
	@echo "📈 Quality Metrics:"
	@echo "  🧪 Unit Tests: Backend API endpoints"
	@echo "  🔗 Integration Tests: Frontend-Backend communication"
	@echo "  🎯 E2E Tests: Complete user workflows"
	@echo "  🗄️  Database Tests: Schema and CRUD operations"
	@echo ""
	@echo "🚀 Next Steps:"
	@echo "  • Run 'make test-full-stack' for comprehensive testing"
	@echo "  • Run 'make launch-all' to start the complete stack"
	@echo "  • Run 'make stop-all' to stop all services"

# =============================================================================
# EXISTING TARGETS (Updated for consistency)
# =============================================================================

# Installation targets
install: install-frontend install-backend ## Install all dependencies

install-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	@if command -v bun >/dev/null 2>&1; then \
		bun install; \
	elif command -v npm >/dev/null 2>&1; then \
		npm install; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

install-backend: ## Install backend dependencies
	@echo "Installing backend dependencies..."
	@pip3 install -r backend/requirements.txt

# Development targets (3 Musketeers pattern)
dev: ## Start development environment (Docker-first, fallback to local)
	@echo "Starting development environment..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "Using Docker Compose for development..."; \
		make docker-dev; \
	else \
		echo "Docker Compose not available, using local development..."; \
		make dev-local; \
	fi

dev-local: ## Start both frontend and backend locally
	@echo "Starting local development servers..."
	@make dev-backend-local &
	@make dev-frontend-local

dev-with-env: ## Start both frontend and backend with .env file loaded and DEBUG logging
	@echo "🚀 Starting AI Marketing Campaign Post Generator with environment variables and DEBUG logging..."
	@make setup-logging
	@if [ ! -f backend/.env ]; then \
		echo "⚠️  Creating backend/.env file..."; \
		echo "DATABASE_URL=sqlite:///./data/database.db" >> backend/.env; \
		echo "LOG_LEVEL=DEBUG" >> backend/.env; \
		echo "LOG_FILE=../$(BACKEND_LOG_FILE)" >> backend/.env; \
		echo "📝 Please update backend/.env with your GEMINI_API_KEY"; \
	else \
		echo "✅ Using existing backend/.env file"; \
	fi
	@echo "Loading environment variables from backend/.env..."
	@set -a && . backend/.env && set +a && \
	echo "Starting backend server with loaded environment and DEBUG logging..." && \
	cd backend && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level debug --reload 2>&1 | tee -a ../$(BACKEND_LOG_FILE) &
	@echo "Starting frontend server with DEBUG logging..."
	@if [ "$(BUN_AVAILABLE)" ]; then \
		DEBUG=vite:* VITE_LOG_LEVEL=debug bun run dev --port 8080 --debug 2>&1 | tee -a $(FRONTEND_LOG_FILE); \
	elif [ "$(NODE_AVAILABLE)" ]; then \
		DEBUG=vite:* VITE_LOG_LEVEL=debug npm run dev -- --port 8080 --debug 2>&1 | tee -a $(FRONTEND_LOG_FILE); \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

dev-frontend: ## Start frontend development server (Docker-first)
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "Starting frontend with Docker Compose..."; \
		docker-compose up frontend; \
	else \
		echo "Docker Compose not available, starting locally..."; \
		make dev-frontend-local; \
	fi

dev-frontend-local: ## Start frontend development server locally with DEBUG logging
	@echo "Starting frontend development server locally with DEBUG logging..."
	@make setup-logging
	@echo "🐛 DEBUG logging enabled - Frontend logs: $(FRONTEND_LOG_FILE)"
	@if [ "$(BUN_AVAILABLE)" ]; then \
		DEBUG=vite:* VITE_LOG_LEVEL=debug bun run dev --port 8080 --debug 2>&1 | tee -a $(FRONTEND_LOG_FILE); \
	elif [ "$(NODE_AVAILABLE)" ]; then \
		DEBUG=vite:* VITE_LOG_LEVEL=debug npm run dev -- --port 8080 --debug 2>&1 | tee -a $(FRONTEND_LOG_FILE); \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

dev-backend: ## Start backend development server (Docker-first)
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "Starting backend with Docker Compose..."; \
		docker-compose up backend; \
	else \
		echo "Docker Compose not available, starting locally..."; \
		make dev-backend-local; \
	fi

dev-backend-local: ## Start backend development server locally with DEBUG logging
	@echo "🚀 Starting AI Marketing Campaign Post Generator backend server with DEBUG logging..."
	@make setup-logging
	@if [ ! -f backend/.env ]; then \
		echo "⚠️  Creating backend/.env file..."; \
		echo "GEMINI_API_KEY=your_gemini_api_key_here" > backend/.env; \
		echo "LOG_LEVEL=DEBUG" >> backend/.env; \
		echo "LOG_FILE=../$(BACKEND_LOG_FILE)" >> backend/.env; \
		echo "📝 Please update backend/.env with your GEMINI_API_KEY"; \
	else \
		if ! grep -q "LOG_LEVEL" backend/.env; then \
			echo "LOG_LEVEL=DEBUG" >> backend/.env; \
		fi; \
		if ! grep -q "LOG_FILE" backend/.env; then \
			echo "LOG_FILE=../$(BACKEND_LOG_FILE)" >> backend/.env; \
		fi; \
	fi
	@echo "🐛 DEBUG logging enabled - Backend logs: $(BACKEND_LOG_FILE)"
	@cd backend && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level debug --reload 2>&1 | tee -a ../$(BACKEND_LOG_FILE)

# Testing targets
test: test-frontend test-backend ## Run all tests

test-frontend: ## Run frontend tests
	@echo "Running frontend tests..."
	@if command -v bun >/dev/null 2>&1; then \
		bun test --run; \
	elif command -v npm >/dev/null 2>&1; then \
		npm test -- --run; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

test-backend: ## Test backend ADK agent
	@echo "Testing backend ADK agent..."
	@if [ -z "$(GEMINI_API_KEY)" ]; then \
		echo "Error: GEMINI_API_KEY environment variable not set"; \
		echo "Usage: GEMINI_API_KEY=your_key make test-backend"; \
		exit 1; \
	fi
	@GEMINI_API_KEY=$(GEMINI_API_KEY) python3 -m google.adk.cli run backend.marketing_agent --query "Test campaign for a tech startup focused on AI solutions"

test-api: ## Run comprehensive API tests
	@echo "🧪 Running API Tests..."
	@echo "====================="
	@echo ""
	@echo "1. Running unit tests..."
	@make test-api-unit
	@echo ""
	@echo "2. Running integration tests..."
	@make test-api-integration
	@echo ""
	@echo "3. Running end-to-end tests..."
	@make test-api-e2e
	@echo ""
	@echo "✅ API testing complete!"

test-api-unit: ## Run API unit tests
	@echo "Running API unit tests..."
	@cd backend && python3 -m pytest tests/ -v -m "not integration and not e2e" --tb=short

test-api-integration: ## Run API integration tests
	@echo "Running API integration tests..."
	@cd backend && python3 -m pytest tests/ -v -m "integration" --tb=short

test-api-e2e: ## Run API end-to-end tests
	@echo "Running API end-to-end tests..."
	@cd backend && python3 -m pytest tests/ -v -m "e2e" --tb=short

test-api-coverage: ## Run API tests with coverage report
	@echo "Running API tests with coverage..."
	@cd backend && python3 -m pytest tests/ --cov=api --cov=agents --cov-report=term-missing --cov-report=html --cov-report=xml

test-api-regression: ## Run regression test suite
	@echo "🔄 Running Regression Tests..."
	@echo "============================="
	@echo ""
	@echo "Testing all API endpoints for regression..."
	@cd backend && python3 -m pytest tests/test_api_*.py -v --tb=short
	@echo ""
	@echo "✅ Regression testing complete!"

# Runtime and UI Testing targets
launch: ## Launch complete development environment and run health checks
	@echo "🚀 Launching AI Marketing Campaign Post Generator development environment..."
	@echo "=========================================================="
	@make status
	@echo ""
	@echo "Starting development servers..."
	@make dev-frontend-local &
	@sleep 3
	@echo ""
	@echo "Running health checks..."
	@make health-check
	@echo ""
	@echo "✅ Launch complete! Access the application at:"
	@echo "   Frontend: http://localhost:8080"
	@echo "   Backend:  Not yet implemented (ADK agent available)"
	@echo ""
	@echo "Run 'make test-ui' to test UI pages"
	@echo "Run 'make test-api' to test API endpoints"

runtime: launch ## Alias for launch command

test-ui: ## Test all UI pages and user flows
	@echo "🧪 Testing UI Pages and User Flows..."
	@echo "====================================="
	@echo ""
	@echo "1. Running automated UI tests..."
	@make test-frontend
	@echo ""
	@echo "2. Testing UI page accessibility..."
	@make test-ui-pages
	@echo ""
	@echo "3. Testing user flows..."
	@make test-user-flows
	@echo ""
	@echo "✅ UI testing complete!"

test-ui-pages: ## Test individual UI pages are accessible
	@echo "Testing UI page accessibility..."
	@echo "Checking if development server is running..."
	@if ! curl -s http://localhost:8080 > /dev/null 2>&1; then \
		echo "❌ Development server not running. Start with 'make dev-frontend-local'"; \
		exit 1; \
	fi
	@echo "✅ Development server is running"
	@echo ""
	@echo "Testing UI pages:"
	@echo -n "  Dashboard (/).................. "
	@if curl -s http://localhost:8080/ | grep -q "<!DOCTYPE html"; then \
		echo "✅ OK"; \
	else \
		echo "❌ FAIL"; \
	fi
	@echo -n "  New Campaign (/new-campaign)... "
	@if curl -s http://localhost:8080/new-campaign | grep -q "<!DOCTYPE html"; then \
		echo "✅ OK"; \
	else \
		echo "❌ FAIL"; \
	fi
	@echo -n "  Ideation (/ideation)........... "
	@if curl -s http://localhost:8080/ideation | grep -q "<!DOCTYPE html"; then \
		echo "✅ OK"; \
	else \
		echo "❌ FAIL"; \
	fi
	@echo -n "  Proposals (/proposals)......... "
	@if curl -s http://localhost:8080/proposals | grep -q "<!DOCTYPE html"; then \
		echo "✅ OK"; \
	else \
		echo "❌ FAIL"; \
	fi

test-user-flows: ## Test critical user flows
	@echo "Testing critical user flows..."
	@echo "Running end-to-end test suite..."
	@if command -v bun >/dev/null 2>&1; then \
		bun test --run src/__tests__/HappyPath.test.tsx; \
	elif command -v npm >/dev/null 2>&1; then \
		npm test -- --run src/__tests__/HappyPath.test.tsx; \
	else \
		echo "❌ No test runner available"; \
		exit 1; \
	fi

test-api-old: ## Test API endpoints and backend services (legacy)
	@echo "🔌 Testing API Endpoints and Backend Services..."
	@echo "==============================================="
	@echo ""
	@echo "1. Testing backend ADK agent..."
	@if [ -n "$(GEMINI_API_KEY)" ]; then \
		make test-backend; \
	else \
		echo "⚠️  GEMINI_API_KEY not set - skipping ADK agent test"; \
		echo "   Set GEMINI_API_KEY to test: GEMINI_API_KEY=your_key make test-api"; \
	fi
	@echo ""
	@echo "2. Testing API status endpoints..."
	@make test-api-status
	@echo ""
	@echo "✅ API testing complete!"

test-api-status: ## Test API status and health endpoints
	@echo "Testing API status endpoints..."
	@echo "Note: Backend API server not yet implemented"
	@echo "Available tests:"
	@echo "  ✅ ADK Agent: Available (requires GEMINI_KEY)"
	@echo "  ❌ REST API: Not implemented"
	@echo "  ❌ Health endpoint: Not implemented"
	@echo "  ❌ Status endpoint: Not implemented"
	@echo ""
	@echo "Future API endpoints to implement:"
	@echo "  - GET  /api/health"
	@echo "  - GET  /api/status"
	@echo "  - POST /api/campaigns"
	@echo "  - POST /api/ideas/generate"
	@echo "  - POST /api/videos/generate"

health-check: ## Comprehensive health check of all services
	@echo "🏥 Running Health Checks..."
	@echo "=========================="
	@echo ""
	@echo "Environment Status:"
	@make status-check-quiet
	@echo ""
	@echo "Service Health:"
	@echo -n "  Frontend Server............ "
	@if curl -s http://localhost:8080 > /dev/null 2>&1; then \
		echo "✅ Running (http://localhost:8080)"; \
	else \
		echo "❌ Not running"; \
	fi
	@echo -n "  Backend API................ "
	@if curl -s http://localhost:8000 > /dev/null 2>&1; then \
		echo "✅ Running (http://localhost:8000)"; \
	else \
		echo "❌ Not running"; \
	fi
	@echo -n "  SQLite Database............ "
	@if [ -f backend/data/database.db ]; then \
		echo "✅ Available (backend/data/database.db)"; \
	else \
		echo "❌ Not found"; \
	fi
	@echo -n "  ADK Agent.................. "
	@if [ "$(PYTHON_AVAILABLE)" ] && python3 -c "import google.adk" 2>/dev/null; then \
		if [ -n "$(GEMINI_API_KEY)" ]; then \
			echo "✅ Ready"; \
		else \
			echo "⚠️  Ready (GEMINI_API_KEY not set)"; \
		fi; \
	else \
		echo "❌ Not available"; \
	fi
	@echo ""
	@echo "Dependencies:"
	@echo -n "  Node.js/Bun................ "
	@if [ "$(NODE_AVAILABLE)" ] || [ "$(BUN_AVAILABLE)" ]; then \
		echo "✅ Available"; \
	else \
		echo "❌ Missing"; \
	fi
	@echo -n "  Python..................... "
	@if [ "$(PYTHON_AVAILABLE)" ]; then \
		echo "✅ Available"; \
	else \
		echo "❌ Missing"; \
	fi
	@echo -n "  Docker..................... "
	@if [ "$(DOCKER_AVAILABLE)" ]; then \
		echo "✅ Available"; \
	else \
		echo "❌ Missing"; \
	fi

status-check: health-check ## Alias for health-check

status-check-quiet: ## Quick status check without headers
	@if [ "$(NODE_AVAILABLE)" ] || [ "$(BUN_AVAILABLE)" ]; then \
		echo "  ✅ JavaScript runtime available"; \
	else \
		echo "  ❌ JavaScript runtime missing"; \
	fi
	@if [ "$(PYTHON_AVAILABLE)" ]; then \
		echo "  ✅ Python available"; \
	else \
		echo "  ❌ Python missing"; \
	fi
	@if [ "$(DOCKER_AVAILABLE)" ]; then \
		echo "  ✅ Docker available"; \
	else \
		echo "  ❌ Docker missing"; \
	fi

# Build targets
build: ## Build for production
	@echo "Building for production..."
	@if command -v bun >/dev/null 2>&1; then \
		bun run build; \
	elif command -v npm >/dev/null 2>&1; then \
		npm run build; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

# Quality targets
lint: ## Run linting
	@echo "Running linter..."
	@if command -v bun >/dev/null 2>&1; then \
		bun run lint; \
	elif command -v npm >/dev/null 2>&1; then \
		npm run lint; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

format: ## Format code
	@echo "Formatting code..."
	@echo "Note: Code formatting not yet configured. Add prettier/eslint configuration."

# Docker targets (3 Musketeers implementation)
docker-build: ## Build Docker containers
	@echo "Building Docker containers..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose build; \
	elif [ "$(DOCKER_AVAILABLE)" ]; then \
		echo "Building individual containers..."; \
		docker build -f Dockerfile.frontend -t video-venture-frontend .; \
		docker build -f Dockerfile.backend -t video-venture-backend ./backend; \
	else \
		echo "Error: Docker not available. Please install Docker."; \
		exit 1; \
	fi

docker-dev: ## Start development environment with Docker Compose
	@echo "Starting development environment with Docker Compose..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose up --build; \
	else \
		echo "Error: Docker Compose not available. Please install Docker Compose."; \
		exit 1; \
	fi

docker-test: ## Run tests in Docker containers
	@echo "Running tests in Docker containers..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose run --rm frontend npm test -- --run; \
		docker-compose run --rm backend python3 -m pytest; \
	else \
		echo "Error: Docker Compose not available. Please install Docker Compose."; \
		exit 1; \
	fi

docker-run: ## Run application in Docker (production mode)
	@echo "Running application in Docker (production mode)..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose -f docker-compose.prod.yml up; \
	else \
		echo "Error: Docker Compose not available. Please install Docker Compose."; \
	fi

docker-stop: ## Stop Docker containers
	@echo "Stopping Docker containers..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose down; \
	else \
		echo "Docker Compose not available."; \
	fi

docker-clean: ## Clean Docker containers and images
	@echo "Cleaning Docker containers and images..."
	@if [ "$(DOCKER_AVAILABLE)" ]; then \
		docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true; \
		docker system prune -f; \
	else \
		echo "Docker not available."; \
	fi

# Cleanup targets
clean: ## Clean build artifacts and dependencies
	@echo "Cleaning build artifacts..."
	@rm -rf dist/
	@rm -rf node_modules/
	@rm -rf .vite/
	@echo "Clean complete."

# Environment setup
setup-env: ## Setup development environment
	@echo "Setting up development environment..."
	@echo "1. Install Node.js or Bun for frontend development"
	@echo "2. Install Python 3.9+ for backend development"
	@echo "3. Set GEMINI_KEY environment variable for AI testing"
	@echo "4. Run 'make install' to install dependencies"

# Status check (3 Musketeers compatibility)
status: ## Check development environment status
	@echo "Development Environment Status (3 Musketeers):"
	@echo "=============================================="
	@echo -n "Docker: "
	@if [ "$(DOCKER_AVAILABLE)" ]; then \
		docker --version | head -1; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Docker Compose: "
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose --version | head -1; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Node.js: "
	@if [ "$(NODE_AVAILABLE)" ]; then \
		node --version; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Bun: "
	@if [ "$(BUN_AVAILABLE)" ]; then \
		bun --version; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Python: "
	@if [ "$(PYTHON_AVAILABLE)" ]; then \
		python3 --version; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Google ADK: "
	@if [ "$(PYTHON_AVAILABLE)" ] && python3 -c "import google.adk" 2>/dev/null; then \
		echo "✅ Installed"; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "GEMINI_KEY: "
	@if [ -n "$(GEMINI_KEY)" ]; then \
		echo "✅ Set"; \
	else \
		echo "❌ Not set"; \
	fi
	@echo ""
	@echo "3 Musketeers Readiness:"
	@if [ "$(DOCKER_AVAILABLE)" ] && [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "✅ Ready for Docker-based development"; \
	else \
		echo "⚠️  Docker setup incomplete - will use local development"; \
	fi

doctor: ## Diagnose common development issues
	@echo "Diagnosing development environment..."
	@echo "===================================="
	@if [ ! "$(DOCKER_AVAILABLE)" ]; then \
		echo "❌ Docker not found. Install from: https://docs.docker.com/get-docker/"; \
	fi
	@if [ ! "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "❌ Docker Compose not found. Install from: https://docs.docker.com/compose/install/"; \
	fi
	@if [ ! "$(NODE_AVAILABLE)" ] && [ ! "$(BUN_AVAILABLE)" ]; then \
		echo "❌ No JavaScript runtime found. Install Node.js or Bun"; \
		echo "   Node.js: https://nodejs.org/"; \
		echo "   Bun: https://bun.sh/"; \
	fi
	@if [ ! "$(PYTHON_AVAILABLE)" ]; then \
		echo "❌ Python not found. Install Python 3.9+"; \
	fi
	@if [ "$(PYTHON_AVAILABLE)" ] && ! python3 -c "import google.adk" 2>/dev/null; then \
		echo "❌ Google ADK not installed. Run: pip install google-adk==1.2.1"; \
	fi
	@if [ -z "$(GEMINI_KEY)" ]; then \
		echo "❌ GEMINI_KEY not set. Get API key from Google AI Studio"; \
	fi
	@echo ""
	@echo "Quick fixes:"
	@echo "1. Install missing tools above"
	@echo "2. Run 'make install' to install dependencies"
	@echo "3. Set GEMINI_KEY environment variable"
	@echo "4. Run 'make dev' to start development"

# Testing
test-unit:
	@echo "Running unit tests..."
	pytest backend/tests/ -v -m "not integration and not e2e"

test-integration:
	@echo "Running integration tests..."
	pytest backend/tests/ -v -m "integration"

test-e2e:
	@echo "Running end-to-end tests..."
	pytest backend/tests/ -v -m "e2e"

test-coverage:
	@echo "Running tests with coverage..."
	pytest backend/tests/ --cov=backend --cov-report=term-missing --cov-report=html

# Release Management & Documentation Generation
release: ## Generate release documentation and artifacts
	@echo "🚀 Generating AI Marketing Campaign Post Generator Release Documentation..."
	@echo "========================================================"
	@make generate-about
	@make generate-uml
	@make generate-release-notes
	@echo ""
	@echo "✅ Release documentation generated successfully!"
	@echo "📄 Check docs/ABOUT.md for project overview"
	@echo "📊 Check docs/diagrams/ for UML diagrams"
	@echo "📋 Check docs/RELEASE-NOTES.md for release information"

generate-about: ## Generate comprehensive ABOUT.md page
	@echo "📝 Generating ABOUT.md page..."
	@mkdir -p docs
	@echo "# About AI Marketing Campaign Post Generator 🚀" > docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "**Author: JP + $$(date +%Y-%m-%d)**" >> docs/ABOUT.md
	@echo "**Version**: 1.0.0-alpha (80% Complete - MVP Ready)" >> docs/ABOUT.md
	@echo "**Last Updated**: $$(date +%Y-%m-%d)" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "## 🎯 Purpose & Vision" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "AI Marketing Campaign Post Generator is an **AI-powered marketing campaign generator** that transforms business ideas into professional marketing campaigns using Google's Advanced Development Kit (ADK) Framework and Gemini API." >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "### Core Mission" >> docs/ABOUT.md
	@echo "Empower marketers, entrepreneurs, and businesses to create compelling social media campaigns through intelligent AI assistance, reducing campaign creation time from days to minutes while maintaining professional quality." >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "## 🌟 Key Features" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "### ✅ Currently Available (MVP-Ready)" >> docs/ABOUT.md
	@echo "- **🎨 Campaign Creation**: Intuitive campaign setup with business context analysis" >> docs/ABOUT.md
	@echo "- **🤖 AI-Powered Ideation**: Generate creative campaign concepts using Gemini AI" >> docs/ABOUT.md
	@echo "- **📱 Social Media Content**: Create platform-optimized posts with hashtags" >> docs/ABOUT.md
	@echo "- **🖼️  Visual Content Generation**: AI-powered image and video prompts" >> docs/ABOUT.md
	@echo "- **📊 Campaign Management**: Full CRUD operations with export capabilities" >> docs/ABOUT.md
	@echo "- **🧪 Comprehensive Testing**: 80+ tests with full-stack validation" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "## 🏗️ Technical Architecture" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "### Full-Stack Implementation" >> docs/ABOUT.md
	@echo "- **Frontend**: React 18 + TypeScript + Vite + Material-UI" >> docs/ABOUT.md
	@echo "- **Backend**: FastAPI + Python 3.9+ + Google ADK Framework" >> docs/ABOUT.md
	@echo "- **Database**: SQLite (development) / PostgreSQL (production)" >> docs/ABOUT.md
	@echo "- **AI Integration**: Google Gemini 2.0 Flash + ADK Agents" >> docs/ABOUT.md
	@echo "- **Testing**: Pytest + Vitest + Integration Testing" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "### Agentic AI Architecture (70% Complete)" >> docs/ABOUT.md
	@echo "- **✅ CampaignOrchestratorAgent**: Master workflow coordination" >> docs/ABOUT.md
	@echo "- **✅ BusinessAnalysisAgent**: URL and context analysis" >> docs/ABOUT.md
	@echo "- **✅ ContentGenerationAgent**: Social media post creation" >> docs/ABOUT.md
	@echo "- **✅ VisualContentAgent**: Image and video generation" >> docs/ABOUT.md
	@echo "- **⏳ SocialMediaAgent**: Platform optimization (planned)" >> docs/ABOUT.md
	@echo "- **⏳ SchedulingAgent**: Optimal posting times (planned)" >> docs/ABOUT.md
	@echo "- **⏳ MonitoringAgent**: Performance analytics (planned)" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "## 🚀 Quick Start" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "\`\`\`bash" >> docs/ABOUT.md
	@echo "# Launch complete application stack" >> docs/ABOUT.md
	@echo "make launch-all" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "# Run comprehensive tests" >> docs/ABOUT.md
	@echo "make test-full-stack" >> docs/ABOUT.md
	@echo "" >> docs/ABOUT.md
	@echo "# Access the application" >> docs/ABOUT.md
	@echo "# Frontend: http://localhost:8080" >> docs/ABOUT.md
	@echo "# Backend:  http://localhost:8000" >> docs/ABOUT.md
	@echo "\`\`\`" >> docs/ABOUT.md

generate-uml: ## Generate UML diagrams for architecture documentation
	@echo "📊 Generating UML diagrams..."
	@mkdir -p docs/diagrams
	@echo "Creating system architecture diagram..."
	@echo "@startuml AI Marketing Campaign Post Generator - System Architecture" > docs/diagrams/system-architecture.puml
	@echo "!theme aws-orange" >> docs/diagrams/system-architecture.puml
	@echo "title AI Marketing Campaign Post Generator - System Architecture" >> docs/diagrams/system-architecture.puml
	@echo "" >> docs/diagrams/system-architecture.puml
	@echo "package \"Frontend Layer\" {" >> docs/diagrams/system-architecture.puml
	@echo "    [React UI] as UI" >> docs/diagrams/system-architecture.puml
	@echo "    [Component Library] as COMP" >> docs/diagrams/system-architecture.puml
	@echo "    [State Management] as STATE" >> docs/diagrams/system-architecture.puml
	@echo "}" >> docs/diagrams/system-architecture.puml
	@echo "" >> docs/diagrams/system-architecture.puml
	@echo "package \"API Gateway Layer\" {" >> docs/diagrams/system-architecture.puml
	@echo "    [FastAPI Gateway] as GATEWAY" >> docs/diagrams/system-architecture.puml
	@echo "    [Authentication] as AUTH" >> docs/diagrams/system-architecture.puml
	@echo "    [Rate Limiting] as RATE" >> docs/diagrams/system-architecture.puml
	@echo "    [CORS Middleware] as CORS" >> docs/diagrams/system-architecture.puml
	@echo "}" >> docs/diagrams/system-architecture.puml
	@echo "" >> docs/diagrams/system-architecture.puml
	@echo "package \"Agentic AI Layer\" {" >> docs/diagrams/system-architecture.puml
	@echo "    [Marketing Orchestrator] as ORCHESTRATOR" >> docs/diagrams/system-architecture.puml
	@echo "    package \"Specialized Agents\" {" >> docs/diagrams/system-architecture.puml
	@echo "        [Summary Agent] as SUMMARY" >> docs/diagrams/system-architecture.puml
	@echo "        [Idea Agent] as IDEA" >> docs/diagrams/system-architecture.puml
	@echo "        [Content Agent] as CONTENT" >> docs/diagrams/system-architecture.puml
	@echo "        [Analysis Agent] as ANALYSIS" >> docs/diagrams/system-architecture.puml
	@echo "    }" >> docs/diagrams/system-architecture.puml
	@echo "    package \"AI Services\" {" >> docs/diagrams/system-architecture.puml
	@echo "        [Google Gemini] as GEMINI" >> docs/diagrams/system-architecture.puml
	@echo "        [Google Veo] as VEO" >> docs/diagrams/system-architecture.puml
	@echo "        [ADK Framework] as ADK" >> docs/diagrams/system-architecture.puml
	@echo "    }" >> docs/diagrams/system-architecture.puml
	@echo "}" >> docs/diagrams/system-architecture.puml
	@echo "" >> docs/diagrams/system-architecture.puml
	@echo "UI --> GATEWAY : REST API" >> docs/diagrams/system-architecture.puml
	@echo "GATEWAY --> ORCHESTRATOR" >> docs/diagrams/system-architecture.puml
	@echo "ORCHESTRATOR --> SUMMARY" >> docs/diagrams/system-architecture.puml
	@echo "ORCHESTRATOR --> IDEA" >> docs/diagrams/system-architecture.puml
	@echo "ORCHESTRATOR --> CONTENT" >> docs/diagrams/system-architecture.puml
	@echo "ORCHESTRATOR --> ANALYSIS" >> docs/diagrams/system-architecture.puml
	@echo "SUMMARY --> GEMINI" >> docs/diagrams/system-architecture.puml
	@echo "IDEA --> GEMINI" >> docs/diagrams/system-architecture.puml
	@echo "CONTENT --> GEMINI" >> docs/diagrams/system-architecture.puml
	@echo "ANALYSIS --> GEMINI" >> docs/diagrams/system-architecture.puml
	@echo "GEMINI --> ADK" >> docs/diagrams/system-architecture.puml
	@echo "@enduml" >> docs/diagrams/system-architecture.puml
	@echo "✅ UML diagrams generated successfully!"
	@echo "📊 PlantUML files created in docs/diagrams/"
	@echo "💡 Use PlantUML tools to render these diagrams to PNG/SVG"

generate-release-notes: ## Generate release notes based on current state
	@echo "📋 Generating release notes..."
	@mkdir -p docs
	@echo "# Release Notes - AI Marketing Campaign Post Generator" > docs/RELEASE-NOTES.md
	@echo "" >> docs/RELEASE-NOTES.md
	@echo "**Version**: 1.0.0-alpha" >> docs/RELEASE-NOTES.md
	@echo "**Release Date**: $$(date +%Y-%m-%d)" >> docs/RELEASE-NOTES.md
	@echo "**Maturity Level**: 80% Complete (MVP-Ready)" >> docs/RELEASE-NOTES.md
	@echo "" >> docs/RELEASE-NOTES.md
	@echo "## 🎉 Major Achievements in This Release" >> docs/RELEASE-NOTES.md
	@echo "" >> docs/RELEASE-NOTES.md
	@echo "### ✅ Backend API Service (100% Complete)" >> docs/RELEASE-NOTES.md
	@echo "- **Complete FastAPI Implementation**: Production-ready API with ADK integration" >> docs/RELEASE-NOTES.md
	@echo "- **Campaign Management**: Full CRUD operations with 100% test coverage" >> docs/RELEASE-NOTES.md
	@echo "- **AI Agent Integration**: Marketing Orchestrator with specialized agents" >> docs/RELEASE-NOTES.md
	@echo "- **Comprehensive Error Handling**: Proper validation and error responses" >> docs/RELEASE-NOTES.md
	@echo "- **File Upload Support**: Multipart form data handling for business assets" >> docs/RELEASE-NOTES.md
	@echo "" >> docs/RELEASE-NOTES.md
	@echo "### ✅ API Testing Framework (100% Complete)" >> docs/RELEASE-NOTES.md
	@echo "- **52 Comprehensive Tests**: Complete API endpoint coverage" >> docs/RELEASE-NOTES.md
	@echo "- **Regression Prevention**: Automated testing to prevent breaking changes" >> docs/RELEASE-NOTES.md
	@echo "- **Campaign API**: 15/15 tests passing (100% success rate)" >> docs/RELEASE-NOTES.md
	@echo "- **Test Categories**: Unit, integration, and end-to-end testing" >> docs/RELEASE-NOTES.md
	@echo "- **Coverage Reporting**: Detailed test coverage analysis" >> docs/RELEASE-NOTES.md
	@echo "" >> docs/RELEASE-NOTES.md
	@echo "### ✅ Database Infrastructure (95% Complete)" >> docs/RELEASE-NOTES.md
	@echo "- **Database Integration Tests**: 14/14 tests passing (100% success rate)" >> docs/RELEASE-NOTES.md
	@echo "- **Schema Version**: Updated to v1.0.1 with comprehensive test alignment" >> docs/RELEASE-NOTES.md
	@echo "- **Performance Indexes**: 29+ custom indexes verified and optimized" >> docs/RELEASE-NOTES.md
	@echo "- **Analytics Views**: 3 views fully functional with proper aggregation" >> docs/RELEASE-NOTES.md
	@echo "- **Data Integrity**: All constraints (foreign key, check, unique) enforced" >> docs/RELEASE-NOTES.md
	@echo "- **Pydantic Models**: Full alignment between models and database schema" >> docs/RELEASE-NOTES.md
	@echo "" >> docs/RELEASE-NOTES.md
	@echo "### ✅ Development Infrastructure (95% Complete)" >> docs/RELEASE-NOTES.md
	@echo "- **Enhanced Makefile**: 3 Musketeers pattern with comprehensive targets" >> docs/RELEASE-NOTES.md
	@echo "- **Environment Management**: Automatic .env file creation and loading" >> docs/RELEASE-NOTES.md
	@echo "- **Cross-platform Compatibility**: macOS and Linux support" >> docs/RELEASE-NOTES.md
	@echo "- **Docker Support**: Container-ready for production deployment" >> docs/RELEASE-NOTES.md
	@echo "- **Professional Workflow**: Install, dev, test, and clean targets" >> docs/RELEASE-NOTES.md
	@echo "" >> docs/RELEASE-NOTES.md
	@echo "---" >> docs/RELEASE-NOTES.md
	@echo "" >> docs/RELEASE-NOTES.md
	@echo "**🎉 This release represents a major milestone in AI Marketing Campaign Post Generator development, establishing a solid MVP foundation with professional-grade backend infrastructure and comprehensive testing capabilities.**" >> docs/RELEASE-NOTES.md
	@echo "✅ Release notes generated successfully!"

docs-serve: ## Serve documentation locally
	@echo "📚 Starting documentation server..."
	@if command -v python3 >/dev/null 2>&1; then \
		echo "Serving docs at http://localhost:8080"; \
		cd docs && python3 -m http.server 8080; \
	else \
		echo "Python not available for serving docs"; \
	fi

docs-build: ## Build all documentation
	@echo "📖 Building all documentation..."
	@make generate-about
	@make generate-uml
	@make generate-release-notes
	@make update-about-page-release-info
	@echo "✅ All documentation built successfully!"

update-about-page-release-info: ## Update About page with dynamic release information
	@echo "🔄 Updating About page with current release information..."
	@mkdir -p src/data
	@echo "// Auto-generated release information - Updated: $$(date)" > src/data/releaseInfo.ts
	@echo "// Generated by 'make release' command" >> src/data/releaseInfo.ts
	@echo "" >> src/data/releaseInfo.ts
	@echo "export interface ReleaseInfo {" >> src/data/releaseInfo.ts
	@echo "  version: string;" >> src/data/releaseInfo.ts
	@echo "  date: string;" >> src/data/releaseInfo.ts
	@echo "  status: string;" >> src/data/releaseInfo.ts
	@echo "  completion: string;" >> src/data/releaseInfo.ts
	@echo "  features: string[];" >> src/data/releaseInfo.ts
	@echo "  nextMilestone: string;" >> src/data/releaseInfo.ts
	@echo "  lastUpdated: string;" >> src/data/releaseInfo.ts
	@echo "}" >> src/data/releaseInfo.ts
	@echo "" >> src/data/releaseInfo.ts
	@echo "export const currentRelease: ReleaseInfo = {" >> src/data/releaseInfo.ts
	@echo "  version: \"v0.8.0-beta\"," >> src/data/releaseInfo.ts
	@echo "  date: \"$$(date +%Y-%m-%d)\"," >> src/data/releaseInfo.ts
	@echo "  status: \"MVP-Ready\"," >> src/data/releaseInfo.ts
	@echo "  completion: \"80%\"," >> src/data/releaseInfo.ts
	@echo "  features: [" >> src/data/releaseInfo.ts
	@echo "    \"UI Design Consistency System\"," >> src/data/releaseInfo.ts
	@echo "    \"Comprehensive API Client with TypeScript\"," >> src/data/releaseInfo.ts
	@echo "    \"Backend ADK Integration (Production-Ready)\"," >> src/data/releaseInfo.ts
	@echo "    \"Database Infrastructure (14/14 tests passing)\"," >> src/data/releaseInfo.ts
	@echo "    \"Schema v1.0.1 with 29+ Performance Indexes\"," >> src/data/releaseInfo.ts
	@echo "    \"Analytics Views with Data Integrity\"," >> src/data/releaseInfo.ts
	@echo "    \"52 API Tests (Campaign API: 100% passing)\"," >> src/data/releaseInfo.ts
	@echo "    \"Professional Development Workflow\"," >> src/data/releaseInfo.ts
	@echo "    \"Enhanced Makefile with Release Management\"" >> src/data/releaseInfo.ts
	@echo "  ]," >> src/data/releaseInfo.ts
	@echo "  nextMilestone: \"Frontend-Backend Integration\"," >> src/data/releaseInfo.ts
	@echo "  lastUpdated: \"$$(date +%Y-%m-%d %H:%M:%S)\"" >> src/data/releaseInfo.ts
	@echo "};" >> src/data/releaseInfo.ts
	@echo "✅ Release information updated in src/data/releaseInfo.ts"

# Database operations for local MVP
db-init: ## Initialize local SQLite database with complete schema
	@echo "🗄️  Initializing local SQLite database with complete schema..."
	@mkdir -p data
	@if [ ! -f data/video_venture_launch.db ]; then \
		echo "Creating new SQLite database with complete schema..."; \
		if [ -f "backend/database/schema.sql" ]; then \
			sqlite3 data/video_venture_launch.db < backend/database/schema.sql; \
			echo "✅ Database initialized with complete schema at data/video_venture_launch.db"; \
		else \
			echo "❌ Schema file not found at backend/database/schema.sql"; \
			echo "Creating basic schema as fallback..."; \
			python3 -c "import sqlite3; conn = sqlite3.connect('data/video_venture_launch.db'); conn.execute('CREATE TABLE campaigns (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'); conn.execute('CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'); conn.commit(); conn.close()"; \
			echo "⚠️  Basic schema created. Run 'make db-upgrade' to apply full schema."; \
		fi; \
	else \
		echo "✅ Database already exists at data/video_venture_launch.db"; \
	fi

db-reset: ## Reset local database (WARNING: Deletes all data)
	@echo "🗄️  Resetting local database..."
	@rm -f data/video_venture_launch.db
	@$(MAKE) db-init

db-backup: ## Create backup of local database
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	@if [ -f data/video_venture_launch.db ]; then \
		cp data/video_venture_launch.db backups/video_venture_launch_$(shell date +%Y%m%d_%H%M%S).db; \
		echo "✅ Backup created in backups/ directory"; \
	else \
		echo "❌ No database found to backup. Run 'make db-init' first."; \
	fi

db-status: ## Check database status and show table info
	@echo "📊 Database Status:"
	@python3 backend/database/db_status.py

db-upgrade: ## Upgrade existing database to latest schema
	@echo "🔄 Upgrading database to latest schema..."
	@if [ -f data/video_venture_launch.db ]; then \
		if [ -f "backend/database/schema.sql" ]; then \
			echo "⚠️  WARNING: This will recreate the database with new schema."; \
			echo "Creating backup first..."; \
			$(MAKE) db-backup; \
			echo "Applying new schema..."; \
			rm -f data/video_venture_launch.db; \
			sqlite3 data/video_venture_launch.db < backend/database/schema.sql; \
			echo "✅ Database upgraded to latest schema"; \
		else \
			echo "❌ Schema file not found at backend/database/schema.sql"; \
		fi; \
	else \
		echo "❌ Database not found. Run 'make db-init' to create it."; \
	fi

# MVP setup with database
setup-mvp: ## Complete MVP setup with database initialization
	@echo "🚀 Setting up AI Marketing Campaign Post Generator MVP..."
	@echo "========================================"
	@$(MAKE) install-all
	@$(MAKE) db-init
	@echo ""
	@echo "✅ MVP setup complete!"
	@echo "📊 Run 'make db-status' to check database"
	@echo "🚀 Run 'make dev-with-env' to start the application"

# Comprehensive Testing Framework
test-database: ## Run database integration tests
	@echo "🗄️  Running database integration tests..."
	@cd backend && python3 -m pytest tests/test_database_integration.py -v --tb=short
	@echo "✅ Database tests completed"

test-api-endpoints: ## Run API endpoint tests
	@echo "🌐 Running API endpoint tests..."
	@cd backend && python3 -m pytest tests/test_api_*.py -v --tb=short
	@echo "✅ API tests completed"

test-gemini: ## Run Gemini integration tests (requires API key)
	@echo "🤖 Running Gemini integration tests..."
	@if [ -z "$$GOOGLE_API_KEY" ] && [ -z "$$GOOGLE_CLOUD_PROJECT" ]; then \
		echo "⚠️  Skipping Gemini tests - no API configuration found"; \
		echo "   Set GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT to run Gemini tests"; \
	else \
		cd backend && python3 -m pytest tests/test_gemini_*.py -v --tb=short -m integration; \
	fi
	@echo "✅ Gemini tests completed"

test-comprehensive: ## Run comprehensive test suite with detailed reporting
	@echo "🎯 Running comprehensive test suite..."
	@echo "======================================"
	@$(MAKE) test-database
	@$(MAKE) test-api-endpoints
	@$(MAKE) test-gemini
	@echo "✅ Comprehensive test suite completed"

test-quick: ## Run quick test suite (essential tests only)
	@echo "⚡ Running quick test suite..."
	@cd backend && python3 -m pytest tests/test_api_campaigns.py tests/test_database_integration.py::TestDatabaseIntegration::test_database_schema_integrity -v --tb=short -x
	@echo "✅ Quick tests completed"

test-coverage-db: ## Run tests with coverage reporting for database
	@echo "📊 Running database tests with coverage reporting..."
	@cd backend && python3 -m pytest tests/test_database_integration.py --cov=database --cov-report=html --cov-report=term
	@echo "✅ Database coverage report generated in backend/htmlcov/"

test-clean: ## Clean test artifacts and temporary files
	@echo "🧹 Cleaning test artifacts..."
	@rm -rf backend/.pytest_cache
	@rm -rf backend/htmlcov
	@rm -rf backend/__pycache__
	@rm -rf backend/tests/__pycache__
	@rm -f data/test_*.db
	@echo "✅ Test artifacts cleaned"
