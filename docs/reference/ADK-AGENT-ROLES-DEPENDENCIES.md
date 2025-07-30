# ADK Agent Roles & Data Dependencies
# Author: JP + 2025-01-16
# Google ADK Framework - AI Marketing Campaign Post Generator

## Overview

This document defines the **complete ADK agent architecture** with explicit **upstream/downstream data dependencies** to ensure system integrity when making functional changes. Each agent has clearly defined input/output contracts that **MUST NOT BE BROKEN** without updating all dependent agents.

## Critical ADK Data Flow Rules

1. **Sequential Agent Pattern**: Data flows through agents in a specific order
2. **Context Propagation**: Comprehensive business context must flow to all downstream agents
3. **Dependency Chain**: Breaking any agent's output contract breaks all downstream agents
4. **Schema Stability**: Agent input/output schemas are API contracts

---

## 1. Business Analysis Agent (URLAnalysisAgent)

### **Role Definition**
**Primary Responsibility**: Extract comprehensive business context from user-provided URLs and transform it into structured data for all downstream agents.

### **Agent Type**: `URLAnalysisAgent` (Custom Agent)
**File**: `backend/agents/business_analysis_agent.py`

### **UPSTREAM DEPENDENCIES** (Inputs)
```python
# INPUT SCHEMA - NEVER CHANGE WITHOUT UPDATING ALL CALLERS
{
    "urls": List[str],                    # Required: Business URLs to analyze
    "analysis_depth": str,                # "basic" | "standard" | "comprehensive"
    "analysis_type": str                  # Optional: Additional context
}
```

**Input Sources**:
- User-provided URLs via API endpoint `/api/v1/analysis/url`
- Campaign creation form URL inputs
- **NO UPSTREAM AGENTS** - This is the data source agent

### **DOWNSTREAM DEPENDENCIES** (Outputs)
```python
# OUTPUT SCHEMA - CRITICAL: ALL DOWNSTREAM AGENTS DEPEND ON THIS STRUCTURE
{
    "business_analysis": {
        "company_name": str,              # CRITICAL: Used by ALL content agents
        "business_description": str,      # CRITICAL: Used by ALL content agents
        "industry": str,                  # Used by content generation
        "target_audience": str,           # Used by content generation
        
        # CRITICAL: Product Context - Used by Visual Content Agent
        "product_context": {
            "primary_products": List[str],    # CRITICAL: Specific products being sold
            "design_style": str,              # CRITICAL: Visual style direction
            "visual_themes": List[str],       # CRITICAL: Theme-based image generation
            "color_palette": List[str],       # CRITICAL: Brand color consistency
            "target_scenarios": List[str],    # CRITICAL: Context for image generation
            "brand_personality": str          # CRITICAL: Content tone matching
        },
        
        # CRITICAL: Campaign Guidance - Populates UI elements
        "campaign_guidance": {
            "suggested_themes": List[str],    # CRITICAL: Populates themes dropdown
            "suggested_tags": List[str],      # CRITICAL: Populates tags section
            "creative_direction": str,        # CRITICAL: Guides content creation
            "visual_style": Dict[str, Any],   # CRITICAL: Visual generation parameters
            "campaign_media_tuning": str      # CRITICAL: User media tuning guidance
        },
        
        # Content Generation Context
        "brand_voice": str,               # Used by text generation
        "key_messaging": List[str],       # Used by content generation
        "competitive_advantages": List[str] # Used by campaign strategy
    },
    
    "url_insights": Dict[str, Any],       # Raw scraped data
    "analysis_metadata": {
        "urls_analyzed": int,
        "successful_scrapes": int,
        "analysis_type": str,
        "ai_analysis_used": bool
    }
}
```

### **Data Flow Dependencies**
**CRITICAL DOWNSTREAM CONSUMERS**:
1. **Content Generation Agent** - Requires `business_analysis` for context-aware content
2. **Visual Content Agent** - Requires `product_context` for relevant image generation
3. **Campaign Strategy Agent** - Requires `campaign_guidance` for strategy formation
4. **Frontend UI** - Requires `campaign_guidance.suggested_themes` and `suggested_tags`

