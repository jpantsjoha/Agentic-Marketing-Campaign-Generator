"""
FILENAME: enhanced_campaigns.py
DESCRIPTION/PURPOSE: Enhanced campaign API endpoints using ADK v1.8+ architecture
Author: JP + Claude Code + 2025-07-29

This module provides API endpoints for the enhanced campaign system with:
- ADK v1.8+ streaming capabilities
- A2A messaging integration
- Persistent campaign context
- Real-time progress updates
- Zero fidelity loss data handling
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.responses import StreamingResponse as StarletteStreamingResponse
from pydantic import BaseModel, Field
import uuid

try:
    from ...agents.enhanced_marketing_orchestrator_v2 import (
        EnhancedMarketingOrchestrator,
        create_enhanced_marketing_orchestrator
    )
    from ...models.campaign_context import (
        CampaignContext,
        GenerationEventType,
        SocialPlatform
    )
    from ...messaging.a2a_messaging import get_message_bus, initialize_message_bus
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    backend_path = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(backend_path))
    
    from agents.enhanced_marketing_orchestrator_v2 import (
        EnhancedMarketingOrchestrator,
        create_enhanced_marketing_orchestrator
    )
    from models.campaign_context import (
        CampaignContext,
        GenerationEventType,
        SocialPlatform
    )
    from messaging.a2a_messaging import get_message_bus, initialize_message_bus

logger = logging.getLogger(__name__)

# --- Request/Response Models ---

class CampaignRequest(BaseModel):
    """Request model for campaign creation"""
    campaign_name: Optional[str] = Field(None, description="Campaign name")
    campaign_description: Optional[str] = Field(None, description="Campaign description")
    business_url: Optional[str] = Field(None, description="Business website URL")
    business_description: Optional[str] = Field(None, description="Business description")
    target_platforms: List[SocialPlatform] = Field(default_factory=list, description="Target social platforms")
    campaign_objectives: List[str] = Field(default_factory=list, description="Campaign objectives")

class CampaignResponse(BaseModel):
    """Response model for campaign operations"""
    campaign_id: str
    status: str
    message: str
    completion_percentage: Optional[float] = None
    data: Optional[Dict[str, Any]] = None

class CampaignStatusResponse(BaseModel):
    """Response model for campaign status"""
    campaign_id: str
    completion_percentage: float
    completed_stages: List[str]
    last_updated: str
    version: int
    active_agents: List[str]
    generation_history: List[Dict[str, Any]]

class CampaignListResponse(BaseModel):
    """Response model for campaign listing"""
    campaigns: List[str]
    total_count: int
    memory_stats: Dict[str, Any]

# --- Global State ---

# Global orchestrator instance
_orchestrator: Optional[EnhancedMarketingOrchestrator] = None

async def get_orchestrator() -> EnhancedMarketingOrchestrator:
    """Dependency to get orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        # Initialize message bus
        await initialize_message_bus()
        
        # Create orchestrator
        _orchestrator = await create_enhanced_marketing_orchestrator()
        logger.info("✅ Enhanced orchestrator initialized for API")
    
    return _orchestrator

# --- Router Setup ---

router = APIRouter(prefix="/api/v2/campaigns", tags=["Enhanced Campaigns"])

# --- Endpoints ---

