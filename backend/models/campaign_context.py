"""
FILENAME: campaign_context.py
DESCRIPTION/PURPOSE: Structured campaign context models for ADK v1.6+ implementation
Author: JP + Claude Code + 2025-01-20

This module implements the enhanced CampaignContext architecture with zero fidelity loss,
proper type safety, and persistent session support for ADK v1.6+ upgrade.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid

logger = logging.getLogger(__name__)

# --- Enums and Constants ---

class SocialPlatform(str, Enum):
    """Supported social media platforms"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"

class CampaignObjectiveType(str, Enum):
    """Campaign objective types"""
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    SALES_CONVERSION = "sales_conversion"
    ENGAGEMENT = "engagement"
    TRAFFIC = "traffic"
    APP_DOWNLOADS = "app_downloads"

class ContentType(str, Enum):
    """Content types for posts"""
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    TEXT_ONLY = "text_only"

class GenerationEventType(str, Enum):
    """Types of generation events"""
    BUSINESS_ANALYSIS = "business_analysis"
    CONTENT_STRATEGY = "content_strategy"
    VISUAL_CONTENT = "visual_content"
    SOCIAL_POSTS = "social_posts"
    CAMPAIGN_FINALIZATION = "campaign_finalization"

# --- Core Data Models ---

class Demographics(BaseModel):
    """Target audience demographics"""
    age_range: str = Field(..., description="Age range (e.g., '25-34')")
    gender: Optional[str] = Field(None, description="Primary gender target")
    income_level: Optional[str] = Field(None, description="Income level")
    education: Optional[str] = Field(None, description="Education level")
    location: Optional[str] = Field(None, description="Geographic location")
    occupation: Optional[str] = Field(None, description="Primary occupation")

class Psychographics(BaseModel):
    """Target audience psychographics"""
    interests: List[str] = Field(default_factory=list, description="Primary interests")
    values: List[str] = Field(default_factory=list, description="Core values")
    lifestyle: Optional[str] = Field(None, description="Lifestyle description")
    personality_traits: List[str] = Field(default_factory=list, description="Key personality traits")
    buying_behavior: Optional[str] = Field(None, description="Purchasing behavior patterns")

class EngagementPatterns(BaseModel):
    """Audience engagement patterns"""
    peak_activity_times: List[str] = Field(default_factory=list, description="Best posting times")
    preferred_content_types: List[ContentType] = Field(default_factory=list, description="Preferred content formats")
    engagement_frequency: Optional[str] = Field(None, description="How often they engage")
    content_preferences: List[str] = Field(default_factory=list, description="Content topic preferences")

class TargetAudience(BaseModel):
    """Comprehensive target audience definition"""
    demographics: Demographics
    psychographics: Psychographics
    pain_points: List[str] = Field(default_factory=list, description="Audience pain points")
    preferred_platforms: List[SocialPlatform] = Field(default_factory=list, description="Preferred social platforms")
    engagement_patterns: EngagementPatterns
    audience_size_estimate: Optional[int] = Field(None, description="Estimated audience size")

class BrandGuidelines(BaseModel):
    """Brand guidelines and visual identity"""
    brand_voice: str = Field(..., description="Brand voice description")
    tone_attributes: List[str] = Field(default_factory=list, description="Tone characteristics")
    color_palette: List[str] = Field(default_factory=list, description="Brand colors")
    typography: Optional[str] = Field(None, description="Typography guidelines")
    logo_usage: Optional[str] = Field(None, description="Logo usage guidelines")
    visual_style: Optional[str] = Field(None, description="Visual style description")
    brand_values: List[str] = Field(default_factory=list, description="Core brand values")
    messaging_principles: List[str] = Field(default_factory=list, description="Key messaging principles")

class CompetitiveAnalysis(BaseModel):
    """Competitive landscape analysis"""
    direct_competitors: List[str] = Field(default_factory=list, description="Direct competitors")
    indirect_competitors: List[str] = Field(default_factory=list, description="Indirect competitors")
    competitive_advantages: List[str] = Field(default_factory=list, description="Our competitive advantages")
    market_positioning: Optional[str] = Field(None, description="Market position description")
    differentiation_factors: List[str] = Field(default_factory=list, description="Key differentiators")