### **Functional Change Rules**
⚠️ **BREAKING CHANGE PREVENTION**:
- **NEVER** remove fields from `business_analysis` output schema
- **NEVER** change the structure of `product_context`
- **NEVER** modify `campaign_guidance` without updating frontend
- **ALWAYS** maintain backward compatibility when adding new fields

---

## 2. Content Generation Agent (Sequential Agent)

### **Role Definition**
**Primary Responsibility**: Generate text, image, and video content using business context from Business Analysis Agent.

### **Agent Type**: `SequentialAgent` 
**File**: `backend/agents/marketing_orchestrator.py`

### **Sub-Agents**:
1. `TextGenerationAgent` - Generate social media text content
2. `ImageGenerationAgent` - Generate image prompts and coordinate visual content
3. `VideoGenerationAgent` - Generate video content prompts

### **UPSTREAM DEPENDENCIES** (Inputs)
```python
# INPUT SCHEMA - DEPENDS ON BUSINESS ANALYSIS AGENT OUTPUT
{
    "business_context": Dict[str, Any],   # FROM: Business Analysis Agent
    "campaign_objective": str,            # FROM: User input
    "target_platforms": List[str],        # FROM: Campaign configuration
    "creativity_level": int,              # FROM: User input (1-10)
    "content_types": List[str],           # ["text", "image", "video"]
    
    # ADK Enhancement: Enhanced context parameters
    "campaign_media_tuning": str,         # FROM: business_analysis.campaign_guidance
    "campaign_guidance": Dict[str, Any],  # FROM: business_analysis.campaign_guidance
    "product_context": Dict[str, Any],    # FROM: business_analysis.product_context
    "visual_style": Dict[str, Any],       # FROM: business_analysis.campaign_guidance.visual_style
    "creative_direction": str             # FROM: business_analysis.campaign_guidance.creative_direction
}
```

**Input Sources**:
- Business Analysis Agent output (PRIMARY DEPENDENCY)
- User campaign configuration
- Campaign strategy parameters

### **DOWNSTREAM DEPENDENCIES** (Outputs)
```python
# OUTPUT SCHEMA - SOCIAL MEDIA AGENT AND FRONTEND DEPEND ON THIS
{
    "generated_content": {
        "text_posts": List[Dict[str, Any]],   # Text-only social media posts
        "image_posts": List[Dict[str, Any]],  # Posts with text + generated images
        "video_posts": List[Dict[str, Any]]   # Posts with text + generated videos
    },
    
    "content_metadata": {
        "total_posts_generated": int,
        "generation_timestamp": str,
        "model_versions": Dict[str, str],
        "cost_tracking": Dict[str, float]
    },
    
    # CRITICAL: Each post must have this structure
    "post_structure": {
        "id": str,                        # Unique post identifier
        "content": str,                   # Post text content
        "platform": str,                  # Target platform
        "post_type": str,                 # "text" | "image" | "video"
        "hashtags": List[str],            # Generated hashtags
        "call_to_action": str,            # CTA for the post
        "image_url": Optional[str],       # Generated image URL (if image post)
        "video_url": Optional[str],       # Generated video URL (if video post)
        "engagement_prediction": float,   # Predicted engagement score
        "optimal_posting_time": str       # Recommended posting time
    }
}
```

### **Data Flow Dependencies**
**CRITICAL UPSTREAM DEPENDENCY**: Business Analysis Agent
**CRITICAL DOWNSTREAM CONSUMERS**:
1. **Social Media Agent** - Optimizes generated content for platforms
2. **Frontend UI** - Displays generated posts in campaign interface
3. **Campaign Results API** - Returns final campaign to user

### **Functional Change Rules**
⚠️ **BREAKING CHANGE PREVENTION**:
- **NEVER** change the `post_structure` schema without updating frontend
- **NEVER** remove required fields from generated content
- **ALWAYS** maintain the relationship with Business Analysis Agent output

---

## 3. ADK Agentic Visual Content System (ADR-019)

### **Role Definition**
**Primary Responsibility**: Autonomous visual content generation with validation and self-correction using true ADK agent framework.