@router.post("/create", response_model=CampaignResponse)
async def create_enhanced_campaign(
    request: CampaignRequest,
    background_tasks: BackgroundTasks,
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """Create a new enhanced campaign with A2A coordination"""
    
    try:
        # Generate campaign ID
        campaign_id = f"campaign_{uuid.uuid4().hex[:12]}"
        
        # Prepare business input
        business_input = {
            "campaign_name": request.campaign_name,
            "description": request.campaign_description,
            "business_url": request.business_url,
            "business_description": request.business_description,
            "target_platforms": [p.value for p in request.target_platforms],
            "campaign_objectives": request.campaign_objectives
        }
        
        # Start campaign generation in background
        background_tasks.add_task(
            _generate_campaign_background,
            orchestrator,
            campaign_id,
            business_input
        )
        
        logger.info(f"🚀 Created enhanced campaign: {campaign_id}")
        
        return CampaignResponse(
            campaign_id=campaign_id,
            status="created",
            message="Campaign created and generation started",
            completion_percentage=0.0,
            data={"business_input": business_input}
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to create campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Campaign creation failed: {str(e)}")

async def _generate_campaign_background(
    orchestrator: EnhancedMarketingOrchestrator,
    campaign_id: str,
    business_input: Dict[str, Any]
):
    """Background task for campaign generation"""
    
    try:
        logger.info(f"🔄 Starting background generation for campaign: {campaign_id}")
        
        # Generate campaign
        final_context = await orchestrator.generate_campaign(campaign_id, business_input)
        
        logger.info(f"✅ Background generation complete for campaign: {campaign_id}")
        
    except Exception as e:
        logger.error(f"❌ Background generation failed for {campaign_id}: {e}")

@router.get("/{campaign_id}/status", response_model=CampaignStatusResponse)
async def get_campaign_status(
    campaign_id: str,
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """Get campaign status and progress"""
    
    try:
        status = await orchestrator.get_campaign_status(campaign_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return CampaignStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get campaign status: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.get("/{campaign_id}/context")
async def get_campaign_context(
    campaign_id: str,
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """Get full campaign context (for debugging)"""
    
    try:
        context = await orchestrator.memory_service.get_campaign_context(campaign_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Convert to dict for JSON response
        context_dict = context.model_dump()
        
        return {
            "campaign_id": campaign_id,
            "context": context_dict,
            "metadata": {
                "version": context.version,
                "last_updated": context.last_updated.isoformat(),
                "completion_percentage": context.get_completion_percentage()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get campaign context: {e}")
        raise HTTPException(status_code=500, detail=f"Context retrieval failed: {str(e)}")

@router.get("/list", response_model=CampaignListResponse)
async def list_campaigns(
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """List all campaigns with memory statistics"""
    
    try:
        # Get campaign list
        campaigns = await orchestrator.list_campaigns()
        
        # Get memory stats
        memory_stats = await orchestrator.get_memory_stats()
        
        return CampaignListResponse(
            campaigns=campaigns,
            total_count=len(campaigns),
            memory_stats=memory_stats
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to list campaigns: {e}")
        raise HTTPException(status_code=500, detail=f"Campaign listing failed: {str(e)}")

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """Delete campaign and its context"""
    
    try:
        success = await orchestrator.memory_service.delete_campaign_context(campaign_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return CampaignResponse(
            campaign_id=campaign_id,
            status="deleted",
            message="Campaign deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Campaign deletion failed: {str(e)}")

@router.get("/{campaign_id}/messages")
async def get_campaign_messages(
    campaign_id: str,
    limit: int = 50,
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """Get A2A messages for campaign"""
    
    try:
        message_bus = get_message_bus()
        messages = message_bus.get_message_history(campaign_id=campaign_id, limit=limit)
        
        # Convert messages to dict format
        message_data = []
        for message in messages:
            message_data.append({
                "message_id": message.message_id,
                "message_type": message.message_type.value,
                "sender": message.sender,
                "recipients": message.recipients,
                "timestamp": message.timestamp.isoformat(),
                "payload_summary": {
                    key: str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    for key, value in message.payload.items()
                },
                "delivered_to": message.delivered_to,
                "failed_deliveries": message.failed_deliveries,
                "response_received": message.response_received
            })
        
        return JSONResponse(content={
            "campaign_id": campaign_id,
            "messages": message_data,
            "total_messages": len(message_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get campaign messages: {e}")
        raise HTTPException(status_code=500, detail=f"Message retrieval failed: {str(e)}")

@router.get("/debug/memory-stats")
async def get_memory_stats(
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """Get detailed memory and message bus statistics"""
    
    try:
        stats = await orchestrator.get_memory_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get memory stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@router.post("/{campaign_id}/regenerate")
async def regenerate_campaign_stage(
    campaign_id: str,
    stage: GenerationEventType,
    background_tasks: BackgroundTasks,
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """Regenerate a specific campaign stage"""
    
    try:
        context = await orchestrator.memory_service.get_campaign_context(campaign_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Start regeneration in background
        background_tasks.add_task(
            _regenerate_stage_background,
            orchestrator,
            campaign_id,
            stage
        )
        
        return CampaignResponse(
            campaign_id=campaign_id,
            status="regenerating",
            message=f"Regenerating {stage.value} stage",
            data={"stage": stage.value}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to regenerate campaign stage: {e}")
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")

async def _regenerate_stage_background(
    orchestrator: EnhancedMarketingOrchestrator,
    campaign_id: str,
    stage: GenerationEventType
):
    """Background task for stage regeneration"""
    
    try:
        logger.info(f"🔄 Regenerating {stage.value} for campaign: {campaign_id}")
        
        context = await orchestrator.memory_service.get_campaign_context(campaign_id)
        
        if stage == GenerationEventType.BUSINESS_ANALYSIS:
            await orchestrator.business_agent.run(context)
        elif stage == GenerationEventType.CONTENT_STRATEGY:
            await orchestrator.content_agent.run(context)
        
        logger.info(f"✅ Regeneration complete for {stage.value}: {campaign_id}")
        
    except Exception as e:
        logger.error(f"❌ Regeneration failed for {campaign_id} {stage.value}: {e}")

# Health check for enhanced system
@router.get("/health")
async def enhanced_system_health():
    """Health check for enhanced campaign system"""
    
    try:
        # Check if orchestrator is available
        orchestrator = await get_orchestrator()
        
        # Get system stats
        stats = await orchestrator.get_memory_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "ADK v1.8+ Enhanced",
            "features": [
                "A2A messaging",
                "Persistent memory",
                "Structured context",
                "Event-driven coordination"
            ],
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.post("/{campaign_id}/stream")
async def stream_campaign_generation(
    campaign_id: str,
    request: CampaignRequest,
    orchestrator: EnhancedMarketingOrchestrator = Depends(get_orchestrator)
):
    """Stream real-time campaign generation updates using ADK v1.8+ capabilities"""
    
    async def generate_stream():
        """Generate Server-Sent Events stream"""
        try:
            # Prepare campaign request with campaign_id
            campaign_request = request.model_dump()
            campaign_request["campaign_id"] = campaign_id
            
            async for update in orchestrator.stream_campaign_generation(campaign_request):
                # Format as Server-Sent Events (update is already JSON string)
                yield f"data: {update}\n\n"
                
                # Add small delay to ensure proper streaming
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            import json
            error_update = json.dumps({
                "type": "error",
                "message": f"Streaming failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
            yield f"data: {error_update}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

@router.get("/stream/health")
async def stream_health_check():
    """Health check for streaming capabilities"""
    return {
        "streaming_enabled": True,
        "adk_version": "1.8.0",
        "features": [
            "Real-time updates",
            "Server-Sent Events",
            "Campaign progress streaming",
            "Error handling"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

# Export router
__all__ = ["router"]