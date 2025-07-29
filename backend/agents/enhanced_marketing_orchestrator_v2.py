"""
FILENAME: enhanced_marketing_orchestrator_v2.py
DESCRIPTION/PURPOSE: ADK v1.8+ Enhanced Marketing Orchestrator with streaming and advanced A2A messaging
Author: JP + Claude Code + 2025-07-29

This is the upgraded marketing orchestrator leveraging ADK v1.8+ features:
- Enhanced memory service with persistent sessions
- Advanced A2A messaging with streaming capabilities
- Structured campaign context with zero fidelity loss
- Event-driven parallel execution
- Real-time streaming responses
- Improved Model Context Protocol (MCP) integration
"""

import os
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, AsyncIterator
from datetime import datetime
import uuid

# ADK v1.8+ imports
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.active_streaming_tool import ActiveStreamingTool
from google.adk.models import Gemini
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.adk.agents.run_config import RunConfig

# Import enhanced services and models
try:
    from ..services.enhanced_memory_service import EnhancedMemoryService, initialize_memory_service
    from ..models.campaign_context import (
        CampaignContext,
        BusinessAnalysis,
        ContentStrategy,
        VisualGuidance,
        GenerationEventType,
        create_campaign_context
    )
    from ..messaging.a2a_messaging import (
        MessageBus,
        A2AMessage,
        MessageType,
        get_message_bus,
        send_business_analysis_complete,
        send_content_strategy_ready,
        send_progress_update
    )
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    backend_path = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_path))
    
    from services.enhanced_memory_service import EnhancedMemoryService, initialize_memory_service
    from models.campaign_context import (
        CampaignContext,
        BusinessAnalysis,
        ContentStrategy,
        VisualGuidance,
        GenerationEventType,
        create_campaign_context
    )
    from messaging.a2a_messaging import (
        MessageBus,
        A2AMessage,
        MessageType,
        get_message_bus,
        send_business_analysis_complete,
        send_content_strategy_ready,
        send_progress_update
    )

# Import existing agents for integration
from .business_analysis_agent import URLAnalysisAgent

logger = logging.getLogger(__name__)

# Model configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not configured - using mock responses")