### **Agent Hierarchy**: 
- **`VisualContentOrchestratorAgent`** (ADK SequentialAgent)
- **`ImageGenerationAgent`** (ADK LlmAgent) 
- **`VideoGenerationAgent`** (ADK LlmAgent)
- **`VisualContentValidationTool`** (Validation Framework)

**File**: `backend/agents/adk_visual_agents.py`

### **UPSTREAM DEPENDENCIES** (Inputs)
```python
# INPUT SCHEMA - ENHANCED ADK DATA FLOW
{
    "social_posts": List[Dict[str, Any]], # FROM: Content Generation Agent
    "business_context": Dict[str, Any],   # FROM: Business Analysis Agent
    "campaign_objective": str,            # FROM: User input
    "target_platforms": List[str],        # FROM: Campaign configuration
    
    # ADK AGENTIC ENHANCEMENT: Campaign-aware autonomous generation
    "campaign_media_tuning": str,         # FROM: business_analysis.campaign_guidance
    "campaign_guidance": Dict[str, Any],  # FROM: business_analysis.campaign_guidance  
    "product_context": Dict[str, Any],    # FROM: business_analysis.product_context
    "visual_style": Dict[str, Any],       # FROM: business_analysis.campaign_guidance.visual_style
    "creative_direction": str,            # FROM: business_analysis.campaign_guidance.creative_direction
    "campaign_id": str                    # FROM: Campaign context for caching and validation
}
```

**Key Business Context Dependencies**:
```python
# CRITICAL: Visual Content Agent MUST receive product-specific context
"product_context": {
    "primary_products": ["Joker t-shirt design"],      # CRITICAL: Specific product
    "visual_themes": ["dark humor", "comic book"],     # CRITICAL: Theme guidance
    "color_palette": ["purple", "green", "white"],     # CRITICAL: Brand colors
    "target_scenarios": ["people wearing t-shirts"],   # CRITICAL: Image scenarios
    "brand_personality": "edgy, artistic"              # CRITICAL: Style direction
}
```

### **DOWNSTREAM DEPENDENCIES** (Outputs)
```python
# OUTPUT SCHEMA - ADK AGENTIC VISUAL CONTENT WITH VALIDATION
{
    "visual_content": {
        "images": List[Dict[str, Any]],   # Validated generated images with metadata
        "videos": List[Dict[str, Any]]    # Validated generated videos with metadata
    },
    
    # CRITICAL: Each visual content item structure with ADK validation
    "visual_item_structure": {
        "id": str,                        # Unique content identifier
        "post_id": str,                   # Links to original social post
        "content_type": str,              # "image" | "video"
        "url": str,                       # Generated content URL
        "prompt_used": str,               # Final enhanced generation prompt
        "generation_metadata": {
            "model_used": str,            # "imagen-3.0-generate-002" | "veo-2.0"
            "generation_time": float,     # Time taken to generate
            "cost": float,                # Generation cost
            "retry_count": int,           # Number of retry attempts
            "validation_score": float,    # Autonomous validation score (0-100)
            "iterations": int             # Number of self-correction iterations
        },
        "adk_agent_metadata": {
            "agent_used": str,            # "ImageGenerationAgent" | "VideoGenerationAgent"
            "autonomous_validation": bool, # Whether agent validated its own work
            "self_correction_applied": bool, # Whether agent self-corrected
            "campaign_context_integration": bool, # Whether campaign guidance was used
            "validation_details": Dict[str, Any] # Detailed validation results
        },
        "business_context_applied": {
            "product_context_used": bool, # Whether product context influenced generation
            "campaign_guidance_used": bool, # Whether campaign guidance was applied
            "media_tuning_applied": bool  # Whether media tuning was considered
        }
    }
}
```

