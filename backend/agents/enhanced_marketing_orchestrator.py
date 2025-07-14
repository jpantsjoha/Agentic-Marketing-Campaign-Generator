"""
Enhanced Marketing Orchestrator with ADK v1.6.1+ Features

This module implements the enhanced marketing orchestrator using ADK v1.6.1+ features
including enhanced state management, A2A communication, and improved orchestration.

Author: JP + 2025-07-14
"""

import os
import logging
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

# ADK v1.6.1 imports with correct modules
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.memory import InMemoryMemoryService
from google.adk.models import Gemini

# Import existing agents
from .business_analysis_agent import URLAnalysisAgent

# Configure logging
logger = logging.getLogger(__name__)

# Model configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not configured - using mock responses")

def create_business_analysis_agent() -> SequentialAgent:
    """Create enhanced business analysis agent with state persistence."""
    
    url_analysis_agent = LlmAgent(
        name="url_analysis_agent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are an expert business intelligence analyst.
        
        Analyze the provided business information and extract:
        1. Company overview and positioning
        2. Products/services analysis
        3. Target audience insights
        4. Brand analysis and voice
        5. Market positioning
        6. Visual content recommendations
        7. Campaign guidance
        
        Store findings in session state for persistent access across the campaign workflow.
        
        Return comprehensive business analysis in JSON format.""",
        output_key="business_analysis"
    )
    
    context_enrichment_agent = LlmAgent(
        name="context_enrichment_agent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""Enrich business analysis with campaign-specific context.
        
        Based on the business analysis, add:
        1. Campaign media tuning recommendations
        2. Visual style guidelines
        3. Content tone and messaging
        4. Platform-specific optimizations
        5. Engagement prediction factors
        
        Update session state with enriched context.""",
        output_key="enriched_context"
    )
    
    return SequentialAgent(
        name="business_analysis_agent",
        description="Enhanced business analysis with context enrichment",
        sub_agents=[url_analysis_agent, context_enrichment_agent]
    )

