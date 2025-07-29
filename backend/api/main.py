"""
FILENAME: main.py
DESCRIPTION/PURPOSE: FastAPI application entry point for AI Marketing Campaign Post Generator backend
Author: JP + 2025-06-15

This module provides the main FastAPI application with ADK agent integration,
following Google ADK samples best practices for sequential agent workflows.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import InMemoryRunner
from google.adk.telemetry import tracer

from .routes.campaigns import router as campaigns_router
from .routes.content import router as content_router
from .routes.analysis import router as analysis_router
from .routes.enhanced_campaigns import router as enhanced_campaigns_router

from .routes.social_auth import router as social_auth_router
from .routes.social_posts import router as social_posts_router

from .routes.test_endpoints import router as test_router

from .models import CampaignRequest, CampaignResponse, ErrorResponse
from agents.marketing_orchestrator import create_marketing_orchestrator_agent

# Configure comprehensive logging
from config.logging import setup_logging, get_logger
logger = setup_logging()

# Global agent instance
marketing_agent: SequentialAgent = None
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for ADK agent initialization."""
    global marketing_agent
    
    logger.info("=== AI Marketing Campaign Post Generator Backend Startup ===")
    logger.debug(f"Environment variables loaded from: {os.path.join(os.path.dirname(__file__), '../.env')}")
    
    # Log environment status
    gemini_key = os.getenv("GEMINI_API_KEY")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "not set")
    
    logger.info(f"Configuration:")
    logger.info(f"  - Log Level: {log_level}")
    logger.info(f"  - Log File: {log_file}")
    logger.info(f"  - GEMINI_API_KEY: {'SET' if gemini_key else 'NOT SET'}")
    
    if gemini_key:
        logger.debug(f"GEMINI_API_KEY length: {len(gemini_key)} characters")
    else:
        logger.warning("GEMINI_API_KEY not set - AI functionality will be limited")
    
    # Initialize the marketing orchestrator agent
    logger.debug("Initializing marketing orchestrator agent...")
    try:
        marketing_agent = await create_marketing_orchestrator_agent()
        logger.info("✅ Marketing orchestrator agent initialized successfully")
        logger.debug(f"Agent details: {type(marketing_agent).__name__}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize marketing agent: {e}")
        logger.exception("Full exception details:")
        raise
    
    logger.info("=== Backend startup complete ===")
    
    yield
    
    logger.info("=== AI Marketing Campaign Post Generator Backend Shutdown ===")
    logger.debug("Cleaning up resources...")
    logger.info("✅ Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="AI Marketing Campaign Post Generator API",
    description="Agentic AI Marketing Campaign Manager - Backend API",
    version="v1.0.1alpha-blog-post",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vite dev server
        "http://localhost:8081",  # Alternative Vite port
        "http://localhost:8096",  # Current Vite dev server port
        "https://Agentic-Marketing-Campaign-Generator.web.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security (allow test hosts)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "testserver", "*.web.app", "*.run.app"]
)

# Include API routes
app.include_router(
    campaigns_router,
    prefix="/api/v1/campaigns",
    tags=["Campaign Management"]
)
app.include_router(
    content_router,
    prefix="/api/v1/content",
    tags=["Content Generation"]
)
app.include_router(
    analysis_router,
    prefix="/api/v1/analysis",
    tags=["Business Analysis"]
)
# Include enhanced campaigns V2 router
app.include_router(
    enhanced_campaigns_router,
    tags=["Enhanced Campaigns V2"]
)
app.include_router(
    social_auth_router,
    prefix="/api/v1/auth/social",
    tags=["Social Media Authentication"]
)
app.include_router(
    social_posts_router,
    prefix="/api/v1/posts",
    tags=["Social Media Publishing"]
)
app.include_router(
    test_router,
    prefix="/api/v1",
    tags=["Testing"]
)

@app.get("/", response_model=dict)
async def root():
    """Root endpoint providing API information."""
    return {
        "name": "AI Marketing Campaign Post Generator API",
        "version": "v1.0.1alpha-blog-post",
        "description": "Agentic AI Marketing Campaign Manager",
        "framework": "Google ADK",
        "author": "Jaroslav Pantsjoha",
        "docs": "/api/docs",
        "health": "/health"
    }

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint for monitoring."""
    logger.debug("Health check endpoint called")
    
    agent_initialized = marketing_agent is not None
    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    
    logger.debug(f"Health check status: agent_initialized={agent_initialized}, gemini_configured={gemini_configured}")
    
    health_status = {
        "status": "healthy",
        "agent_initialized": agent_initialized,
        "gemini_key_configured": gemini_configured,
        "services": {
            "session_service": "in_memory",
            "artifact_service": "in_memory"
        }
    }
    
    logger.debug(f"Returning health status: {health_status}")
    return health_status

@app.get("/api/v1/agent/status", response_model=dict)
async def agent_status():
    """Get the status of the marketing orchestrator agent."""
    if not marketing_agent:
        raise HTTPException(status_code=503, detail="Marketing agent not initialized")
    
    return {
        "agent_name": marketing_agent.name,
        "agent_type": type(marketing_agent).__name__,
        "sub_agents": [agent.name for agent in marketing_agent.sub_agents],
        "description": marketing_agent.description,
        "status": "ready"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper error response format."""
    from fastapi.responses import JSONResponse
    
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url}")
    logger.debug(f"Request details: Method={request.method}, Headers={dict(request.headers)}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with proper logging."""
    from fastapi.responses import JSONResponse
    
    logger.error(f"❌ Unhandled exception: {exc}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Headers: {dict(request.headers)}")
    logger.exception("Full exception traceback:")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 