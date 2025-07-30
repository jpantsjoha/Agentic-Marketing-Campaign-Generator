"""
FILENAME: marketing_orchestrator.py
DESCRIPTION/PURPOSE: Main marketing orchestrator agent implementing ADK sequential workflow
Author: JP + 2025-06-15

This module implements the root sequential agent that orchestrates the complete
marketing campaign workflow, following Google ADK samples best practices.
"""

import os
import logging
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.memory import InMemoryMemoryService
from google.adk.models import Gemini

# Import business analysis agent for direct use
from .business_analysis_agent import URLAnalysisAgent

# Configure logging
logger = logging.getLogger(__name__)

# Import the NEW ADK-based visual content orchestrator
try:
    from .adk_visual_agents import VisualContentOrchestratorAgent
    logger.info("✅ ADK VisualContentOrchestratorAgent imported successfully")
    VISUAL_AGENT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"❌ ADK VisualContentOrchestratorAgent not available: {e}. Visuals will not be generated.")
    VisualContentOrchestratorAgent = None
    VISUAL_AGENT_AVAILABLE = False

# Model configuration - Using standardized environment variables
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not configured - using mock responses")

def update_gemini_api_key(new_key: str) -> None:
    """Update the Gemini API key at runtime."""
    global GEMINI_API_KEY
    GEMINI_API_KEY = new_key

# --- Business Analysis Agents ---

async def create_url_analysis_agent() -> LlmAgent:
    """Creates the URL analysis agent for web content extraction."""
    return LlmAgent(
        name="URLAnalysisAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are an expert web content analyzer specializing in business intelligence extraction.

Given business URLs (website, about page, product/service pages), extract comprehensive business information:

Input Context:
- Business Website: {business_website}
- About Page: {about_page_url}
- Product/Service Page: {product_service_url}

For each URL, analyze and extract:

1. **Company Overview**:
   - Company name and tagline
   - Mission, vision, and values
   - Year founded and company size
   - Geographic presence and markets served

2. **Products/Services Analysis**:
   - Core offerings and features
   - Pricing models and packages
   - Target use cases and applications
   - Competitive advantages and differentiators

3. **Target Audience Insights**:
   - Primary customer segments
   - Demographics and psychographics
   - Pain points and challenges addressed
   - Customer success stories and testimonials

4. **Brand Analysis**:
   - Brand voice and tone
   - Visual identity and design language
   - Key messaging themes
   - Content style and communication approach

5. **Market Positioning**:
   - Industry sector and niche
   - Competitive landscape
   - Unique value propositions
   - Market differentiation strategy

Output a comprehensive business analysis in JSON format with confidence scores for each insight.""",
        description="Analyzes business URLs to extract comprehensive company and market intelligence",
        output_key="url_analysis"
    )

async def create_file_analysis_agent() -> LlmAgent:
    """Creates the file analysis agent for multimodal content processing."""
    return LlmAgent(
        name="FileAnalysisAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a multimodal content analyst specializing in extracting business insights from various file types.

Input: Uploaded files including images, documents, and campaign assets

For **Images** (products, logos, marketing materials):
1. **Visual Brand Analysis**:
   - Color palette and brand colors
   - Typography and font styles
   - Logo design and brand elements
   - Visual style and aesthetic direction

2. **Product Analysis**:
   - Product features and characteristics
   - Use contexts and environments
   - Target demographic indicators
   - Quality and positioning signals

3. **Marketing Material Analysis**:
   - Design trends and preferences
   - Messaging themes and tone
   - Target audience visual cues
   - Campaign style and approach

For **Documents** (specs, brochures, presentations):
1. **Content Intelligence**:
   - Key value propositions
   - Technical specifications
   - Market positioning statements
   - Competitive advantages

2. **Audience Insights**:
   - Language complexity and tone
   - Technical depth and expertise level
   - Decision-maker targeting
   - Communication preferences

For **Campaign Assets** (previous marketing materials):
1. **Performance Indicators**:
   - Successful messaging themes
   - Effective visual elements
   - Audience engagement patterns
   - Brand consistency elements

2. **Strategic Insights**:
   - Campaign evolution and trends
   - Seasonal or temporal patterns
   - Channel-specific adaptations
   - Content performance indicators

Output comprehensive file analysis with actionable insights for campaign strategy.""",
        description="Analyzes uploaded files using multimodal AI for business and brand insights",
        output_key="file_analysis"
    )