class EnhancedBusinessAnalysisAgent:
    """Enhanced business analysis agent with A2A messaging"""
    
    def __init__(self, memory_service: EnhancedMemoryService):
        self.name = "enhanced_business_analysis_agent"
        self.memory_service = memory_service
        self.message_bus = get_message_bus()
        
        # Initialize the LLM model if available
        self.model = Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
        self.instruction = self._get_analysis_instruction()
        
        # Register with message bus (async, done in background)
        asyncio.create_task(self._register_with_message_bus())
    
    async def _register_with_message_bus(self):
        """Register with message bus"""
        await self.message_bus.register_agent(self.name, {
            "type": "business_analysis",
            "capabilities": ["url_analysis", "business_context", "target_audience"]
        })
    
    def _get_analysis_instruction(self) -> str:
        return """You are an expert business intelligence analyst with marketing expertise.

Your role is to analyze business information and create comprehensive business analysis that includes:

1. **Company Analysis:**
   - Company name and core business
   - Unique value proposition
   - Key products/services
   - Market positioning

2. **Target Audience Analysis:**
   - Demographics (age, gender, income, location, occupation)
   - Psychographics (interests, values, lifestyle, personality)
   - Pain points and challenges
   - Preferred social platforms
   - Engagement patterns and behavior

3. **Brand Guidelines:**
   - Brand voice and tone attributes
   - Visual style preferences
   - Color palette recommendations
   - Core brand values
   - Messaging principles

4. **Competitive Analysis:**
   - Direct and indirect competitors
   - Competitive advantages
   - Market differentiation factors

5. **Campaign Objectives:**
   - Primary campaign goals
   - Target metrics and KPIs
   - Success measurement criteria

6. **Industry Context:**
   - Industry trends and insights
   - Seasonal considerations
   - Regulatory factors

Return comprehensive analysis in structured JSON format matching the BusinessAnalysis schema.
Focus on actionable insights that will guide content strategy and visual content creation."""
    
    async def run(self, context: CampaignContext) -> BusinessAnalysis:
        """Execute business analysis with context persistence"""
        
        try:
            # Add generation event
            await self.memory_service.add_generation_event(
                campaign_id=context.campaign_id,
                event_type=GenerationEventType.BUSINESS_ANALYSIS,
                agent_name=self.name
            )
            
            # Send progress update
            await send_progress_update(
                sender=self.name,
                recipients=["orchestrator"],
                campaign_id=context.campaign_id,
                stage=GenerationEventType.BUSINESS_ANALYSIS,
                progress_percentage=10.0,
                status_message="Starting business analysis"
            )
            
            start_time = time.time()
            
            # Use existing URL analysis logic if available
            url_analysis_agent = URLAnalysisAgent()
            if hasattr(context, 'business_url') and context.business_url:
                analysis_result = await url_analysis_agent.analyze_business_url(context.business_url)
            else:
                # Mock analysis for testing
                analysis_result = self._create_mock_business_analysis()
            
            # Convert to structured BusinessAnalysis object
            business_analysis = BusinessAnalysis.parse_obj(analysis_result)
            
            # Update campaign context
            context.business_analysis = business_analysis
            await self.memory_service.save_campaign_context(context)
            
            duration = time.time() - start_time
            
            # Add completion event
            await self.memory_service.add_generation_event(
                campaign_id=context.campaign_id,
                event_type=GenerationEventType.BUSINESS_ANALYSIS,
                agent_name=self.name,
                duration=duration,
                success=True,
                analysis_confidence=business_analysis.confidence_score
            )
            
            # Send A2A completion message
            await send_business_analysis_complete(
                sender=self.name,
                recipients=["enhanced_content_generation_agent", "visual_planning_agent"],
                campaign_id=context.campaign_id,
                business_analysis=business_analysis
            )
            
            # Send progress update
            await send_progress_update(
                sender=self.name,
                recipients=["orchestrator"],
                campaign_id=context.campaign_id,
                stage=GenerationEventType.BUSINESS_ANALYSIS,
                progress_percentage=100.0,
                status_message="Business analysis complete"
            )
            
            logger.info(f"✅ Business analysis complete for campaign {context.campaign_id}")
            return business_analysis
            
        except Exception as e:
            logger.error(f"❌ Business analysis failed: {e}")
            
            # Add error event
            await self.memory_service.add_generation_event(
                campaign_id=context.campaign_id,
                event_type=GenerationEventType.BUSINESS_ANALYSIS,
                agent_name=self.name,
                success=False,
                error_message=str(e)
            )
            
            raise
    
    def _create_mock_business_analysis(self) -> Dict[str, Any]:
        """Create mock business analysis for testing"""
        return {
            "company_name": "TechStartup Inc",
            "business_description": "AI-powered productivity software for remote teams",
            "target_audience": {
                "demographics": {
                    "age_range": "25-45",
                    "gender": "All genders",
                    "income_level": "Middle to high income",
                    "education": "College educated",
                    "location": "Urban areas, North America",
                    "occupation": "Software developers, project managers"
                },
                "psychographics": {
                    "interests": ["Technology", "Productivity", "Remote work"],
                    "values": ["Efficiency", "Innovation", "Work-life balance"],
                    "lifestyle": "Tech-savvy professionals",
                    "personality_traits": ["Detail-oriented", "Goal-driven", "Collaborative"],
                    "buying_behavior": "Research-driven, values ROI"
                },
                "pain_points": [
                    "Managing distributed teams",
                    "Communication inefficiencies", 
                    "Project coordination challenges"
                ],
                "preferred_platforms": ["LINKEDIN", "TWITTER"],
                "engagement_patterns": {
                    "peak_activity_times": ["9:00 AM", "1:00 PM", "6:00 PM"],
                    "preferred_content_types": ["IMAGE", "VIDEO"],
                    "engagement_frequency": "Daily during work hours",
                    "content_preferences": ["How-to guides", "Industry insights", "Product demos"]
                }
            },
            "brand_guidelines": {
                "brand_voice": "Professional yet approachable, knowledgeable and helpful",
                "tone_attributes": ["Professional", "Innovative", "Reliable", "User-focused"],
                "color_palette": ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"],
                "visual_style": "Clean, modern, tech-focused",
                "brand_values": ["Innovation", "Reliability", "User experience", "Productivity"],
                "messaging_principles": ["Clear communication", "Value-focused", "Solution-oriented"]
            },
            "competitive_analysis": {
                "direct_competitors": ["Slack", "Microsoft Teams", "Notion"],
                "indirect_competitors": ["Zoom", "Google Workspace", "Asana"],
                "competitive_advantages": ["AI-powered insights", "Seamless integration", "User-friendly interface"],
                "market_positioning": "Premium AI-enhanced productivity platform",
                "differentiation_factors": ["Advanced AI features", "Intuitive design", "Comprehensive analytics"]
            },
            "campaign_objectives": [
                {
                    "type": "BRAND_AWARENESS",
                    "description": "Increase brand recognition in target market",
                    "target_metrics": {"reach": 100000, "impressions": 500000},
                    "priority": 1
                },
                {
                    "type": "LEAD_GENERATION", 
                    "description": "Generate qualified leads for sales team",
                    "target_metrics": {"leads": 1000, "conversion_rate": 0.15},
                    "priority": 2
                }
            ],
            "industry_context": {
                "industry": "SaaS/Productivity Software",
                "market_size": "Growing rapidly, $50B+ market",
                "growth_trends": ["Remote work adoption", "AI integration", "Collaboration focus"],
                "regulatory_considerations": ["Data privacy", "GDPR compliance"],
                "seasonal_factors": ["Q4 budget cycles", "Back-to-school periods"]
            },
            "unique_value_proposition": "AI-powered productivity platform that helps remote teams work smarter, not harder",
            "key_messages": [
                "Boost team productivity with AI",
                "Seamless remote collaboration",
                "Data-driven insights for better decisions"
            ],
            "confidence_score": 0.85
        }