### **ADK Agentic Visual Generation Logic**
```python
# ADK AUTONOMOUS VISUAL GENERATION WITH VALIDATION - NEVER BREAK THIS LOGIC
class ImageGenerationAgent(LlmAgent):
    async def generate_and_validate_image(
        self, 
        post_content: str,
        campaign_guidance: Dict[str, Any],
        business_context: Dict[str, Any],
        campaign_id: str,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Generate and validate image with autonomous iteration."""
        
        for iteration in range(max_iterations):
            # Step 1: Create campaign-aware prompt
            enhanced_prompt = self._create_campaign_aware_prompt(
                post_content, campaign_guidance, business_context
            )
    
            # Step 2: Generate image using Imagen API
            image_result = await self._generate_imagen_content(enhanced_prompt, campaign_id)
            
            # Step 3: Autonomous validation
            validation_result = await self.validator.validate_image_content(
                image_result["image_url"], post_content, campaign_guidance, business_context
            )
            
            # Step 4: Self-correction if validation fails
            if validation_result.get("valid") and validation_result.get("overall_score", 0) >= 75:
                return {"success": True, "image_url": image_result["image_url"], ...}
            else:
                # Use validation feedback to improve next iteration
                campaign_guidance["validation_feedback"] = validation_result.get("recommendations", [])
        
        return {"success": False, "error": "Failed after max iterations"}

# CRITICAL: Campaign-aware prompt creation
def _create_campaign_aware_prompt(self, post_content: str, campaign_guidance: Dict, business_context: Dict) -> str:
    """Create enhanced image prompt incorporating campaign guidance."""
    base_prompt = f"Create a professional marketing image for: {post_content}"
    
    # Add campaign context from guidance
    if campaign_guidance.get("visual_style"):
        base_prompt += f" Visual style: {campaign_guidance['visual_style']}."
    if campaign_guidance.get("brand_voice"):
        base_prompt += f" Brand voice: {campaign_guidance['brand_voice']}."
    
    # Add business context
    if business_context.get("company_name"):
        base_prompt += f" Company: {business_context['company_name']}."
    
    return base_prompt + " High quality, professional, social media optimized, brand consistent."
```

### **Data Flow Dependencies**
**CRITICAL UPSTREAM DEPENDENCIES**:
1. **Business Analysis Agent** - Provides product context for relevant generation
2. **Content Generation Agent** - Provides social posts to generate visuals for

**CRITICAL DOWNSTREAM CONSUMERS**:
1. **Frontend UI** - Displays generated images/videos in campaign results
2. **Campaign Results API** - Returns visual content URLs to user

### **ADK Agentic Functional Change Rules**
⚠️ **BREAKING CHANGE PREVENTION**:
- **NEVER** bypass autonomous validation in ADK agents
- **NEVER** change `visual_item_structure` without updating frontend
- **NEVER** remove self-correction capabilities from agents
- **ALWAYS** use campaign guidance in system prompts for context-aware generation
- **NEVER** fall back to non-ADK wrapper classes
- **ALWAYS** maintain validation score thresholds (>=75 for success)
- **NEVER** ignore validation feedback in self-correction loops

---

## 4. Social Media Agent (Sequential Agent)

### **Role Definition**
**Primary Responsibility**: Optimize generated content for specific social media platforms and predict engagement performance.

### **Agent Type**: `SequentialAgent`
**File**: `backend/agents/marketing_orchestrator.py`

### **Sub-Agents**:
1. `PlatformOptimizationAgent` - Platform-specific content optimization
2. `HashtagGenerationAgent` - Generate relevant hashtags
3. `EngagementPredictionAgent` - Predict content performance

### **UPSTREAM DEPENDENCIES** (Inputs)
```python
# INPUT SCHEMA - DEPENDS ON CONTENT GENERATION AGENT OUTPUT
{
    "generated_content": Dict[str, Any], # FROM: Content Generation Agent
    "visual_content": Dict[str, Any],    # FROM: Visual Content Agent
    "business_context": Dict[str, Any],  # FROM: Business Analysis Agent
    "target_platforms": List[str],       # FROM: User configuration
    "campaign_objective": str            # FROM: User input
}
```

### **DOWNSTREAM DEPENDENCIES** (Outputs)
```python
# OUTPUT SCHEMA - FINAL CAMPAIGN RESULTS STRUCTURE
{
    "optimized_campaign": {
        "posts": List[Dict[str, Any]],    # Platform-optimized posts
        "platform_strategies": Dict[str, Any], # Platform-specific recommendations
        "hashtag_strategies": Dict[str, Any],   # Hashtag recommendations per platform
        "engagement_predictions": Dict[str, Any] # Expected performance metrics
    },
    
    "campaign_metadata": {
        "total_posts": int,
        "platforms_covered": List[str],
        "estimated_reach": int,
        "confidence_score": float
    }
}
```