class CampaignObjective(BaseModel):
    """Individual campaign objective"""
    type: CampaignObjectiveType
    description: str = Field(..., description="Objective description")
    target_metrics: Dict[str, Union[int, float, str]] = Field(default_factory=dict, description="Target KPIs")
    priority: int = Field(1, ge=1, le=5, description="Priority level (1-5)")
    timeline: Optional[str] = Field(None, description="Objective timeline")

class IndustryContext(BaseModel):
    """Industry and market context"""
    industry: str = Field(..., description="Primary industry")
    market_size: Optional[str] = Field(None, description="Market size information")
    growth_trends: List[str] = Field(default_factory=list, description="Industry growth trends")
    regulatory_considerations: List[str] = Field(default_factory=list, description="Regulatory factors")
    seasonal_factors: List[str] = Field(default_factory=list, description="Seasonal considerations")

class BusinessAnalysis(BaseModel):
    """Comprehensive business analysis with zero data loss"""
    company_name: str = Field(..., description="Company name")
    business_description: str = Field(..., description="Business description")
    target_audience: TargetAudience
    brand_guidelines: BrandGuidelines
    competitive_analysis: CompetitiveAnalysis
    campaign_objectives: List[CampaignObjective]
    industry_context: IndustryContext
    unique_value_proposition: str = Field(..., description="Unique value proposition")
    key_messages: List[str] = Field(default_factory=list, description="Key marketing messages")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis completion time")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0, description="Analysis confidence (0-1)")

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MessagingPillar(BaseModel):
    """Content messaging pillar"""
    theme: str = Field(..., description="Messaging theme")
    key_points: List[str] = Field(default_factory=list, description="Key messaging points")
    supporting_evidence: List[str] = Field(default_factory=list, description="Supporting evidence/examples")
    target_emotion: Optional[str] = Field(None, description="Target emotional response")

class PlatformVariation(BaseModel):
    """Platform-specific content variation"""
    platform: SocialPlatform
    content_adaptations: List[str] = Field(default_factory=list, description="Platform-specific adaptations")
    hashtag_strategy: List[str] = Field(default_factory=list, description="Platform hashtags")
    posting_frequency: Optional[str] = Field(None, description="Recommended posting frequency")
    optimal_times: List[str] = Field(default_factory=list, description="Optimal posting times")

class SocialMediaPost(BaseModel):
    """Individual social media post with full context"""
    post_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique post ID")
    platform: SocialPlatform
    content_type: ContentType
    caption: str = Field(..., description="Post caption")
    hashtags: List[str] = Field(default_factory=list, description="Post hashtags")
    call_to_action: Optional[str] = Field(None, description="Call to action")
    visual_prompt: Optional[str] = Field(None, description="Visual content prompt")
    requires_image: bool = Field(False, description="Requires image generation")
    requires_video: bool = Field(False, description="Requires video generation")
    target_engagement: Optional[str] = Field(None, description="Target engagement type")
    posting_time_recommendation: Optional[str] = Field(None, description="Recommended posting time")
    
    # Generated content URLs (populated by visual agents)
    image_url: Optional[str] = Field(None, description="Generated image URL")
    video_url: Optional[str] = Field(None, description="Generated video URL")
    
    class Config:
        validate_assignment = True

class ContentCalendar(BaseModel):
    """Content calendar structure"""
    campaign_duration_days: int = Field(..., ge=1, description="Campaign duration in days")
    posts_per_week: Dict[SocialPlatform, int] = Field(default_factory=dict, description="Posts per platform per week")
    content_themes_by_week: List[str] = Field(default_factory=list, description="Weekly content themes")
    special_events: List[str] = Field(default_factory=list, description="Special events/holidays")