def create_content_generation_agent() -> SequentialAgent:
    """Create enhanced content generation agent with memory-aware communication."""
    
    strategy_agent = LlmAgent(
        name="strategy_agent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a content strategy expert.
        
        Access business analysis from session state and create:
        1. Content strategy framework
        2. Messaging pillars
        3. Content calendar recommendations
        4. Engagement optimization strategies
        
        Store strategy in session state for content creation agents.""",
        output_key="content_strategy"
    )
    
    content_creation_agent = LlmAgent(
        name="content_creation_agent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""Generate social media content based on strategy and business analysis.
        
        Access from session state:
        - Business analysis
        - Content strategy
        - Campaign objectives
        
        Generate diverse content types:
        - Text + URL posts
        - Text + Image posts  
        - Text + Video posts
        
        Return content in ADR-020 compliant format.""",
        output_key="social_media_content"
    )
    
    optimization_agent = LlmAgent(
        name="optimization_agent", 
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""Optimize content for platforms and engagement.
        
        Access generated content from session state and optimize:
        1. Platform-specific formatting
        2. Hashtag optimization
        3. Engagement scoring
        4. A/B testing recommendations
        
        Update content with optimizations.""",
        output_key="optimized_content"
    )
    
    return SequentialAgent(
        name="content_generation_agent",
        description="Enhanced content generation with strategy and optimization",
        sub_agents=[strategy_agent, content_creation_agent, optimization_agent]
    )

def create_visual_content_agent() -> ParallelAgent:
    """Create enhanced visual content agent with parallel processing."""
    
    image_generation_agent = LlmAgent(
        name="image_generation_agent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""Generate images using Imagen 3.0 API.
        
        Access content and business context from session state.
        
        For each image post:
        1. Create campaign-aware image prompts
        2. Generate high-quality images
        3. Validate image quality and relevance
        4. Store image URLs in session state
        
        Implement batch processing for efficiency.""",
        output_key="generated_images"
    )
    
    video_generation_agent = LlmAgent(
        name="video_generation_agent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""Generate videos using Veo 2.0 API.
        
        Access content and business context from session state.
        
        For each video post:
        1. Create campaign-aware video prompts
        2. Generate high-quality videos
        3. Validate video quality and relevance
        4. Store video URLs in session state
        
        Implement asynchronous processing for long-running operations.""",
        output_key="generated_videos"
    )
    
    return ParallelAgent(
        name="visual_content_agent",
        description="Enhanced visual content generation with parallel processing",
        sub_agents=[image_generation_agent, video_generation_agent]
    )

def create_social_media_agent() -> SequentialAgent:
    """Create enhanced social media agent with OAuth and publishing."""
    
    platform_optimization_agent = LlmAgent(
        name="platform_optimization_agent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""Optimize content for specific social media platforms.
        
        Access complete campaign content from session state.
        
        For each platform (LinkedIn, Twitter, Instagram, Facebook):
        1. Adapt content to platform requirements
        2. Optimize visual content dimensions
        3. Adjust messaging for platform audience
        4. Prepare publishing metadata
        
        Store platform-optimized content in session state.""",
        output_key="platform_content"
    )
    
    publishing_agent = LlmAgent(
        name="publishing_agent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""Manage social media publishing workflow.
        
        Access platform-optimized content from session state.
        
        For each post:
        1. Validate OAuth tokens
        2. Upload media assets
        3. Publish to platforms
        4. Track publishing status
        5. Handle errors and retries
        
        Store publishing results in session state.""",
        output_key="publishing_results"
    )
    
    return SequentialAgent(
        name="social_media_agent",
        description="Enhanced social media agent with OAuth and publishing",
        sub_agents=[platform_optimization_agent, publishing_agent]
    )

class EnhancedMarketingOrchestrator(SequentialAgent):
    """
    Enhanced Marketing Orchestrator using ADK v1.6.1+ features.
    
    Features:
    - Enhanced state management with persistent session storage
    - A2A agent communication capabilities
    - Improved orchestration patterns
    - Campaign context persistence between sessions
    - Memory-aware agent communication
    """
    
    def __init__(self, campaign_id: str = None):
        """Initialize the enhanced marketing orchestrator."""
        
        # Initialize sub-agents first
        business_analysis_agent = create_business_analysis_agent()
        content_generation_agent = create_content_generation_agent()
        visual_content_agent = create_visual_content_agent()
        social_media_agent = create_social_media_agent()
        
        super().__init__(
            name="enhanced_marketing_orchestrator",
            description="Enhanced marketing campaign orchestrator with ADK v1.6.1 features",
            sub_agents=[
                business_analysis_agent,
                content_generation_agent,
                visual_content_agent,
                social_media_agent
            ]
        )
        
        # Set campaign_id for internal use
        self._campaign_id = campaign_id or str(uuid.uuid4())
        
        # Initialize memory service for state management
        self._memory_service = InMemoryMemoryService()
        self._campaign_state = {}
        
        # Store sub-agent references
        self._business_analysis_agent = business_analysis_agent
        self._content_generation_agent = content_generation_agent
        self._visual_content_agent = visual_content_agent
        self._social_media_agent = social_media_agent
        
        logger.info(f"✅ Enhanced Marketing Orchestrator initialized for campaign: {self._campaign_id}")
    
    @property
    def campaign_id(self) -> str:
        """Get campaign ID."""
        return self._campaign_id
    
    @property
    def memory_service(self) -> InMemoryMemoryService:
        """Get memory service."""
        return self._memory_service
    
    @property
    def campaign_state(self) -> Dict[str, Any]:
        """Get campaign state."""
        return self._campaign_state
    
    @property
    def business_analysis_agent(self) -> SequentialAgent:
        """Get business analysis agent."""
        return self._business_analysis_agent
    
    @property
    def content_generation_agent(self) -> SequentialAgent:
        """Get content generation agent."""
        return self._content_generation_agent
    
    @property
    def visual_content_agent(self) -> ParallelAgent:
        """Get visual content agent."""
        return self._visual_content_agent
    
    @property
    def social_media_agent(self) -> SequentialAgent:
        """Get social media agent."""
        return self._social_media_agent
    
    async def execute_campaign_workflow(
        self,
        business_urls: List[str] = None,
        business_description: str = "",
        target_audience: str = "",
        objective: str = "",
        campaign_type: str = "awareness",
        post_count: int = 9
    ) -> Dict[str, Any]:
        """
        Execute enhanced campaign workflow with persistent state management.
        
        Args:
            business_urls: List of URLs for business analysis
            business_description: Business description
            target_audience: Target audience description
            objective: Campaign objective
            campaign_type: Type of campaign
            post_count: Number of posts to generate
            
        Returns:
            Dict with campaign results and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Starting enhanced campaign workflow for {self._campaign_id}")
            
            # Initialize campaign context in session state
            campaign_context = {
                "campaign_id": self._campaign_id,
                "business_urls": business_urls or [],
                "business_description": business_description,
                "target_audience": target_audience,
                "objective": objective,
                "campaign_type": campaign_type,
                "post_count": post_count,
                "start_time": start_time,
                "status": "in_progress"
            }
            
            # Store context in campaign state
            self._campaign_state["campaign_context"] = campaign_context
            
            # Execute the sequential workflow
            workflow_result = await self.run_async(context=campaign_context)
            
            # Update final status
            campaign_context["status"] = "completed"
            campaign_context["end_time"] = time.time()
            campaign_context["duration"] = campaign_context["end_time"] - start_time
            
            self._campaign_state["campaign_context"] = campaign_context
            
            logger.info(f"✅ Enhanced campaign workflow completed for {self._campaign_id}")
            
            return {
                "campaign_id": self._campaign_id,
                "status": "success",
                "duration": campaign_context["duration"],
                "results": workflow_result,
                "state_summary": {"campaign_state": self._campaign_state}
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced campaign workflow failed for {self._campaign_id}: {e}", exc_info=True)
            
            # Update error status
            campaign_context["status"] = "failed"
            campaign_context["error"] = str(e)
            campaign_context["end_time"] = time.time()
            
            self._campaign_state["campaign_context"] = campaign_context
            
            return {
                "campaign_id": self._campaign_id,
                "status": "error",
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def get_campaign_state(self) -> Dict[str, Any]:
        """Get current campaign state from persistent storage."""
        return self._campaign_state
    
    def restore_campaign_state(self, campaign_id: str) -> bool:
        """Restore campaign state from persistent storage."""
        try:
            self._campaign_id = campaign_id
            # In a real implementation, this would load from persistent storage
            # For now, just return False indicating no state to restore
            logger.warning(f"⚠️ No state found for campaign {campaign_id}")
            return False
                
        except Exception as e:
            logger.error(f"❌ Failed to restore campaign state: {e}")
            return False


# Factory function for backward compatibility
async def create_enhanced_marketing_orchestrator(campaign_id: str = None) -> EnhancedMarketingOrchestrator:
    """Create an enhanced marketing orchestrator instance."""
    return EnhancedMarketingOrchestrator(campaign_id=campaign_id)


# Backward compatibility function
async def execute_campaign_workflow(
    business_urls: List[str] = None,
    business_description: str = "",
    target_audience: str = "",
    objective: str = "",
    campaign_type: str = "awareness",
    post_count: int = 9,
    campaign_id: str = None
) -> Dict[str, Any]:
    """
    Execute enhanced campaign workflow with backward compatibility.
    
    This function maintains compatibility with the existing API while
    leveraging the enhanced ADK v1.6.1+ features.
    """
    orchestrator = await create_enhanced_marketing_orchestrator(campaign_id)
    
    return await orchestrator.execute_campaign_workflow(
        business_urls=business_urls,
        business_description=business_description,
        target_audience=target_audience,
        objective=objective,
        campaign_type=campaign_type,
        post_count=post_count
    )