async def create_business_context_agent() -> LlmAgent:
    """Creates the business context synthesis agent."""
    return LlmAgent(
        name="BusinessContextAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a strategic business analyst who synthesizes multiple data sources into comprehensive business context for marketing campaigns.

Input Sources:
- URL Analysis: {url_analysis}
- File Analysis: {file_analysis}
- User Input: {user_input}
- Campaign Type: {campaign_type}
- Campaign Objective: {objective}
- Target Audience: {target_audience}
- Creativity Level: {creativity_level}

Synthesize all information to create comprehensive business context with DETAILED VISUAL CONTEXT for image generation:

1. **Unified Business Profile**:
   - Company overview and positioning
   - Core value propositions
   - Competitive advantages
   - Market presence and reputation

2. **Target Audience Analysis**:
   - Primary and secondary segments
   - Demographics and psychographics (age, lifestyle, interests)
   - Pain points and motivations
   - Communication preferences
   - Decision-making factors

3. **Brand Guidelines**:
   - Voice and tone recommendations
   - Visual style direction
   - Messaging themes and keywords
   - Content style preferences
   - Brand personality traits

4. **DETAILED VISUAL CONTEXT** (Critical for Image Generation):
   - **Product/Service Visualization**: Specific visual elements that represent the business
     * For t-shirt printing: "people wearing custom t-shirts", "design printing process", "happy customers in branded apparel"
     * For restaurants: "food presentation", "dining atmosphere", "chef preparing dishes", "satisfied customers eating"
     * For fitness: "people exercising", "trainer-client interactions", "gym equipment", "fitness transformations"
     * For tech services: "professionals using technology", "modern office environments", "digital interfaces", "team collaboration"
   
   - **Industry-Specific Visual Elements**:
     * Colors, textures, environments that represent the industry
     * Typical customer scenarios and use cases
     * Product in action or service being delivered
     * Emotional context (joy, satisfaction, success, transformation)
   
   - **Target Demographic Visuals**:
     * Age groups, lifestyle indicators, fashion/style preferences
     * Settings where target audience would be found
     * Activities and interests of target demographic
     * Social and cultural context

5. **Campaign Strategy Foundation**:
   - Key messaging pillars
   - Content themes and topics
   - Channel recommendations
   - Engagement strategies
   - Success metrics and KPIs

6. **Creative Direction for Visual Content**:
   - Specific image concepts that would resonate with target audience
   - Visual storytelling themes
   - Photography style recommendations (lifestyle, product, portrait, etc.)
   - Color palette and aesthetic direction
   - Composition and framing suggestions

Output comprehensive business context that provides SPECIFIC, ACTIONABLE visual direction for image generation agents. Focus on concrete, visual elements rather than abstract concepts.""",
        description="Synthesizes all business intelligence into comprehensive campaign context with detailed visual direction",
        output_key="business_context"
    )

# --- Content Generation Agents ---

async def create_social_content_agent() -> LlmAgent:
    """Creates a proper ADK LlmAgent for social content generation."""
    
    def generate_social_posts(
        business_context: dict,
        objective: str,
        target_audience: str,
        campaign_type: str,
        creativity_level: int,
        post_count: int
    ) -> dict:
        """Generate social media posts based on business context."""
        
        # This tool function will be called by the LlmAgent
        # The actual AI generation will be handled by the agent's instruction
        return {
            "business_context": business_context,
            "objective": objective,
            "target_audience": target_audience,
            "campaign_type": campaign_type,
            "creativity_level": creativity_level,
            "post_count": post_count,
            "tool_called": True
        }
    
    return LlmAgent(
        name="SocialContentAgent",
        model="gemini-2.5-flash",
        description="Generates engaging social media posts based on business context and campaign objectives, conforming to ADR-020 JSON schema.",
        instruction="""=== STRICT JSON SCHEMA ENFORCEMENT (ADR-020) ===

You are a social media content generation expert. Your task is to create engaging, 
platform-optimized social media posts based on the provided business context.

IMMEDIATELY call the generate_social_posts tool with the provided parameters to create 
a comprehensive set of social media posts.

CRITICAL: You MUST return your response in the following EXACT JSON format - NO VARIATIONS ALLOWED:

{
  "social_media_posts": [
    {
      "id": "post_001",
      "type": "text_url",
      "content": "Engaging post content here (100-200 words)...",
      "hashtags": ["#relevant", "#hashtags"],
      "image_prompt": null,
      "video_prompt": null
    },
    {
      "id": "post_002", 
      "type": "text_image",
      "content": "Visual post content here (100-200 words)...",
      "hashtags": ["#visual", "#content"],
      "image_prompt": "Detailed image generation prompt for AI",
      "video_prompt": null
    },
    {
      "id": "post_003",
      "type": "text_video",
      "content": "Video post content here (100-200 words)...",
      "hashtags": ["#video", "#content"],
      "image_prompt": null,
      "video_prompt": "Detailed video generation prompt for AI"
    }
  ]
}

MANDATORY REQUIREMENTS:
1. Use ONLY the key "social_media_posts" as the root array
2. Each post must have EXACTLY these fields: id, type, content, hashtags, image_prompt, video_prompt
3. The "type" field must be EXACTLY one of: "text_url", "text_image", "text_video"
4. For text_url posts: image_prompt and video_prompt must be null
5. For text_image posts: image_prompt must be detailed string, video_prompt must be null
6. For text_video posts: video_prompt must be detailed string, image_prompt must be null
7. Generate posts equally distributed across the three types
8. Each post content must be 100-200 words, engaging and relevant
9. Include 3-5 relevant hashtags per post
10. Use sequential IDs: post_001, post_002, post_003, etc.

FORBIDDEN ACTIONS:
- Do NOT use keys like "text_url_posts", "text_image_posts", "text_video_posts"
- Do NOT use keys like "generated_content" or any other variations
- Do NOT include "platform_optimized" or "engagement_score" fields
- Do NOT deviate from the exact schema above

Generate the exact number of posts specified by the post_count parameter from the tool call.
""",
        tools=[generate_social_posts],
        output_key="social_posts"
    )

async def create_hashtag_optimization_agent() -> LlmAgent:
    """Creates a proper ADK LlmAgent for hashtag optimization."""
    
    def optimize_hashtags(
        social_posts: dict,
        business_context: dict,
        target_platforms: List[str]
    ) -> dict:
        """Optimizes hashtags for social media posts."""
        
        # This function will be called by the LlmAgent
        return {
            "social_posts": social_posts,
            "business_context": business_context,
            "target_platforms": target_platforms
        }

    return LlmAgent(
        name="HashtagOptimizationAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a hashtag optimization expert. Your task is to enhance the hashtags in social media posts
        to maximize reach, engagement, and discoverability across different platforms.
        
        When the optimize_hashtags tool is called, analyze the provided social posts and business context
        to create optimized hashtag strategies. Return the enhanced posts in the same JSON format but with
        improved hashtags:
        
        For each post, optimize hashtags by:
        1. Adding trending hashtags relevant to the business/industry
        2. Including niche-specific hashtags for targeted reach
        3. Balancing popular vs. less competitive hashtags
        4. Ensuring platform-specific hashtag strategies
        5. Maintaining relevance to the post content
        
        Platform-specific hashtag guidelines:
        - Instagram: 20-30 hashtags, mix of popular and niche
        - Twitter: 1-2 hashtags, focus on trending topics
        - LinkedIn: 3-5 professional hashtags
        - Facebook: 1-2 hashtags, focus on community building
        - TikTok: 3-5 trending hashtags
        
        Return the posts with enhanced hashtag arrays and updated platform_optimized sections.
        Ensure all hashtags are relevant, properly formatted, and likely to increase engagement.
        """,
        description="Optimizes hashtags for social media posts to maximize reach and engagement",
        output_key="optimized_posts",
        tools=[optimize_hashtags]
    )