class EngagementStrategy(BaseModel):
    """Engagement and community management strategy"""
    response_guidelines: List[str] = Field(default_factory=list, description="Response guidelines")
    community_building_tactics: List[str] = Field(default_factory=list, description="Community building")
    influencer_collaboration: Optional[str] = Field(None, description="Influencer strategy")
    user_generated_content: Optional[str] = Field(None, description="UGC strategy")

class ContentStrategy(BaseModel):
    """Comprehensive content strategy preserving all relationships"""
    campaign_theme: str = Field(..., description="Overall campaign theme")
    messaging_pillars: List[MessagingPillar] = Field(default_factory=list, description="Key messaging pillars")
    content_calendar: ContentCalendar
    social_posts: List[SocialMediaPost] = Field(default_factory=list, description="Generated social media posts")
    cross_platform_variations: Dict[SocialPlatform, PlatformVariation] = Field(default_factory=dict, description="Platform variations")
    engagement_strategy: EngagementStrategy
    content_guidelines: List[str] = Field(default_factory=list, description="Content creation guidelines")
    success_metrics: Dict[str, str] = Field(default_factory=dict, description="Success measurement criteria")
    strategy_timestamp: datetime = Field(default_factory=datetime.now, description="Strategy creation time")

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VisualStyle(BaseModel):
    """Visual content style guidelines"""
    style_attributes: List[str] = Field(default_factory=list, description="Visual style attributes")
    color_scheme: List[str] = Field(default_factory=list, description="Preferred colors")
    mood_and_tone: str = Field(..., description="Visual mood and tone")
    composition_preferences: List[str] = Field(default_factory=list, description="Composition guidelines")
    avoid_elements: List[str] = Field(default_factory=list, description="Elements to avoid")

class VisualGuidance(BaseModel):
    """Visual content generation guidance"""
    style_preferences: VisualStyle
    brand_consistency_requirements: List[str] = Field(default_factory=list, description="Brand consistency rules")
    platform_specifications: Dict[SocialPlatform, Dict[str, Any]] = Field(default_factory=dict, description="Platform-specific specs")
    image_generation_prompts: List[str] = Field(default_factory=list, description="Base image prompts")
    video_generation_prompts: List[str] = Field(default_factory=list, description="Base video prompts")
    visual_quality_standards: List[str] = Field(default_factory=list, description="Quality requirements")

class SocialMediaConfig(BaseModel):
    """Social media platform configuration"""
    enabled_platforms: List[SocialPlatform] = Field(default_factory=list, description="Enabled platforms")
    platform_priorities: Dict[SocialPlatform, int] = Field(default_factory=dict, description="Platform priority rankings")
    cross_posting_rules: Dict[str, Any] = Field(default_factory=dict, description="Cross-posting guidelines")
    scheduling_preferences: Dict[SocialPlatform, List[str]] = Field(default_factory=dict, description="Optimal posting times")
    engagement_monitoring: Dict[str, Any] = Field(default_factory=dict, description="Engagement monitoring config")