### **Data Flow Dependencies**
**CRITICAL UPSTREAM DEPENDENCIES**:
1. **Content Generation Agent** - Provides base content to optimize
2. **Visual Content Agent** - Provides visual assets to associate with posts
3. **Business Analysis Agent** - Provides business context for platform optimization

**CRITICAL DOWNSTREAM CONSUMERS**:
1. **Campaign Results API** - Returns final optimized campaign to user
2. **Frontend UI** - Displays final campaign with platform recommendations

---

## 5. Campaign Results API

### **Role Definition**
**Primary Responsibility**: Aggregate all agent outputs into final campaign results and provide API endpoint for frontend consumption.

### **Agent Type**: API Endpoint
**File**: `backend/api/routes/content.py`

### **UPSTREAM DEPENDENCIES** (Inputs)
```python
# INPUT SCHEMA - AGGREGATES ALL AGENT OUTPUTS
{
    "business_analysis": Dict[str, Any],    # FROM: Business Analysis Agent
    "generated_content": Dict[str, Any],    # FROM: Content Generation Agent  
    "visual_content": Dict[str, Any],       # FROM: Visual Content Agent
    "optimized_campaign": Dict[str, Any]    # FROM: Social Media Agent
}
```

### **DOWNSTREAM DEPENDENCIES** (Outputs)
```python
# FINAL API RESPONSE SCHEMA - FRONTEND DEPENDS ON THIS STRUCTURE
{
    "campaign": {
        "id": str,                          # Unique campaign identifier
        "business_context": Dict[str, Any], # Business analysis results
        "posts": List[Dict[str, Any]],      # Final optimized social media posts
        "campaign_guidance": {
            "suggested_themes": List[str],   # CRITICAL: Populates UI themes section
            "suggested_tags": List[str],     # CRITICAL: Populates UI tags section
            "creative_direction": str,       # Campaign creative guidance
            "platform_recommendations": Dict[str, Any] # Platform-specific advice
        },
        "generation_metadata": {
            "total_generation_time": float,
            "total_cost": float,
            "models_used": List[str],
            "success_rate": float
        }
    },
    
    "status": str,                          # "success" | "error" | "partial"
    "message": str,                         # Status message
    "timestamp": str                        # Generation timestamp
}
```

---

## ADK Data Flow Validation

### **Environment Configuration Requirements**
```bash
# CRITICAL: These environment variables MUST be set for real AI analysis
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
IMAGE_MODEL=imagen-3.0-generate-002
VIDEO_MODEL=veo-2
```

### **Data Flow Testing Commands**
```bash
# 1. Test Business Analysis Agent
curl -X POST "http://localhost:8000/api/v1/analysis/url" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.redbubble.com/i/t-shirt/The-Joker-Why-Aren-t-You-Laughing-by-illustraMan/170001221.1AP75"]}'

# 2. Test Full Campaign Generation
curl -X POST "http://localhost:8000/api/v1/content/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "business_description": "illustraMan Joker t-shirt design",
    "objective": "increase sales",
    "target_audience": "comic book fans",
    "campaign_type": "product_launch"
  }'
```

### **Critical Success Criteria**
1. **Business Analysis**: Must return product-specific context, not generic mock data
2. **Campaign Guidance**: UI elements (themes/tags) must be populated with real data  
3. **Visual Content**: Images must be contextually relevant to the specific product
4. **Data Flow**: Each agent must receive and process upstream context correctly

### **Breaking Change Detection**
```bash
# Run full integration tests to detect breaking changes
make test-full-stack

# Verify agent data flow integrity
python backend/test_workflow.py
```

---

## Conclusion

This ADK agent architecture ensures **robust data flow** with clear **input/output contracts**. When making functional changes:

1. **NEVER** break agent output schemas without updating all downstream consumers
2. **ALWAYS** test the complete data flow after changes
3. **VERIFY** that business context propagates correctly through all agents
4. **ENSURE** the frontend receives properly structured campaign data

The system's reliability depends on maintaining these **strict data dependency contracts**. 