# --- Sequential Agent Orchestration ---

async def create_business_analysis_agent() -> SequentialAgent:
    """Creates the business analysis sequential agent."""
    url_agent = await create_url_analysis_agent()
    file_agent = await create_file_analysis_agent()
    context_agent = await create_business_context_agent()
    
    return SequentialAgent(
        name="BusinessAnalysisAgent",
        sub_agents=[url_agent, file_agent, context_agent],
        description="Comprehensive business analysis and context extraction workflow"
    )

async def create_content_generation_agent() -> SequentialAgent:
    """Creates the content generation sequential agent."""
    social_agent = await create_social_content_agent()
    hashtag_agent = await create_hashtag_optimization_agent()
    
    return SequentialAgent(
        name="ContentGenerationAgent",
        sub_agents=[social_agent, hashtag_agent],
        description="Multi-format social media content generation and optimization workflow"
    )

# --- Root Marketing Orchestrator ---

async def create_marketing_orchestrator_agent() -> SequentialAgent:
    """Creates the root marketing orchestrator agent."""
    logger.info("Initializing Marketing Orchestrator Agent...")
    
    # Create sub-agents
    business_agent = await create_business_analysis_agent()
    content_agent = await create_content_generation_agent()
    
    # Create root orchestrator
    orchestrator = SequentialAgent(
        name="MarketingOrchestratorAgent",
        sub_agents=[business_agent, content_agent],
        description="Master orchestrator for complete marketing campaign workflow that coordinates business analysis and content generation"
    )
    
    logger.info(f"Marketing Orchestrator Agent initialized with {len(orchestrator.sub_agents)} sub-agents")
    return orchestrator

# --- Utility Functions ---