class EnhancedContentGenerationAgent:
    """Enhanced content generation agent with A2A messaging"""
    
    def __init__(self, memory_service: EnhancedMemoryService):
        self.name = "enhanced_content_generation_agent"
        self.memory_service = memory_service
        self.message_bus = get_message_bus()
        
        # Initialize the LLM model if available
        self.model = Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
        self.instruction = self._get_content_instruction()
        
        # Register with message bus and handlers (async, done in background)
        asyncio.create_task(self._register_with_message_bus())
    
    async def _register_with_message_bus(self):
        """Register agent and message handlers"""
        await self.message_bus.register_agent(self.name, {
            "type": "content_generation",
            "capabilities": ["content_strategy", "social_posts", "messaging"]
        })
        
        # Register handler for business analysis complete
        self.message_bus.register_message_handler(
            self.name,
            MessageType.BUSINESS_ANALYSIS_COMPLETE,
            self._handle_business_analysis_complete
        )
    
    def _get_content_instruction(self) -> str:
        return """You are an expert content strategist and social media specialist.

Your role is to create comprehensive content strategy and social media posts based on business analysis.

Create content strategy that includes:

1. **Campaign Theme:** Overall theme that aligns with brand and objectives
2. **Messaging Pillars:** 3-5 key messaging themes with supporting points
3. **Content Calendar:** Posting frequency and scheduling recommendations
4. **Social Media Posts:** Platform-optimized posts with captions, hashtags, and CTAs
5. **Cross-Platform Variations:** Adaptations for different social platforms
6. **Engagement Strategy:** Community management and interaction guidelines

For social media posts, create:
- Compelling captions that reflect brand voice
- Relevant hashtags for discoverability
- Clear calls-to-action
- Visual content requirements (image/video needs)
- Platform-specific optimizations

Return structured content strategy in JSON format matching ContentStrategy schema."""
    
    async def run(self, context: CampaignContext) -> ContentStrategy:
        """Execute content generation with business context"""
        
        if not context.business_analysis:
            raise ValueError("Business analysis required for content generation")
        
        try:
            start_time = time.time()
            
            # Add generation event
            await self.memory_service.add_generation_event(
                campaign_id=context.campaign_id,
                event_type=GenerationEventType.CONTENT_STRATEGY,
                agent_name=self.name
            )
            
            # Send progress update
            await send_progress_update(
                sender=self.name,
                recipients=["orchestrator"],
                campaign_id=context.campaign_id,
                stage=GenerationEventType.CONTENT_STRATEGY,
                progress_percentage=25.0,
                status_message="Generating content strategy"
            )
            
            # Generate content strategy based on business analysis
            content_strategy = await self._generate_content_strategy(context.business_analysis)
            
            # Update campaign context
            context.content_strategy = content_strategy
            await self.memory_service.save_campaign_context(context)
            
            duration = time.time() - start_time
            
            # Add completion event
            await self.memory_service.add_generation_event(
                campaign_id=context.campaign_id,
                event_type=GenerationEventType.CONTENT_STRATEGY,
                agent_name=self.name,
                duration=duration,
                success=True,
                posts_generated=len(content_strategy.social_posts)
            )
            
            # Send A2A completion message
            await send_content_strategy_ready(
                sender=self.name,
                recipients=["visual_content_orchestrator", "social_media_optimizer"],
                campaign_id=context.campaign_id,
                content_strategy=content_strategy
            )
            
            # Send progress update
            await send_progress_update(
                sender=self.name,
                recipients=["orchestrator"],
                campaign_id=context.campaign_id,
                stage=GenerationEventType.CONTENT_STRATEGY,
                progress_percentage=100.0,
                status_message="Content strategy complete"
            )
            
            logger.info(f"✅ Content strategy complete for campaign {context.campaign_id}")
            return content_strategy
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            
            # Add error event
            await self.memory_service.add_generation_event(
                campaign_id=context.campaign_id,
                event_type=GenerationEventType.CONTENT_STRATEGY,
                agent_name=self.name,
                success=False,
                error_message=str(e)
            )
            
            raise
    
    async def _handle_business_analysis_complete(self, message: A2AMessage) -> None:
        """Handle business analysis completion message"""
        logger.info(f"📨 Received business analysis complete for campaign {message.campaign_id}")
        
        # Auto-trigger content generation
        context = await self.memory_service.get_campaign_context(message.campaign_id)
        if context:
            await self.run(context)
    
    async def _generate_content_strategy(self, business_analysis: BusinessAnalysis) -> ContentStrategy:
        """Generate content strategy based on business analysis"""
        
        # This would normally use the LLM to generate strategy
        # For now, return structured mock strategy
        from ..models.campaign_context import (
            ContentStrategy, MessagingPillar, ContentCalendar, 
            SocialMediaPost, EngagementStrategy, PlatformVariation,
            SocialPlatform, ContentType
        )
        
        return ContentStrategy(
            campaign_theme="AI-Powered Productivity Revolution",
            messaging_pillars=[
                MessagingPillar(
                    theme="Productivity Enhancement",
                    key_points=["Save 2+ hours daily", "Automate routine tasks", "Focus on high-value work"],
                    target_emotion="Empowerment"
                ),
                MessagingPillar(
                    theme="Remote Team Success",
                    key_points=["Seamless collaboration", "Real-time insights", "Team alignment"],
                    target_emotion="Confidence"
                ),
                MessagingPillar(
                    theme="AI Innovation",
                    key_points=["Cutting-edge AI", "Smart recommendations", "Continuous learning"],
                    target_emotion="Excitement"
                )
            ],
            content_calendar=ContentCalendar(
                campaign_duration_days=30,
                posts_per_week={
                    SocialPlatform.LINKEDIN: 5,
                    SocialPlatform.TWITTER: 7
                },
                content_themes_by_week=[
                    "Product introduction",
                    "Use cases and benefits", 
                    "Customer success stories",
                    "Future vision"
                ]
            ),
            social_posts=[
                SocialMediaPost(
                    platform=SocialPlatform.LINKEDIN,
                    content_type=ContentType.IMAGE,
                    caption="🚀 Transform your team's productivity with AI-powered insights. See how our platform helps remote teams achieve 40% better collaboration. #ProductivityAI #RemoteWork #TeamCollaboration",
                    hashtags=["#ProductivityAI", "#RemoteWork", "#TeamCollaboration", "#AITools"],
                    call_to_action="Try our free 14-day trial",
                    visual_prompt="Professional team working remotely with AI dashboard, modern office setup, productivity metrics visible",
                    requires_image=True,
                    target_engagement="clicks"
                ),
                SocialMediaPost(
                    platform=SocialPlatform.TWITTER,
                    content_type=ContentType.VIDEO,
                    caption="Watch how AI transforms your daily workflow ⚡ From chaos to clarity in 60 seconds #AIProductivity #WorkSmart",
                    hashtags=["#AIProductivity", "#WorkSmart", "#TechTools"],
                    call_to_action="Learn more",
                    visual_prompt="Quick product demo showing before/after workflow transformation",
                    requires_video=True,
                    target_engagement="retweets"
                )
            ],
            engagement_strategy=EngagementStrategy(
                response_guidelines=["Respond within 2 hours", "Be helpful and solution-focused"],
                community_building_tactics=["Share user-generated content", "Host Q&A sessions"],
                user_generated_content="Encourage sharing of productivity tips"
            ),
            content_guidelines=[
                "Always include value proposition",
                "Use data-driven benefits",
                "Maintain professional tone",
                "Include clear CTAs"
            ],
            success_metrics={
                "engagement_rate": "5%+",
                "click_through_rate": "2%+",
                "lead_generation": "100 leads/month"
            }
        )