class GenerationEvent(BaseModel):
    """Campaign generation event for history tracking"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    event_type: GenerationEventType
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    agent_name: str = Field(..., description="Agent that generated the event")
    duration_seconds: Optional[float] = Field(None, description="Generation duration")
    success: bool = Field(True, description="Whether generation was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")
    
    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CampaignContext(BaseModel):
    """Root context object with all campaign data - zero fidelity loss"""
    
    # Core identifiers
    campaign_id: str = Field(..., description="Unique campaign identifier")
    creation_timestamp: datetime = Field(default_factory=datetime.now, description="Campaign creation time")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Campaign metadata
    campaign_name: Optional[str] = Field(None, description="Campaign name")
    campaign_description: Optional[str] = Field(None, description="Campaign description")
    
    # Structured components - no data loss
    business_analysis: Optional[BusinessAnalysis] = Field(None, description="Business analysis results")
    content_strategy: Optional[ContentStrategy] = Field(None, description="Content strategy")
    visual_guidance: Optional[VisualGuidance] = Field(None, description="Visual content guidance")
    social_media_config: Optional[SocialMediaConfig] = Field(None, description="Social media configuration")
    
    # Generation history and versioning
    generation_history: List[GenerationEvent] = Field(default_factory=list, description="Campaign generation history")
    version: int = Field(1, ge=1, description="Context version number")
    
    # Agent coordination state
    active_agents: List[str] = Field(default_factory=list, description="Currently active agents")
    completed_stages: List[GenerationEventType] = Field(default_factory=list, description="Completed generation stages")
    
    # Session persistence metadata
    session_id: Optional[str] = Field(None, description="Session identifier")
    persistent: bool = Field(True, description="Whether context should be persisted")
    
    def add_generation_event(self, event_type: GenerationEventType, agent_name: str, 
                           duration: Optional[float] = None, success: bool = True, 
                           error_message: Optional[str] = None, **metadata) -> GenerationEvent:
        """Add a generation event to the history"""
        event = GenerationEvent(
            event_type=event_type,
            agent_name=agent_name,
            duration_seconds=duration,
            success=success,
            error_message=error_message,
            metadata=metadata
        )
        self.generation_history.append(event)
        
        if success and event_type not in self.completed_stages:
            self.completed_stages.append(event_type)
        
        self.last_updated = datetime.now()
        self.version += 1
        
        return event
    
    def get_completion_percentage(self) -> float:
        """Calculate campaign completion percentage"""
        total_stages = len(GenerationEventType)
        completed_stages = len(self.completed_stages)
        return (completed_stages / total_stages) * 100
    
    def is_stage_complete(self, stage: GenerationEventType) -> bool:
        """Check if a generation stage is complete"""
        return stage in self.completed_stages
    
    def get_latest_event(self, event_type: Optional[GenerationEventType] = None) -> Optional[GenerationEvent]:
        """Get the latest generation event of a specific type"""
        events = self.generation_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return max(events, key=lambda e: e.timestamp) if events else None
    
    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "campaign_id": "campaign_123456",
                "campaign_name": "Product Launch Q1 2025",
                "creation_timestamp": "2025-01-20T10:00:00Z",
                "business_analysis": {
                    "company_name": "TechStartup Inc",
                    "business_description": "AI-powered productivity software",
                    "target_audience": {
                        "demographics": {
                            "age_range": "25-45",
                            "occupation": "Software developers"
                        }
                    }
                },
                "version": 1,
                "completed_stages": ["business_analysis"],
                "generation_history": [
                    {
                        "event_type": "business_analysis",
                        "agent_name": "business_analysis_agent",
                        "timestamp": "2025-01-20T10:05:00Z",
                        "success": True
                    }
                ]
            }
        }

# --- Validation Functions ---

@validator('email', pre=True, always=True)
def validate_email_format(cls, v):
    """Validate email format if provided"""
    if v and '@' not in v:
        raise ValueError('Invalid email format')
    return v

# --- Helper Functions ---

def create_campaign_context(campaign_id: str, campaign_name: Optional[str] = None, 
                          campaign_description: Optional[str] = None) -> CampaignContext:
    """Create a new campaign context with proper initialization"""
    return CampaignContext(
        campaign_id=campaign_id,
        campaign_name=campaign_name,
        campaign_description=campaign_description,
        session_id=str(uuid.uuid4())
    )

def serialize_campaign_context(context: CampaignContext) -> str:
    """Serialize campaign context to JSON string"""
    return context.model_dump_json(indent=2)

def deserialize_campaign_context(json_str: str) -> CampaignContext:
    """Deserialize campaign context from JSON string"""
    return CampaignContext.model_validate_json(json_str)

# Export all models for easy import
__all__ = [
    "CampaignContext",
    "BusinessAnalysis", 
    "ContentStrategy",
    "VisualGuidance",
    "SocialMediaConfig",
    "TargetAudience",
    "BrandGuidelines",
    "SocialMediaPost",
    "GenerationEvent",
    "SocialPlatform",
    "ContentType",
    "GenerationEventType",
    "CampaignObjectiveType",
    "create_campaign_context",
    "serialize_campaign_context", 
    "deserialize_campaign_context"
]