async def execute_campaign_workflow(
    business_description: str,
    objective: str,
    target_audience: str,
    campaign_type: str,
    creativity_level: int,
    post_count: int = 9,
    business_website: Optional[str] = None,
    about_page_url: Optional[str] = None,
    product_service_url: Optional[str] = None,
    uploaded_files: Optional[List[Dict[str, Any]]] = None,
    campaign_id: Optional[str] = None,
    session_id: Optional[str] = None,
    isolation_key: Optional[str] = None,
    campaign_guidance: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Root function to execute the complete ADK-based marketing campaign workflow.
    This orchestrates business analysis, content generation, and agentic visual content generation.
    """
    start_time = time.time()
    campaign_id = campaign_id or str(uuid.uuid4())
    logger.info(f"🚀 Starting campaign workflow for campaign_id: {campaign_id}")

    try:
        # Step 1: Business Analysis
        # CRITICAL FIX: Use URLAnalysisAgent when URLs are provided, fallback to description analysis
        business_analysis = await _comprehensive_business_analysis(
            business_description=business_description,
            target_audience=target_audience,
            objective=objective,
            campaign_type=campaign_type,
            business_website=business_website,
            about_page_url=about_page_url,
            product_service_url=product_service_url
        )
        if not business_analysis:
            logger.error(f"Business analysis failed for campaign {campaign_id}.")
            return {"error": "Business analysis could not be completed."}
        
        # Step 1.5: Merge Frontend Campaign Guidance
        # If campaign_guidance is provided from the frontend (e.g., from AI Campaign Summary),
        # merge it with the extracted business analysis
        if campaign_guidance:
            logger.info(f"🎨 Merging frontend campaign guidance with business analysis: {list(campaign_guidance.keys())}")
            business_analysis["campaign_guidance"] = campaign_guidance
            
            # Log the merged guidance for debugging
            if campaign_guidance.get('creative_direction'):
                logger.info(f"🎭 Creative Direction: {campaign_guidance['creative_direction'][:100]}...")
            if campaign_guidance.get('visual_style'):
                logger.info(f"🎨 Visual Style: {campaign_guidance['visual_style']}")
        else:
            logger.info("📋 No frontend campaign guidance provided, using extracted analysis only")
        
        # Build the context for the content generation agents
        context = {
            "business_description": business_description, "objective": objective,
            "target_audience": target_audience, "campaign_type": campaign_type,
            "creativity_level": creativity_level, "post_count": post_count,
            "business_website": business_website, "about_page_url": about_page_url,
            "product_service_url": product_service_url, "uploaded_files": uploaded_files,
            "campaign_id": campaign_id,
        }

        # Step 2: Content Generation (Text)
        # This agent generates the social media post text based on the analysis
        generated_content_raw = await _generate_real_social_content(business_analysis, context)
        
        # Step 3: Format Generated Content
        # This structures the raw LLM output into the application's data models
        formatted_posts = _format_generated_content({"generated_content": generated_content_raw}, context, business_analysis)

        workflow_result = {
            "business_analysis": business_analysis,
            "generated_content": formatted_posts,
            "success": True
        }

        # Step 4: Agentic Visual Content Generation
        if VISUAL_AGENT_AVAILABLE and formatted_posts:
            logger.info("🧠 Engaging ADK VisualContentOrchestratorAgent for visual generation...")
            visual_orchestrator = VisualContentOrchestratorAgent()
            
            # Use the detailed analysis as the context for the visual agents
            visual_business_context = business_analysis.get("business_context", business_analysis)
            
            visual_result = await visual_orchestrator.generate_visual_content_for_posts(
                social_posts=formatted_posts,
                business_context=visual_business_context,
                campaign_objective=objective,
                campaign_guidance=business_analysis.get("campaign_guidance", {}),
                campaign_id=campaign_id
            )
            
            workflow_result["generated_content"] = visual_result.get("posts_with_visuals", formatted_posts)
            workflow_result["visual_generation_metadata"] = visual_result.get("generation_metadata", {})
            logger.info("✅ Visual content generation complete. Posts updated with media URLs.")
        else:
            logger.warning("Visual agent not available or no text posts generated, skipping visual content.")

        processing_time = time.time() - start_time
        workflow_result["total_processing_time"] = processing_time
        logger.info(f"✅ Campaign workflow for {campaign_id} completed in {processing_time:.2f} seconds.")
        return workflow_result

    except Exception as e:
        logger.error(f"FATAL: Campaign workflow failed for campaign_id {campaign_id}: {e}", exc_info=True)
        return {
            "error": f"An unexpected error occurred in the campaign workflow: {str(e)}",
            "campaign_id": campaign_id
        }

async def _comprehensive_business_analysis(
    business_description: str,
    target_audience: str,
    objective: str,
    campaign_type: str,
    business_website: Optional[str] = None,
    about_page_url: Optional[str] = None,
    product_service_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Comprehensive business analysis using URLAnalysisAgent when URLs are available,
    otherwise fallback to description-based analysis.
    """
    
    # Collect all available URLs
    urls_to_analyze = []
    if business_website:
        urls_to_analyze.append(business_website)
    if about_page_url:
        urls_to_analyze.append(about_page_url)
    if product_service_url:
        urls_to_analyze.append(product_service_url)
    
    # If URLs are available, use the URLAnalysisAgent for comprehensive analysis
    if urls_to_analyze:
        logger.info(f"🔍 Using URLAnalysisAgent to analyze {len(urls_to_analyze)} URLs")
        try:
            url_analysis_agent = URLAnalysisAgent()
            url_analysis_result = await url_analysis_agent.analyze_urls(
                urls=urls_to_analyze,
                analysis_type="comprehensive"
            )
            
            # Extract the business analysis from URL analysis result
            if url_analysis_result and url_analysis_result.get("business_analysis"):
                business_analysis = url_analysis_result["business_analysis"]
                
                # Enhance with campaign-specific context
                business_analysis["target_audience"] = target_audience
                business_analysis["objective"] = objective
                business_analysis["campaign_type"] = campaign_type
                business_analysis["business_description"] = business_description
                
                logger.info(f"✅ URL analysis complete for {business_analysis.get('company_name', 'business')}")
                logger.info(f"   Industry: {business_analysis.get('industry', 'N/A')}")
                logger.info(f"   Suggested Tags: {len(business_analysis.get('suggested_tags', []))}")
                
                return business_analysis
            else:
                logger.warning("URL analysis returned no business analysis, falling back to description analysis")
        except Exception as e:
            logger.error(f"URLAnalysisAgent failed: {e}, falling back to description analysis")
    
    # Fallback to description-based analysis
    logger.info("📝 Using description-based business analysis (no URLs provided or URL analysis failed)")
    return await _extract_business_context_from_description(
        business_description, target_audience, objective, campaign_type
    )

async def _extract_business_context_from_description(
    business_description: str,
    target_audience: str,
    objective: str,
    campaign_type: str
) -> Dict[str, Any]:
    """Extract detailed business context from business description using AI analysis."""
    
    try:
        if GEMINI_API_KEY:
            import google.genai as genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            
            analysis_prompt = f"""
            Analyze this business description and extract detailed business context for marketing campaign generation:
            
            Business Description: "{business_description}"
            Target Audience: "{target_audience}"
            Campaign Objective: "{objective}"
            Campaign Type: "{campaign_type}"
            
            Extract and provide:
            1. Company name (if mentioned, otherwise "Your Company")
            2. Industry classification (be specific - e.g., "Custom T-shirt Printing", "Italian Restaurant", "Fitness Training")
            3. Key products/services offered
            4. Target demographic details (age, interests, lifestyle)
            5. Brand voice and personality
            6. Visual elements that would represent this business
            7. Competitive advantages
            8. Market positioning
            
            Format as JSON:
            {{
                "company_name": "extracted or inferred company name",
                "industry": "specific industry classification",
                "business_description": "{business_description}",
                "target_audience": "{target_audience}",
                "products_services": ["list of key offerings"],
                "brand_voice": "professional/casual/creative/etc",
                "visual_elements": ["specific visual concepts that represent this business"],
                "competitive_advantages": ["key differentiators"],
                "market_positioning": "how this business positions itself",
                "demographic_details": {{
                    "age_range": "inferred age range",
                    "interests": ["relevant interests"],
                    "lifestyle": "lifestyle characteristics"
                }}
            }}
            """
            
            response = client.models.generate_content(
                model=model,
                contents=analysis_prompt
            )
            
            # Parse JSON response
            import json
            import re
            
            response_text = response.text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    business_context = json.loads(json_match.group())
                    logger.info(f"Extracted business context for {business_context.get('company_name', 'Unknown')} in {business_context.get('industry', 'Unknown')} industry")
                    return business_context
                except json.JSONDecodeError:
                    logger.warning("Failed to parse business context JSON")
        
        # Fallback: Enhanced manual extraction
        return _manual_business_context_extraction(business_description, target_audience, objective)
        
    except Exception as e:
        logger.error(f"Business context extraction failed: {e}")
        return _manual_business_context_extraction(business_description, target_audience, objective)

def _manual_business_context_extraction(
    business_description: str,
    target_audience: str,
    objective: str
) -> Dict[str, Any]:
    """Manual business context extraction with industry-specific logic."""
    
    description_lower = business_description.lower()
    
    # Industry detection
    if any(keyword in description_lower for keyword in ['t-shirt', 'tshirt', 'apparel', 'clothing', 'print', 'custom']):
        industry = "Custom T-shirt Printing"
        visual_elements = ["people wearing custom t-shirts", "printing process", "design showcase", "happy customers in branded apparel"]
        brand_voice = "creative and fun"
    elif any(keyword in description_lower for keyword in ['restaurant', 'food', 'dining', 'kitchen', 'chef', 'cuisine']):
        industry = "Restaurant & Food Service"
        visual_elements = ["food presentation", "dining atmosphere", "chef preparing dishes", "satisfied customers eating"]
        brand_voice = "warm and inviting"
    elif any(keyword in description_lower for keyword in ['fitness', 'gym', 'training', 'workout', 'health']):
        industry = "Fitness & Health"
        visual_elements = ["people exercising", "trainer-client interactions", "gym equipment", "fitness transformations"]
        brand_voice = "motivational and energetic"
    elif any(keyword in description_lower for keyword in ['tech', 'software', 'digital', 'app', 'platform']):
        industry = "Technology Services"
        visual_elements = ["professionals using technology", "modern office environments", "digital interfaces", "team collaboration"]
        brand_voice = "innovative and professional"
    else:
        industry = "Professional Services"
        visual_elements = ["professional business environment", "team collaboration", "client satisfaction", "service delivery"]
        brand_voice = "professional and trustworthy"
    
    return {
        "company_name": "Your Company",
        "industry": industry,
        "business_description": business_description,
        "target_audience": target_audience,
        "products_services": ["Core service offering", "Customer solutions"],
        "brand_voice": brand_voice,
        "visual_elements": visual_elements,
        "competitive_advantages": ["Quality service", "Customer focus", "Innovation"],
        "market_positioning": f"Trusted {industry.lower()} provider",
        "demographic_details": {
            "age_range": "25-45",
            "interests": ["quality", "value", "service"],
            "lifestyle": "active and engaged"
        }
    }

async def _generate_real_social_content(business_analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate real social media content using Gemini AI, conforming to ADR-020.
    
    ⚠️  CRITICAL: ADR-020 SCHEMA ENFORCEMENT ⚠️
    This function implements the DEFINITIVE solution for consistent JSON schema enforcement.
    
    ENFORCED OUTPUT SCHEMA (ADR-020 Canonical):
    {
      "social_media_posts": [
        {
          "id": "post_001",
          "type": "text_url" | "text_image" | "text_video",
          "content": "100-200 word engaging post content",
          "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
          "image_prompt": null | "detailed AI image generation prompt",
          "video_prompt": null | "detailed AI video generation prompt"
        }
      ]
    }
    
    DYNAMIC CAMPAIGN GUIDANCE INTEGRATION:
    This function dynamically incorporates campaign guidance from the frontend:
    - creative_direction: Overall creative vision and brand aesthetic
    - visual_style: Photography style, mood, lighting preferences  
    - content_themes: Primary themes and target context
    - imagen_prompts: Technical specifications for image generation
    - veo_prompts: Technical specifications for video generation
    
    ❌ ANTI-PATTERNS PREVENTED:
    - Legacy "text_url_posts", "text_image_posts", "text_video_posts" structure
    - Inconsistent JSON formatting with control characters  
    - Missing or incorrect post type specifications
    - Non-canonical key names or structures
    
    ROBUST JSON PARSING STRATEGY:
    1. CONTROL CHAR CLEANING: Remove JSON-breaking control characters
    2. DIRECT PARSING: Parse cleaned JSON directly if properly formatted
    3. MARKDOWN EXTRACTION: Handle ```json blocks if present
    4. REGEX EXTRACTION: Find JSON objects in mixed content
    5. FALLBACK PARSING: Try original text if cleaning fails
    
    Args:
        business_analysis: Business context including company info and campaign guidance
        context: Campaign parameters (objective, audience, post_count, etc.)
        
    Returns:
        Dict containing "social_media_posts" array in ADR-020 format
        Returns {"social_media_posts": []} on any parsing failure
        
    Raises:
        Logs errors but does not raise exceptions (returns empty result on failure)
    """
    try:
        import google.genai as genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        
        company_name = business_analysis.get('company_name', 'Your Company')
        industry = business_analysis.get('industry', 'Professional Services')
        objective = context['objective']
        target_audience = context['target_audience']
        campaign_type = context['campaign_type']
        post_count = context.get('post_count', 9)
        
        # Calculate posts per type (divide evenly, with remainder distributed)
        posts_per_type = post_count // 3
        remainder = post_count % 3
        text_url_count = posts_per_type + (1 if remainder > 0 else 0)
        text_image_count = posts_per_type + (1 if remainder > 1 else 0)
        text_video_count = posts_per_type
        
        # This prompt is architecturally significant and enforces ADR-020 with MAXIMUM STRICTNESS.
        content_prompt = f"""=== STRICT JSON SCHEMA ENFORCEMENT (ADR-020) ===

YOU ARE A JSON-ONLY CONTENT GENERATOR. YOUR RESPONSE MUST BE EXCLUSIVELY A SINGLE, VALID JSON OBJECT.

FORBIDDEN ACTIONS:
- NO markdown code blocks (```json)
- NO explanatory text before or after the JSON
- NO comments or annotations
- NO variations from the specified schema

REQUIRED RESPONSE FORMAT:
You must respond with ONLY this exact JSON structure:

{{
  "social_media_posts": [
    {{
      "id": "post_001",
      "type": "text_url",
      "content": "Your engaging post content here...",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "image_prompt": null,
      "video_prompt": null
    }},
    {{
      "id": "post_002", 
      "type": "text_image",
      "content": "Your visual post content here...",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "image_prompt": "Detailed image generation prompt here",
      "video_prompt": null
    }},
    {{
      "id": "post_003",
      "type": "text_video", 
      "content": "Your video post content here...",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "image_prompt": null,
      "video_prompt": "Detailed video generation prompt here"
    }}
  ]
}}

BUSINESS CONTEXT FOR CONTENT GENERATION:
- Company: {company_name}
- Industry: {industry} 
- Objective: {objective}
- Target Audience: {target_audience}
- Campaign Type: {campaign_type}
- Brand Voice: {business_analysis.get('brand_voice', 'Professional')}

MANDATORY REQUIREMENTS:
1. Generate exactly {post_count} posts total
2. Create {text_url_count} posts with type "text_url" (image_prompt: null, video_prompt: null)
3. Create {text_image_count} posts with type "text_image" (image_prompt: detailed string, video_prompt: null)
4. Create {text_video_count} posts with type "text_video" (image_prompt: null, video_prompt: detailed string)
5. Each post must have unique id starting with "post_"
6. Content must be 100-200 words, engaging and relevant
7. Include 3-5 relevant hashtags per post
8. Image prompts must be detailed descriptions for AI image generation
9. Video prompts must be detailed descriptions for AI video generation

YOUR RESPONSE MUST START WITH {{ AND END WITH }} - NOTHING ELSE."""
        
        logger.debug(f"Sending content generation request to Gemini with {post_count} posts")
        response = client.models.generate_content(model=model, contents=content_prompt)
        
        import json
        import re
        response_text = response.text.strip()
        
        # Clean control characters that break JSON parsing
        cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_text)
        
        # Log the raw response for debugging
        logger.debug(f"Raw Gemini response: {response_text[:500]}...")
        logger.debug(f"Cleaned response: {cleaned_text[:500]}...")
        
        # Try to extract JSON - be more aggressive about finding it
        json_data = None
        
        # Method 1: Direct parse if it starts with { (use cleaned text)
        if cleaned_text.startswith('{'):
            try:
                json_data = json.loads(cleaned_text)
                logger.debug("✅ Successfully parsed JSON directly from cleaned response")
            except json.JSONDecodeError as e:
                logger.warning(f"Direct JSON parse failed: {e}")
        
        # Method 2: Extract from markdown blocks (use cleaned text)
        if not json_data:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', cleaned_text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    logger.debug("✅ Successfully extracted JSON from markdown block")
                except json.JSONDecodeError as e:
                    logger.warning(f"Markdown JSON parse failed: {e}")
        
        # Method 3: Find any JSON object in the response (use cleaned text)
        if not json_data:
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(0))
                    logger.debug("✅ Successfully extracted JSON object from cleaned response")
                except json.JSONDecodeError as e:
                    logger.warning(f"Generic JSON parse failed: {e}")
                    
        # Method 4: Fallback to original text if cleaned version fails
        if not json_data:
            logger.info("🔄 Trying fallback parsing with original response text...")
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(0))
                    logger.debug("✅ Fallback JSON parse successful with original text")
                except json.JSONDecodeError as e:
                    logger.warning(f"Fallback JSON parse failed: {e}")
        
        # Validate the JSON structure
        if json_data:
            if "social_media_posts" in json_data and isinstance(json_data["social_media_posts"], list):
                posts_count = len(json_data["social_media_posts"])
                logger.info(f"✅ Successfully generated {posts_count} social media posts")
                return json_data
            else:
                logger.error(f"JSON response missing 'social_media_posts' key or invalid structure. Keys: {list(json_data.keys())}")
        
        # If all parsing failed, log and return empty result
        logger.error(f"❌ All JSON parsing methods failed. Raw response: {response_text}")
        return {"social_media_posts": []}
        
    except Exception as e:
        logger.error(f"Real content generation failed: {e}", exc_info=True)
        return {"social_media_posts": []}

def _format_generated_content(content_data: Dict[str, Any], context: Dict[str, Any], business_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Formats the structured content from the LLM into the application's data models, conforming to ADR-020.
    
    ⚠️  CRITICAL: ADR-020 SCHEMA COMPLIANCE ⚠️
    This function MUST parse the canonical ADR-020 schema format:
    
    EXPECTED INPUT SCHEMA (ADR-020 Canonical Format):
    {
      "social_media_posts": [
        {
          "id": "string - Unique identifier (e.g., 'post_001')",
          "type": "string - MUST be 'text_url', 'text_image', or 'text_video'",
          "content": "string - Main post content (100-200 words)",
          "hashtags": ["string", "string", ...] - Array of hashtags,
          "image_prompt": "string | null - Detailed AI image prompt if type='text_image'",
          "video_prompt": "string | null - Detailed AI video prompt if type='text_video'"
        }
      ]
    }
    
    ❌ FORBIDDEN FORMATS (will trigger fallback parsing):
    - "text_url_posts", "text_image_posts", "text_video_posts" (legacy format)
    - "generated_content" (nested format)
    - Direct post arrays at root level
    
    PARSING STRATEGY:
    1. PRIMARY: Parse ADR-020 compliant "social_media_posts" array
    2. FALLBACK: Convert legacy formats to ADR-020 structure
    3. FALLBACK: Handle nested "generated_content" structures
    4. FALLBACK: Process direct post arrays
    
    This function implements comprehensive parsing with multiple fallback strategies
    to maintain backward compatibility while enforcing the ADR-020 standard.
    
    Args:
        content_data: Raw LLM response data (should contain "social_media_posts")
        context: Campaign context (objective, audience, etc.)
        business_analysis: Business context and campaign guidance
        
    Returns:
        List of formatted post dictionaries ready for visual content generation
        
    Raises:
        Logs errors but does not raise exceptions (returns empty list on failure)
    """
    logger.info("--- STARTING CONTENT FORMATTING (ADR-020 COMPLIANT) ---")
    formatted_posts = []
    
    # Method 1: ADR-020 compliant format with "social_media_posts" key
    if "social_media_posts" in content_data and isinstance(content_data["social_media_posts"], list):
        posts_list = content_data["social_media_posts"]
        logger.info(f"✅ Found ADR-020 compliant 'social_media_posts' key with {len(posts_list)} items.")
        for post_data in posts_list:
            if isinstance(post_data, dict):
                post_type = post_data.get("type", "text_url")
                formatted_post = _format_single_post(post_data, post_type, business_analysis)
                formatted_posts.append(formatted_post)
    
    # Method 2: Legacy format with separate post type arrays (fallback)
    elif any(key in content_data for key in ["text_url_posts", "text_image_posts", "text_video_posts"]):
        logger.warning("⚠️ Found legacy format with separate post arrays. Converting to ADR-020 format.")
        
        # Process each post type array
        for post_type_key in ["text_url_posts", "text_image_posts", "text_video_posts"]:
            if post_type_key in content_data and isinstance(content_data[post_type_key], list):
                post_type = post_type_key.replace("_posts", "")  # "text_url_posts" -> "text_url"
                for post_data in content_data[post_type_key]:
                    if isinstance(post_data, dict):
                        # Ensure post has the type field for consistency
                        post_data["type"] = post_type
                        formatted_post = _format_single_post(post_data, post_type, business_analysis)
                        formatted_posts.append(formatted_post)
        
        logger.info(f"✅ Successfully converted {len(formatted_posts)} posts from legacy format.")
    
    # Method 3: Check for "generated_content" key (another fallback)
    elif "generated_content" in content_data:
        logger.warning("⚠️ Found 'generated_content' key. Attempting to parse nested structure.")
        generated_content = content_data["generated_content"]
        
        # Recursively parse the nested content
        if isinstance(generated_content, dict):
            formatted_posts = _format_generated_content(generated_content, context, business_analysis)
        elif isinstance(generated_content, list):
            # Assume it's a list of posts
            for post_data in generated_content:
                if isinstance(post_data, dict):
                    post_type = post_data.get("type", "text_url")
                    formatted_post = _format_single_post(post_data, post_type, business_analysis)
                    formatted_posts.append(formatted_post)
    
    # Method 4: Direct post array at root level (final fallback)
    elif isinstance(content_data, list):
        logger.warning("⚠️ Found direct post list at root level. Processing as posts array.")
        for post_data in content_data:
            if isinstance(post_data, dict):
                post_type = post_data.get("type", "text_url")
                formatted_post = _format_single_post(post_data, post_type, business_analysis)
                formatted_posts.append(formatted_post)
    
    else:
        logger.error(f"❌ Could not parse content data. Keys found: {list(content_data.keys()) if isinstance(content_data, dict) else 'Not a dictionary'}")
        logger.debug(f"Content data structure: {type(content_data)} - {str(content_data)[:200]}...")

    logger.info(f"--- FINISHED CONTENT FORMATTING: Formatted {len(formatted_posts)} posts ---")
    return formatted_posts

def _format_single_post(post_data: Dict[str, Any], post_type: str, business_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a single post from agent response into the application's internal data model.
    
    ⚠️  CRITICAL: ADR-020 SCHEMA COMPLIANCE ⚠️
    This function converts individual post data from the ADR-020 canonical format into
    the application's internal post representation for visual content generation.
    
    EXPECTED INPUT (from ADR-020 "social_media_posts" array):
    {
      "id": "post_001",
      "type": "text_url" | "text_image" | "text_video", 
      "content": "100-200 word post content",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "image_prompt": null | "detailed image prompt",
      "video_prompt": null | "detailed video prompt"
    }
    
    OUTPUT FORMAT (Application Internal Model):
    {
      "id": "string - Post identifier",
      "type": "string - Normalized post type (text_url, text_image, text_video)",
      "content": "string - Post content",
      "url": "string | None - Associated URL if applicable",
      "image_prompt": "string | None - Image generation prompt",
      "image_url": "None - Placeholder for generated image URL",
      "video_prompt": "string | None - Video generation prompt", 
      "video_url": "None - Placeholder for generated video URL",
      "hashtags": "List[str] - Array of hashtags",
      "platform_optimized": "Dict - Platform-specific optimizations",
      "engagement_score": "float - Predicted engagement score",
      "selected": "bool - User selection status",
      "business_context": "Dict - Business analysis context"
    }
    
    TYPE NORMALIZATION:
    - "text_url_posts" or "text_url" → "text_url"
    - "text_image_posts" or "text_image" → "text_image" 
    - "text_video_posts" or "text_video" → "text_video"
    - Default fallback → "text_url"
    
    Args:
        post_data: Individual post data from LLM response
        post_type: Post type string (may be legacy format)
        business_analysis: Business context for embedding in post
        
    Returns:
        Formatted post dictionary ready for visual content generation
    """
    post_id = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(str(post_data))}"
    
    # Determine post type from source
    if post_type == 'text_url_posts' or post_type == 'text_url':
        type_value = "text_url"
    elif post_type == 'text_image_posts' or post_type == 'text_image':
        type_value = "text_image"
    elif post_type == 'text_video_posts' or post_type == 'text_video':
        type_value = "text_video"
    else:
        type_value = "text_url"
    
    # Safely parse platform_optimized content
    platform_optimized_raw = post_data.get("platform_optimized", {})
    platform_optimized_data = {}
    if isinstance(platform_optimized_raw, str):
        try:
            platform_optimized_data = json.loads(platform_optimized_raw)
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode platform_optimized JSON for post {post_id}")
            platform_optimized_data = {}
    elif isinstance(platform_optimized_raw, dict):
        platform_optimized_data = platform_optimized_raw
    
    return {
        "id": post_data.get("id", post_id),
        "type": type_value,
        "content": post_data.get("content", "No content generated."),
        "url": post_data.get("url"),
        "image_prompt": post_data.get("image_prompt"),
        "image_url": None,  # Will be set when visual content is generated
        "video_prompt": post_data.get("video_prompt"),
        "video_url": None,  # Will be set when visual content is generated
        "hashtags": post_data.get("hashtags", []),
        "platform_optimized": platform_optimized_data,
        "engagement_score": post_data.get("engagement_score", 0.8),
        "selected": post_data.get("selected", False),
        "business_context": business_analysis
    } 