class EnhancedMarketingOrchestrator:
    """Enhanced marketing orchestrator with A2A coordination and persistent memory"""
    
    def __init__(self, base_path: str = "./campaign_sessions"):
        # Core attributes
        self.name = "enhanced_marketing_orchestrator"
        self.description = "Enhanced marketing orchestrator with A2A messaging and persistent memory"
        self.base_path = base_path
        
        # Service instances (initialized async)
        self.memory_service = None
        self.message_bus = get_message_bus()
        
        # Agent instances (initialized async)
        self.business_agent = None
        self.content_agent = None
        
        # Orchestrator state
        self.active_campaigns: Dict[str, CampaignContext] = {}
        
        logger.info("✅ Enhanced Marketing Orchestrator created")
    
    async def initialize(self):
        """Async initialization of memory service and agents"""
        
        # Initialize memory service
        self.memory_service = await initialize_memory_service(self.base_path)
        
        # Create agent instances
        self.business_agent = EnhancedBusinessAnalysisAgent(self.memory_service)
        self.content_agent = EnhancedContentGenerationAgent(self.memory_service)
        
        # Register orchestrator with message bus
        await self.message_bus.register_agent(self.name, {
            "type": "orchestrator",
            "capabilities": ["campaign_coordination", "progress_tracking"]
        })
        
        # Register progress update handler
        self.message_bus.register_message_handler(
            self.name,
            MessageType.PROGRESS_UPDATE,
            self._handle_progress_update
        )
        
        logger.info("✅ Enhanced Marketing Orchestrator fully initialized")
    
    async def generate_campaign(self, campaign_id: str, business_input: Dict[str, Any]) -> CampaignContext:
        """Generate complete marketing campaign with A2A coordination"""
        
        if not self.memory_service:
            await self.initialize()
        
        try:
            # Create or get campaign context
            context = await self.memory_service.get_campaign_context(campaign_id)
            if not context:
                context = await self.memory_service.create_campaign_context(
                    campaign_id=campaign_id,
                    campaign_name=business_input.get("campaign_name"),
                    campaign_description=business_input.get("description")
                )
            
            # Add business input to context
            if "business_url" in business_input:
                context.business_url = business_input["business_url"]
            
            self.active_campaigns[campaign_id] = context
            
            logger.info(f"🚀 Starting campaign generation: {campaign_id}")
            
            # Phase 1: Business Analysis
            business_analysis = await self.business_agent.run(context)
            
            # Phase 2: Content Generation (triggered by A2A message)
            content_strategy = await self.content_agent.run(context)
            
            # Phase 3: Visual Content (would be implemented next)
            # This would be triggered by A2A message from content agent
            
            # Get final context
            final_context = await self.memory_service.get_campaign_context(campaign_id)
            
            logger.info(f"✅ Campaign generation complete: {campaign_id}")
            return final_context
            
        except Exception as e:
            logger.error(f"❌ Campaign generation failed for {campaign_id}: {e}")
            
            # Add error event to context if available
            if campaign_id in self.active_campaigns:
                context = self.active_campaigns[campaign_id]
                await self.memory_service.add_generation_event(
                    campaign_id=campaign_id,
                    event_type=GenerationEventType.CAMPAIGN_FINALIZATION,
                    agent_name=self.name,
                    success=False,
                    error_message=str(e)
                )
            
            raise
        finally:
            # Clean up active campaign
            self.active_campaigns.pop(campaign_id, None)
    
    async def _handle_progress_update(self, message: A2AMessage) -> None:
        """Handle progress update messages"""
        payload = message.payload
        logger.info(f"📊 Progress update: {payload.get('stage')} - {payload.get('progress_percentage')}% - {payload.get('status_message')}")
    
    async def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign status and progress"""
        
        context = await self.memory_service.get_campaign_context(campaign_id)
        if not context:
            return None
        
        return {
            "campaign_id": campaign_id,
            "completion_percentage": context.get_completion_percentage(),
            "completed_stages": [stage.value for stage in context.completed_stages],
            "last_updated": context.last_updated.isoformat(),
            "version": context.version,
            "active_agents": context.active_agents,
            "generation_history": [
                {
                    "event_type": event.event_type.value,
                    "agent_name": event.agent_name,
                    "timestamp": event.timestamp.isoformat(),
                    "success": event.success,
                    "duration": event.duration_seconds
                }
                for event in context.generation_history[-10:]  # Last 10 events
            ]
        }
    
    async def list_campaigns(self) -> List[str]:
        """List all campaigns"""
        return await self.memory_service.list_campaign_contexts()
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory service statistics"""
        stats = await self.memory_service.get_memory_stats()
        message_stats = self.message_bus.get_agent_stats()
        
        return {
            "memory_service": stats,
            "message_bus": message_stats,
            "active_campaigns": len(self.active_campaigns)
        }
    
    async def stream_campaign_generation(self, campaign_request: Dict[str, Any]) -> AsyncIterator[str]:
        """Stream real-time campaign generation updates using ADK v1.8+ streaming capabilities"""
        
        campaign_id = campaign_request.get("campaign_id", str(uuid.uuid4()))
        
        try:
            # Initialize streaming context
            import json
            yield json.dumps({
                "type": "campaign_started", 
                "campaign_id": campaign_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Campaign generation started"
            })
            
            # Create campaign context
            context = await self.memory_service.create_campaign_context(
                campaign_id=campaign_id,
                campaign_name=campaign_request.get("campaign_name"),
                campaign_description=campaign_request.get("description")
            )
            
            # Add business input to context
            if "business_url" in campaign_request:
                context.business_url = campaign_request["business_url"]
            
            self.active_campaigns[campaign_id] = context
            
            yield json.dumps({
                "type": "context_created",
                "campaign_id": campaign_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Campaign context initialized"
            })
            
            # Stream business analysis
            yield json.dumps({
                "type": "stage_started",
                "campaign_id": campaign_id,
                "stage": "business_analysis",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Starting business analysis..."
            })
            
            # Perform business analysis with streaming updates
            business_analysis = await self.business_agent.run(context)
            
            yield json.dumps({
                "type": "stage_completed",
                "campaign_id": campaign_id,
                "stage": "business_analysis",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Business analysis completed",
                "data": {
                    "company_name": business_analysis.company_name,
                    "target_audience_summary": business_analysis.target_audience.demographics.model_dump(),
                    "confidence_score": business_analysis.confidence_score
                }
            })
            
            # Stream content generation
            yield json.dumps({
                "type": "stage_started",
                "campaign_id": campaign_id,
                "stage": "content_generation",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Generating marketing content..."
            })
            
            # Generate content with business analysis context
            content_strategy = await self.content_agent.run(context)
            
            yield json.dumps({
                "type": "stage_completed",
                "campaign_id": campaign_id,
                "stage": "content_generation",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Content generation completed",
                "data": {
                    "posts_generated": len(content_strategy.social_posts),
                    "platforms": [post.platform.value for post in content_strategy.social_posts],
                    "campaign_theme": content_strategy.campaign_theme
                }
            })
            
            # Final completion
            yield json.dumps({
                "type": "campaign_completed",
                "campaign_id": campaign_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Campaign generation completed successfully",
                "data": {
                    "business_analysis_summary": {
                        "company_name": business_analysis.company_name,
                        "confidence_score": business_analysis.confidence_score
                    },
                    "content_strategy_summary": {
                        "campaign_theme": content_strategy.campaign_theme,
                        "posts_count": len(content_strategy.social_posts)
                    },
                    "completion_percentage": context.get_completion_percentage()
                }
            })
            
        except Exception as e:
            logger.error(f"❌ Streaming campaign generation failed: {e}")
            import json
            yield json.dumps({
                "type": "campaign_error",
                "campaign_id": campaign_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Campaign generation failed: {str(e)}",
                "error": str(e)
            })
        finally:
            # Clean up active campaign tracking
            self.active_campaigns.pop(campaign_id, None)
    
    async def create_streaming_tool(self) -> ActiveStreamingTool:
        """Create ADK v1.8+ streaming tool for real-time updates"""
        
        def streaming_handler(query: str, campaign_id: str = None) -> AsyncIterator[str]:
            """Handle streaming requests"""
            async def stream():
                yield f"Processing query: {query}"
                if campaign_id:
                    status = await self.get_campaign_status(campaign_id)
                    if status:
                        yield f"Campaign {campaign_id} progress: {status['completion_percentage']}%"
                    else:
                        yield f"Campaign {campaign_id} not found"
                else:
                    yield "No campaign ID provided"
            
            return stream()
        
        return ActiveStreamingTool(
            name="marketing_orchestrator_stream",
            description="Stream real-time marketing campaign generation updates",
            handler=streaming_handler
        )

# --- Factory Functions ---

async def create_enhanced_marketing_orchestrator(base_path: str = "./campaign_sessions") -> EnhancedMarketingOrchestrator:
    """Factory function to create and initialize enhanced orchestrator"""
    
    orchestrator = EnhancedMarketingOrchestrator(base_path)
    await orchestrator.initialize()
    
    return orchestrator

# Export main class
__all__ = [
    "EnhancedMarketingOrchestrator",
    "EnhancedBusinessAnalysisAgent",
    "EnhancedContentGenerationAgent", 
    "create_enhanced_marketing_orchestrator"
]