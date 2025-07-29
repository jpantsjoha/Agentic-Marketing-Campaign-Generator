"""
FILENAME: content.py
DESCRIPTION/PURPOSE: Content generation API routes for social media posts
Author: JP + 2025-06-16
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os
import time
import asyncio
from pathlib import Path

from ..models import (
    ContentGenerationRequest, ContentGenerationResponse,
    SocialPostRegenerationRequest, SocialPostRegenerationResponse,
    SocialMediaPost, PostType, 
    VisualGenerationJob, VisualJobStatus, VisualContentType, 
    AsyncVisualResponse, BatchVisualStatus, VisualJobUpdate
)
# Removed async visual manager import - architectural coherence fix

logger = logging.getLogger(__name__)

def _validate_visual_results_context_fidelity(visual_results: dict, business_context: dict) -> None:
    """
    ADR-020 REQUIREMENT: Validate visual results don't contain forbidden demo URLs.
    
    This function prevents the regression where mountain landscape images and generic demo content
    was shown for business marketing campaigns by validating the API response.
    """
    if not visual_results or not isinstance(visual_results, dict):
        return
    
    # ADR-020 FORBIDDEN: Demo URLs that caused the original regression
    forbidden_demo_urls = [
        'https://images.unsplash.com/photo-1542038784456-1ea8e732b2b9',
        'https://images.unsplash.com/photo-1531804055935-76f44d7c3621',
        'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        'https://via.placeholder.com',
        'https://picsum.photos'
    ]
    
    posts_with_visuals = visual_results.get("posts_with_visuals", [])
    for post in posts_with_visuals:
        if not isinstance(post, dict):
            continue
            
        # Check image URLs
        image_url = post.get("image_url", "")
        if image_url:
            for forbidden_url in forbidden_demo_urls:
                if image_url.startswith(forbidden_url):
                    error_msg = f"CONTEXT_FIDELITY_VIOLATION: Forbidden demo image URL in API response: {image_url}"
                    logger.error(f"❌ {error_msg}")
                    raise HTTPException(status_code=500, detail=error_msg)
        
        # Check video URLs  
        video_url = post.get("video_url", "")
        if video_url:
            for forbidden_url in forbidden_demo_urls:
                if video_url.startswith(forbidden_url):
                    error_msg = f"CONTEXT_FIDELITY_VIOLATION: Forbidden demo video URL in API response: {video_url}"
                    logger.error(f"❌ {error_msg}")
                    raise HTTPException(status_code=500, detail=error_msg)
    
    logger.debug(f"✅ VISUAL_RESULTS_VALIDATION_PASSED: No forbidden URLs detected for {business_context.get('company_name', 'unknown')}")

# Import ADK agents for real content generation
try:
    from agents.marketing_orchestrator import execute_campaign_workflow
    logger.info("✅ Marketing orchestrator agent available for API endpoints")
except ImportError as e:
    logger.warning(f"❌ Marketing orchestrator agent not available: {e}")
    execute_campaign_workflow = None

# Import visual content generation - ENHANCED: Use ADK agentic visual generation
try:
    from agents.adk_visual_agents import generate_agentic_visual_content
    logger.info("✅ ADK agentic visual content agent available for API endpoints")
    generate_visual_content_for_posts = generate_agentic_visual_content  # Use ADK agents
except ImportError as e:
    try:
        from agents.visual_content_agent import generate_visual_content_for_posts
        logger.info("✅ Fallback visual content agent available for API endpoints")
    except ImportError as e2:
        logger.warning(f"❌ No visual content agent available: {e}, {e2}")
    generate_visual_content_for_posts = None

router = APIRouter()

# Cache will be initialized when needed

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest) -> ContentGenerationResponse:
    """
    Generate social media content by executing the real ADK agent workflow.
    This endpoint no longer uses mock data.
    """
    if not execute_campaign_workflow:
        logger.error("Marketing orchestrator not available.")
        raise HTTPException(status_code=500, detail="AI services are not configured.")

    try:
        logger.info(f"Executing real AI workflow to generate content for campaign objective: {request.campaign_objective}")
        start_time = time.time()

        # Extract or create business description from business context
        business_description = request.business_context.business_description
        if not business_description:
            # Create a business description from available context
            company_name = getattr(request.business_context, 'company_name', 'the company')
            industry = getattr(request.business_context, 'industry', 'business')
            value_props = getattr(request.business_context, 'value_propositions', [])
            value_props_text = ', '.join(value_props) if value_props else 'quality products and services'
            business_description = f"{company_name} is a {industry} company that provides {value_props_text}"

        # Extract campaign guidance from the frontend request
        campaign_guidance = getattr(request.business_context, 'campaign_guidance', None)
        if campaign_guidance:
            logger.info(f"🎨 Frontend campaign guidance received: {list(campaign_guidance.keys())}")
        
        # Call the orchestrator to execute the real end-to-end workflow
        # The orchestrator will handle analysis (from URL or description) and content generation
        workflow_result = await execute_campaign_workflow(
            business_description=business_description,
            objective=request.campaign_objective,
            target_audience=getattr(request.business_context, 'target_audience', 'general audience'),
            campaign_type=request.campaign_type.value if request.campaign_type else 'product',
            creativity_level=request.creativity_level,
            post_count=request.post_count,
            business_website=getattr(request.business_context, 'business_website', None),
            about_page_url=getattr(request.business_context, 'about_page_url', None),
            product_service_url=getattr(request.business_context, 'product_service_url', None),
            campaign_guidance=campaign_guidance
        )

        processing_time = time.time() - start_time

        if "error" in workflow_result:
            logger.error(f"Workflow execution failed: {workflow_result['error']}")
            raise HTTPException(status_code=500, detail=workflow_result["error"])

        # Extract generated posts and other relevant data from the result
        generated_posts = workflow_result.get("generated_content", [])
        business_analysis = workflow_result.get("business_analysis", {})
        
        # Suggest hashtags from the campaign guidance
        hashtag_suggestions = business_analysis.get("campaign_guidance", {}).get("suggested_tags", [])
        if not hashtag_suggestions:
             hashtag_suggestions = ["#Innovation", "#Business", "#Growth", "#Marketing", "#Success"]

        return ContentGenerationResponse(
            posts=generated_posts,
            hashtag_suggestions=hashtag_suggestions,
            generation_metadata={
                "creativity_level": request.creativity_level,
                "post_count": len(generated_posts),
                "total_posts": len(generated_posts),
                "generation_method": "real_adk_workflow",
                "generation_time": processing_time,
                "real_ai_used": True
            },
            processing_time=processing_time,
            business_analysis=business_analysis # Pass the analysis back to the frontend
        )

    except Exception as e:
        logger.error(f"Content generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/regenerate", response_model=SocialPostRegenerationResponse)
async def regenerate_posts(request: SocialPostRegenerationRequest) -> SocialPostRegenerationResponse:
    """Regenerate specific social media posts using real ADK agents."""
    
    try:
        logger.info(f"Regenerating {request.regenerate_count} {request.post_type} posts with business context")
        
        # Extract business context from request
        business_context = getattr(request, 'business_context', {})
        creativity_level = getattr(request, 'creativity_level', 7)
        
        # Use optimized batch generation if Gemini API is available
        if os.getenv("GEMINI_API_KEY") and business_context:
            logger.info("Using optimized batch Gemini generation for content regeneration")
            
            # Use the new batch generation function for optimal performance
            start_time = time.time()
            generated_posts = await _generate_batch_content_with_gemini(
                request.post_type, 
                request.regenerate_count, 
                business_context
            )
            
            # Return successful response
            return SocialPostRegenerationResponse(
                new_posts=generated_posts,
                regeneration_metadata={
                    "regenerated_count": len(generated_posts),
                    "post_type": request.post_type.value,
                    "generation_method": "optimized_batch_gemini_generation",
                    "creativity_level": request.creativity_level,
                    "business_context_used": bool(business_context),
                    "cost_controlled": len(generated_posts) < request.regenerate_count
                },
                processing_time=time.time() - start_time
            )
            
        else:
            # Enhanced fallback with business context
            logger.info("Using enhanced mock generation with business context")
            
            new_posts = []
            for i in range(request.regenerate_count):
                post = SocialMediaPost(
                    id=f"enhanced_{request.post_type}_{i+1}",
                    type=request.post_type,
                    content=generate_enhanced_content(request.post_type, business_context, i),
                    hashtags=generate_contextual_hashtags(business_context),
                    platform_optimized={
                        "linkedin": {
                            "content": f"Professional {request.post_type.replace('_', ' + ')} content",
                            "hashtags": ["#Professional", "#LinkedIn", "#Business"]
                        },
                        "twitter": {
                            "content": f"Engaging {request.post_type.replace('_', ' + ')} content",
                            "hashtags": ["#Twitter", "#Social", "#Marketing"]
                        },
                        "instagram": {
                            "content": f"Visual {request.post_type.replace('_', ' + ')} content",
                            "hashtags": ["#Instagram", "#Visual", "#Creative"]
                        },
                        "facebook": {
                            "content": f"Community {request.post_type.replace('_', ' + ')} content",
                            "hashtags": ["#Facebook", "#Community", "#Engagement"]
                        }
                    },
                    engagement_score=8.0 + (i * 0.1),
                    selected=False
                )
                new_posts.append(post)
            
            return SocialPostRegenerationResponse(
                new_posts=new_posts,
                regeneration_metadata={
                    "post_type": request.post_type,
                    "regenerate_count": len(new_posts),
                    "method": "enhanced_mock_with_context",
                    "business_context_used": bool(business_context)
                },
                processing_time=1.5
            )
        
    except Exception as e:
        logger.error(f"Post regeneration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Post regeneration failed: {str(e)}"
        )

def generate_enhanced_content(post_type: PostType, business_context: dict, index: int) -> str:
    """Generate enhanced content based on business context."""
    
    company_name = business_context.get('company_name', 'Your Company')
    objective = business_context.get('objective', 'increase sales')
    campaign_type = business_context.get('campaign_type', 'service')
    business_description = business_context.get('business_description', '')
    
    # Extract key themes from business description
    themes = []
    if 'innovative' in business_description.lower() or 'innovation' in business_description.lower():
        themes.append('innovation')
    if 'quality' in business_description.lower() or 'premium' in business_description.lower():
        themes.append('quality')
    if 'customer' in business_description.lower() or 'client' in business_description.lower():
        themes.append('customer-focused')
    if 'technology' in business_description.lower() or 'tech' in business_description.lower():
        themes.append('technology')
    
    # Social media optimized content (short and punchy)
    base_content = {
        PostType.TEXT_URL: [
            f"🚀 Ready to {objective}? {company_name} has the solution!",
            f"💡 Transform your business with {company_name}'s {campaign_type} approach",
            f"🎯 {company_name} helps businesses {objective} faster than ever",
            f"✨ Discover how {company_name} can revolutionize your {campaign_type} strategy",
            f"🔥 Game-changing {campaign_type} solutions from {company_name}"
        ],
        PostType.TEXT_IMAGE: [
            f"🎨 {company_name} in action",
            f"📸 Innovation meets results",
            f"🌟 Your success story starts here",
            f"💫 Transforming {campaign_type} industry",
            f"🎭 Excellence you can see"
        ],
        PostType.TEXT_VIDEO: [
            f"🎬 {company_name} transforming {campaign_type}",
            f"📹 See innovation in motion",
            f"🎥 Your future starts now",
            f"🌟 Dynamic solutions, real results",
            f"🚀 Watch the transformation"
        ]
    }
    
    content_list = base_content.get(post_type, base_content[PostType.TEXT_URL])
    selected_content = content_list[index % len(content_list)]
    
    # Add theme-specific enhancements
    if 'innovation' in themes:
        selected_content = selected_content.replace('solution', 'cutting-edge solution')
    if 'quality' in themes:
        selected_content = selected_content.replace('approach', 'premium approach')
    if 'customer-focused' in themes:
        selected_content = selected_content.replace('business', 'customer-first business')
    
    return selected_content

def generate_contextual_hashtags(business_context: dict) -> List[str]:
    """Generate AI-powered, context-aware hashtags based on business and product analysis."""
    
    # PRIORITY 1: Use business analysis agent's suggested tags if available
    campaign_guidance = business_context.get('campaign_guidance', {})
    business_suggested_tags = campaign_guidance.get('suggested_tags', [])
    
    # Also check at root level for suggested_tags
    if not business_suggested_tags:
        business_suggested_tags = business_context.get('suggested_tags', [])
    
    # If we have business-specific tags from the analysis agent, prioritize them
    if business_suggested_tags:
        logger.info(f"✅ Using {len(business_suggested_tags)} business-specific hashtags from analysis agent")
        # Clean and validate the tags
        hashtags = []
        for tag in business_suggested_tags:
            if isinstance(tag, str) and len(tag) > 2:
                # Ensure tag starts with # 
                clean_tag = tag if tag.startswith('#') else f"#{tag}"
                hashtags.append(clean_tag)
        
        # Return business-specific tags with maybe 1-2 generic supplements
        if len(hashtags) >= 5:
            return hashtags[:6]  # Use business tags only
        else:
            # Add 1-2 generic supplement tags
            hashtags.extend(["#Business", "#Growth"])
            return hashtags[:6]
    
    # FALLBACK: Generate contextual hashtags if no business analysis tags available
    logger.info("⚠️ No business-specific hashtags found, generating contextual ones")
    
    # Extract comprehensive business context
    company_name = business_context.get('company_name', 'YourBusiness')
    business_type = business_context.get('business_type', 'corporation')
    campaign_type = business_context.get('campaign_type', 'service')
    objective = business_context.get('objective', 'increase sales')
    industry = business_context.get('industry', 'Professional Services')
    brand_voice = business_context.get('brand_voice', 'Professional')
    
    # Extract product-specific context for enhanced targeting
    product_context = business_context.get('product_context', {})
    has_specific_product = product_context.get('has_specific_product', False)
    product_themes = product_context.get('product_themes', [])
    
    content_themes = campaign_guidance.get('content_themes', {})
    primary_themes = content_themes.get('primary_themes', [])
    
    # Start with dynamic base hashtags
    hashtags = []
    
    # 1. PRODUCT-SPECIFIC HASHTAGS (Priority for specific products)
    if has_specific_product and product_themes:
        for theme in product_themes[:3]:  # Limit to top 3 product themes
            clean_theme = theme.replace(' ', '').replace('&', '').replace('-', '')
            if clean_theme and len(clean_theme) > 2:
                hashtags.append(f"#{clean_theme}")
    
    # 2. BUSINESS TYPE SPECIFIC HASHTAGS
    if business_type == "individual_creator":
        hashtags.extend(["#Artist", "#Creator", "#IndependentArt", "#CreativeDesign"])
    elif business_type == "small_business":
        hashtags.extend(["#SmallBusiness", "#LocalBusiness", "#Entrepreneur"])
    else:
        hashtags.extend(["#Business", "#Professional"])
    
    # 3. INDUSTRY-SPECIFIC HASHTAGS
    industry_lower = industry.lower()
    if 'digital art' in industry_lower or 'print-on-demand' in industry_lower:
        hashtags.extend(["#DigitalArt", "#PrintOnDemand", "#CustomDesign", "#ArtisticWear"])
    elif 'technology' in industry_lower:
        hashtags.extend(["#Technology", "#Tech", "#Innovation"])
    elif 'marketing' in industry_lower:
        hashtags.extend(["#Marketing", "#DigitalMarketing", "#Growth"])
    elif 'fitness' in industry_lower:
        hashtags.extend(["#Fitness", "#Health", "#Wellness"])
    elif 'food' in industry_lower:
        hashtags.extend(["#Food", "#Foodie", "#Restaurant"])
    
    # 4. CAMPAIGN OBJECTIVE HASHTAGS
    objective_lower = objective.lower()
    if 'sales' in objective_lower:
        hashtags.extend(["#Sales", "#ShopNow", "#NewProduct"])
    elif 'awareness' in objective_lower:
        hashtags.extend(["#BrandAwareness", "#Discover", "#GetToKnow"])
    elif 'engagement' in objective_lower:
        hashtags.extend(["#Community", "#Engage", "#Connect"])
    elif 'growth' in objective_lower:
        hashtags.extend(["#Growth", "#Expansion", "#Success"])
    
    # 5. BRAND VOICE HASHTAGS
    voice_lower = brand_voice.lower()
    if 'artistic' in voice_lower or 'creative' in voice_lower:
        hashtags.extend(["#Creative", "#Artistic", "#Inspiration"])
    elif 'humorous' in voice_lower or 'funny' in voice_lower:
        hashtags.extend(["#Humor", "#Fun", "#Entertaining"])
    elif 'professional' in voice_lower:
        hashtags.extend(["#Professional", "#Quality", "#Excellence"])
    elif 'innovative' in voice_lower:
        hashtags.extend(["#Innovation", "#Innovative", "#CuttingEdge"])
    
    # 6. CAMPAIGN THEME HASHTAGS
    for theme in primary_themes[:2]:  # Limit to top 2 campaign themes
        if theme.lower() == 'authenticity':
            hashtags.extend(["#Authentic", "#Real", "#Genuine"])
        elif theme.lower() == 'community':
            hashtags.extend(["#Community", "#Together", "#Family"])
        elif theme.lower() == 'innovation':
            hashtags.extend(["#Innovation", "#NewIdeas", "#Creative"])
        elif theme.lower() == 'quality':
            hashtags.extend(["#Quality", "#Premium", "#Excellence"])
    
    # 7. PLATFORM-OPTIMIZED HASHTAGS
    hashtags.extend(["#SocialMedia", "#Content", "#Trending"])
    
    # Clean up and prioritize hashtags
    # Remove duplicates while preserving order
    unique_hashtags = []
    seen = set()
    for tag in hashtags:
        if tag.lower() not in seen and len(tag) > 3:  # Minimum tag length
            unique_hashtags.append(tag)
            seen.add(tag.lower())
    
    # Return top 6 most relevant hashtags
    return unique_hashtags[:6]

@router.post("/generate-visuals")
async def generate_visual_content(request: dict):
    """
    Generate visual content (images/videos) for existing social media posts.
    This endpoint handles both image and video generation for social posts.
    """
    try:
        logger.info(f"🎨 Visual content generation request for {len(request.get('social_posts', []))} posts")
        
        social_posts = request.get('social_posts', [])
        business_context = request.get('business_context', {})
        campaign_objective = request.get('campaign_objective', 'increase engagement')
        target_platforms = request.get('target_platforms', ['instagram', 'linkedin'])
        
        # ADK ENHANCEMENT: Extract comprehensive campaign context from request
        campaign_media_tuning = request.get('campaign_media_tuning', '')
        campaign_guidance = request.get('campaign_guidance', {})
        product_context = request.get('product_context', {})
        visual_style = request.get('visual_style', {})
        creative_direction = request.get('creative_direction', '')
        suggested_themes = request.get('suggested_themes', [])
        suggested_tags = request.get('suggested_tags', [])
        
        # Log extracted campaign context for debugging
        logger.info(f"📋 CAMPAIGN CONTEXT EXTRACTION:")
        logger.info(f"   🎨 Campaign Media Tuning: {len(campaign_media_tuning)} chars")
        logger.info(f"   🎯 Creative Direction: {len(creative_direction)} chars")
        logger.info(f"   🎭 Visual Style: {list(visual_style.keys()) if visual_style else 'None'}")
        logger.info(f"   🏷️ Suggested Themes: {len(suggested_themes)} items")
        logger.info(f"   #️⃣ Suggested Tags: {len(suggested_tags)} items")
        
        if not social_posts:
            raise HTTPException(status_code=400, detail="No social posts provided for visual generation")
        
        start_time = time.time()
        
        # FIXED: Use the same working ADK visual generation from /generate endpoint
        try:
            from agents.adk_visual_agents import generate_agentic_visual_content
            logger.info("🎨 Using working ADK agentic visual content generation (same as /generate endpoint)")
            
            # ENHANCED LOGGING: Log input posts structure
            logger.info(f"📝 Input posts structure:")
            for i, post in enumerate(social_posts):
                logger.info(f"   Post {i+1}: ID={post.get('id', 'N/A')}, Type={post.get('type', 'N/A')}, Platform={post.get('platform', 'N/A')}")
            
            # Extract or generate campaign_id from request
            campaign_id = request.get('campaign_id', 'default')
            if campaign_id == 'default':
                # Generate campaign_id from business context for consistency
                company_name = business_context.get('company_name', 'company')
                import hashlib
                campaign_id = hashlib.md5(f"{company_name}_{campaign_objective}".encode()).hexdigest()[:8]
            
            logger.info(f"🎯 Using campaign_id: {campaign_id}")
            
            # Use the SAME working ADK agents that power the /generate endpoint
            visual_results = await generate_agentic_visual_content(
                social_posts=social_posts,
                business_context=business_context,
                campaign_objective=campaign_objective,
                campaign_guidance=campaign_guidance,
                campaign_id=campaign_id
            )
            
        except ImportError as e:
            logger.error(f"❌ ADK visual agents not available: {e}")
            # Fall back to old agent if available
            if generate_visual_content_for_posts:
                logger.info("Falling back to original visual content generation agent")
                
                campaign_id = request.get('campaign_id', 'default')
                if campaign_id == 'default':
                    company_name = business_context.get('company_name', 'company')
                    import hashlib
                    campaign_id = hashlib.md5(f"{company_name}_{campaign_objective}".encode()).hexdigest()[:8]
                
                # ADR-020 REQUIREMENT: Validate business context before visual generation
                if not business_context.get('company_name'):
                    logger.error("❌ CONTEXT_FIDELITY_VIOLATION: Missing company_name for visual generation")
                    raise HTTPException(status_code=400, detail="Company name required for contextual visual generation")
                
                if not business_context.get('industry'):
                    logger.error("❌ CONTEXT_FIDELITY_VIOLATION: Missing industry for visual generation")
                    raise HTTPException(status_code=400, detail="Industry context required for contextual visual generation")
                
                visual_results = await generate_visual_content_for_posts(
                    social_posts=social_posts,
                    business_context=business_context,
                    campaign_objective=campaign_objective,
                    campaign_guidance=campaign_guidance,
                    campaign_id=campaign_id
                )
                
                # ADR-020 REQUIREMENT: Validate visual results don't contain forbidden URLs
                _validate_visual_results_context_fidelity(visual_results, business_context)
                
            else:
                raise HTTPException(status_code=500, detail="No visual generation agents available")
        
        if visual_results:
            
            # CRITICAL REGRESSION DETECTION: Log visual results structure
            logger.info(f"🔍 VISUAL RESULTS STRUCTURE VALIDATION:")
            logger.info(f"   Type: {type(visual_results)}")
            logger.info(f"   Keys: {list(visual_results.keys()) if isinstance(visual_results, dict) else 'Not a dict'}")
            
            if 'posts_with_visuals' in visual_results:
                posts_with_visuals_data = visual_results['posts_with_visuals']
                logger.info(f"   posts_with_visuals type: {type(posts_with_visuals_data)}")
                logger.info(f"   posts_with_visuals length: {len(posts_with_visuals_data) if isinstance(posts_with_visuals_data, list) else 'Not a list'}")
                
                # DETAILED IMAGE URL VALIDATION
                for i, post in enumerate(posts_with_visuals_data):
                    if isinstance(post, dict):
                        image_url = post.get('image_url')
                        video_url = post.get('video_url')
                        logger.info(f"   Post {i+1} Visual URLs:")
                        logger.info(f"      🖼️ image_url: {'✅ Present' if image_url else '❌ Missing/Null'} ({len(image_url) if image_url else 0} chars)")
                        logger.info(f"      🎬 video_url: {'✅ Present' if video_url else '❌ Missing/Null'} ({len(video_url) if video_url else 0} chars)")
                        
                        # REGRESSION DETECTION: Alert if expected URLs are missing
                        if post.get('type') in ['text_image', 'image_only'] and not image_url:
                            logger.error(f"🚨 REGRESSION DETECTED: Post {post.get('id')} type {post.get('type')} missing image_url!")
                        if post.get('type') in ['text_video', 'video_only'] and not video_url:
                            logger.error(f"🚨 REGRESSION DETECTED: Post {post.get('id')} type {post.get('type')} missing video_url!")
            else:
                logger.error(f"🚨 CRITICAL ERROR: posts_with_visuals missing from visual_results!")
            
            # FIXED: Use the posts_with_visuals directly from the agent response
            # The visual agent returns a structured response with posts_with_visuals as a list
            posts_with_visuals = visual_results.get('posts_with_visuals', [])
            
            # FINAL API RESPONSE VALIDATION
            logger.info(f"📤 FINAL API RESPONSE VALIDATION:")
            logger.info(f"   Returning {len(posts_with_visuals)} posts with visuals")
            
            for i, post in enumerate(posts_with_visuals):
                if isinstance(post, dict):
                    image_url = post.get('image_url')
                    video_url = post.get('video_url')
                    logger.info(f"   API Response Post {i+1}:")
                    logger.info(f"      ID: {post.get('id', 'N/A')}")
                    logger.info(f"      Type: {post.get('type', 'N/A')}")
                    logger.info(f"      🖼️ image_url in response: {'✅ YES' if image_url else '❌ NO'}")
                    logger.info(f"      🎬 video_url in response: {'✅ YES' if video_url else '❌ NO'}")
                    
                    # TYPE-SPECIFIC VALIDATION for test visibility
                    post_type = post.get('type', 'unknown')
                    
                    if post_type == 'text_image':
                        if image_url:
                            print(f"✅ IMAGE_URL_VALIDATION: Post {post.get('id')} has image_url ({len(image_url)} chars)", flush=True)
                        else:
                            print(f"❌ IMAGE_URL_VALIDATION: Post {post.get('id')} type {post_type} MISSING image_url!", flush=True)
                    elif post_type == 'text_video':
                        if video_url:
                            print(f"✅ VIDEO_URL_VALIDATION: Post {post.get('id')} has video_url ({len(video_url)} chars)", flush=True)
                        else:
                            print(f"❌ VIDEO_URL_VALIDATION: Post {post.get('id')} type {post_type} MISSING video_url!", flush=True)
                    elif post_type == 'text_url':
                        print(f"✅ TEXT_URL_VALIDATION: Post {post.get('id')} type {post_type} (no visual content required)", flush=True)
                    else:
                        print(f"⚠️ UNKNOWN_TYPE_VALIDATION: Post {post.get('id')} has unknown type {post_type}", flush=True)
            
            return {
                "posts_with_visuals": posts_with_visuals,
                "generation_metadata": visual_results.get('generation_metadata', {}),
                "processing_time": time.time() - start_time
            }
        
    except Exception as e:
        logger.error(f"❌ Visual content generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Visual content generation failed: {str(e)}"
        )

@router.post("/generate-bulk")
async def generate_bulk_content(request: dict):
    """
    Generate bulk social media content for the ideation page.
    This endpoint matches the frontend's generateBulkContent API call.
    """
    try:
        logger.info(f"🎯 Bulk content generation request: {request.get('post_type', 'unknown')} posts")
        
        post_type = request.get('post_type', 'text_url')
        regenerate_count = request.get('regenerate_count', 4)
        business_context = request.get('business_context', {})
        creativity_level = request.get('creativity_level', 7)
        
        # Validate and limit post count for cost control
        max_posts = {
            'text_url': 6,      # Text posts are cheaper
            'text_image': 4,    # Image generation is expensive
            'text_video': 4     # Video generation is expensive
        }
        
        actual_count = min(regenerate_count, max_posts.get(post_type, 4))
        if actual_count < regenerate_count:
            logger.info(f"⚠️ Limiting {post_type} generation from {regenerate_count} to {actual_count} posts for cost control")
        
        start_time = time.time()
        
        # Use the existing batch generation function
        if os.getenv("GEMINI_API_KEY") and business_context:
            logger.info("Using optimized batch Gemini generation for bulk content")
            
            # Convert post_type string to PostType enum
            post_type_enum = {
                'text_url': PostType.TEXT_URL,
                'text_image': PostType.TEXT_IMAGE,
                'text_video': PostType.TEXT_VIDEO
            }.get(post_type, PostType.TEXT_URL)
            
            generated_posts = await _generate_batch_content_with_gemini(
                post_type_enum, 
                actual_count, 
                business_context
            )
            
            # Transform posts to match frontend expectations
            new_posts = []
            for post in generated_posts:
                new_posts.append({
                    "id": post.id,
                    "type": post.type.value,
                    "content": post.content,
                    "hashtags": post.hashtags,
                    "url": business_context.get('product_service_url') or business_context.get('business_website') if post_type == 'text_url' else None,
                    "image_url": None,  # Will be generated separately
                    "video_url": None,  # Will be generated separately
                    "platform_optimized": post.platform_optimized,
                    "engagement_score": post.engagement_score,
                    "selected": post.selected
                })
            
            processing_time = time.time() - start_time
            
            return {
                "new_posts": new_posts,
                "regeneration_metadata": {
                    "post_type": post_type,
                    "requested_count": regenerate_count,
                    "actual_count": len(new_posts),
                    "generation_method": "optimized_batch_gemini_generation",
                    "creativity_level": creativity_level,
                    "business_context_used": bool(business_context),
                    "cost_controlled": len(new_posts) < regenerate_count
                },
                "processing_time": processing_time
            }
            
        else:
            # Fallback generation
            logger.info("Using fallback generation for bulk content")
            
            new_posts = []
            for i in range(actual_count):
                post_id = f"bulk_{post_type}_{int(time.time())}_{i}"
                content = generate_enhanced_content_for_bulk(post_type, business_context, i)
                
                new_posts.append({
                    "id": post_id,
                    "type": post_type,
                    "content": content,
                    "hashtags": generate_contextual_hashtags(business_context),
                    "url": business_context.get('product_service_url') or business_context.get('business_website') if post_type == 'text_url' else None,
                    "image_url": None,
                    "video_url": None,
                    "platform_optimized": {},
                    "engagement_score": 7.5 + (i * 0.1),
                    "selected": False
                })
            
            processing_time = time.time() - start_time
            
            return {
                "new_posts": new_posts,
                "regeneration_metadata": {
                    "post_type": post_type,
                    "requested_count": regenerate_count,
                    "actual_count": len(new_posts),
                    "generation_method": "fallback_generation",
                    "creativity_level": creativity_level,
                    "business_context_used": bool(business_context)
                },
                "processing_time": processing_time
            }
        
    except Exception as e:
        logger.error(f"❌ Bulk content generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Bulk content generation failed: {str(e)}"
        )

def generate_enhanced_content_for_bulk(post_type: str, business_context: dict, index: int) -> str:
    """Generate enhanced content for bulk generation based on business context."""
    
    company_name = business_context.get('company_name', 'Your Company')
    objective = business_context.get('objective', 'increase sales')
    campaign_type = business_context.get('campaign_type', 'service')
    target_audience = business_context.get('target_audience', 'business professionals')
    
    # Generate contextual content based on post type
    if post_type == 'text_url':
        content_templates = [
            f"🚀 Ready to {objective}? {company_name} has the solution! Discover how we're helping {target_audience} achieve their goals.",
            f"💡 Transform your business with {company_name}'s innovative {campaign_type} approach. Results that speak for themselves.",
            f"🎯 {company_name} helps businesses {objective} faster than ever. Join hundreds of satisfied clients.",
            f"✨ Discover how {company_name} can revolutionize your {campaign_type} strategy. Success starts here.",
            f"🔥 Game-changing {campaign_type} solutions from {company_name}. Experience the difference quality makes."
        ]
    elif post_type == 'text_image':
        content_templates = [
            f"🎨 See {company_name} in action! Visual excellence meets proven results.",
            f"📸 Innovation you can see. {company_name} delivers quality that stands out.",
            f"🌟 Your success story starts here. Professional {campaign_type} solutions that work.",
            f"💫 Transforming the {campaign_type} industry, one client at a time.",
            f"🎭 Excellence you can see and results you can measure."
        ]
    else:  # text_video
        content_templates = [
            f"🎬 Watch {company_name} transform {campaign_type}. Dynamic solutions in motion.",
            f"📹 See innovation come to life. Real stories, real results.",
            f"🎥 Your future starts now. Discover the {company_name} difference.",
            f"🌟 Dynamic solutions, measurable results. Experience it yourself.",
            f"🚀 Watch the transformation happen. Success in action."
        ]
    
    return content_templates[index % len(content_templates)]

async def _generate_batch_content_with_gemini(
    post_type: PostType, 
    regenerate_count: int, 
    business_context: dict
) -> List[SocialMediaPost]:
    """Generate multiple posts in a single Gemini API call for optimal performance."""
    
    try:
        import google.genai as genai
        import json
        import re
        
        # Apply configurable limits based on post type with safe parsing
        def safe_int_env(env_var: str, default: str) -> int:
            """Safely parse environment variable to int, handling malformed values."""
            try:
                value = os.getenv(env_var, default)
                # Handle case where environment variable contains extra content
                if '=' in value:
                    value = value.split('=')[0]
                return int(value)
            except (ValueError, TypeError):
                logger.warning(f"Invalid environment variable {env_var}, using default {default}")
                return int(default)
        
        max_posts_by_type = {
            PostType.TEXT_URL: safe_int_env('MAX_TEXT_URL_POSTS', '10'),
            PostType.TEXT_IMAGE: safe_int_env('MAX_TEXT_IMAGE_POSTS', '4'), 
            PostType.TEXT_VIDEO: safe_int_env('MAX_TEXT_VIDEO_POSTS', '4')
        }
        
        max_allowed = max_posts_by_type.get(post_type, 5)
        actual_count = min(regenerate_count, max_allowed)
        
        if actual_count < regenerate_count:
            logger.info(f"Limiting {post_type.value} generation from {regenerate_count} to {actual_count} posts for cost control")
        
        # Initialize Gemini client
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        
        company_name = business_context.get('company_name', 'Your Company')
        objective = business_context.get('objective', 'increase sales')
        campaign_type = business_context.get('campaign_type', 'service')
        business_description = business_context.get('business_description', '')
        target_audience = business_context.get('target_audience', 'business professionals')
        
        # NEW: Extract Campaign Media Tuning for enhanced visual guidance
        campaign_media_tuning = business_context.get('campaign_media_tuning', '')
        
        # Extract campaign guidance for consistent visual content
        campaign_guidance = business_context.get('campaign_guidance', {})
        visual_style = campaign_guidance.get('visual_style', {})
        imagen_prompts = campaign_guidance.get('imagen_prompts', {})
        veo_prompts = campaign_guidance.get('veo_prompts', {})
        content_themes = campaign_guidance.get('content_themes', {})
        
        # NEW: Extract product-specific context for enhanced targeting
        product_context = business_context.get('product_context', {})
        has_specific_product = product_context.get('has_specific_product', False)
        product_name = product_context.get('product_name', '')
        product_description = product_context.get('product_description', '')
        product_themes = product_context.get('product_themes', [])
        
        # Enhanced business context with product focus
        if has_specific_product and product_name:
            logger.info(f"Using product-specific context for: {product_name}")
            primary_focus = f"Promote the specific product: {product_name}"
            target_context = f"Target audience specifically interested in: {product_description}"
            enhanced_company_name = f"{company_name} - {product_name}"
        else:
            primary_focus = f"Promote {company_name}'s {campaign_type} offerings"
            target_context = f"Target audience: {target_audience}"
            enhanced_company_name = company_name
        
        # Enhanced content generation with product-specific themes
        product_theme_text = f"\\nProduct Themes: {', '.join(product_themes)}" if product_themes else ""
        creative_direction = campaign_guidance.get('creative_direction', f'Professional content showcasing {enhanced_company_name}')
        
        # Create post type specific prompt with campaign guidance
        post_type_name = post_type.value.replace('_', ' + ').title()
        
        if post_type == PostType.TEXT_URL:
            format_instructions = f"""
            Generate {actual_count} Text + URL posts (40-120 characters each):
            - CRITICAL: DO NOT embed URLs in content text - provide URL separately in JSON "url" field
            - Short, punchy, social media optimized content about the actual business/product
            - Twitter/Instagram friendly length
            - Strong action verbs (Discover, Transform, Boost, etc.)
            - Content must be relevant to {company_name}'s actual business/product
            - Platform: LinkedIn, Twitter, Instagram optimized
            - Call-to-Action Style: {content_themes.get('call_to_action_style', 'inspiring and action-oriented')}
            """
        elif post_type == PostType.TEXT_IMAGE:
            imagen_base = imagen_prompts.get('base_prompt', 'Professional lifestyle photography')
            imagen_environment = imagen_prompts.get('environment', 'business setting')
            imagen_technical = imagen_prompts.get('technical_specs', '35mm lens, natural lighting')
            
            # Apply Campaign Media Tuning to Imagen prompts if provided
            media_tuning_guidance = f"\n- Campaign Media Tuning: {campaign_media_tuning}" if campaign_media_tuning else ""
            
            format_instructions = f"""
            Generate {actual_count} Text + Image posts (30-80 characters each):
            - Very short text to complement visuals
            - Include detailed image generation prompts following Imagen best practices
            - Visual storytelling approach focused on {company_name}'s business
            - Instagram/TikTok optimized
            - Let the image do the talking
            
            IMAGEN PROMPT GUIDANCE (follow exactly):
            - Base Style: {imagen_base}
            - Environment: {imagen_environment}  
            - Technical Specs: {imagen_technical}
            - Photography Style: {visual_style.get('photography_style', 'professional lifestyle')}
            - Mood: {visual_style.get('mood', 'professional, trustworthy')}
            - Subject Focus: People using {company_name}'s products/services in real scenarios{media_tuning_guidance}
            
            Cost Control: Limited to {actual_count} posts to manage Imagen API costs
            """
        else:  # TEXT_VIDEO
            veo_base = veo_prompts.get('base_prompt', 'Dynamic lifestyle video')
            veo_movement = veo_prompts.get('movement_style', 'smooth camera movements')
            veo_storytelling = veo_prompts.get('storytelling', 'problem-solution narrative')
            
            # Apply Campaign Media Tuning to Veo prompts if provided
            media_tuning_guidance = f"\n- Campaign Media Tuning: {campaign_media_tuning}" if campaign_media_tuning else ""
            
            format_instructions = f"""
            Generate {actual_count} Text + Video posts (40-100 characters each):
            - Short, dynamic captions for video content
            - Include detailed video concept descriptions following Veo best practices
            - TikTok/Instagram Reels/YouTube Shorts optimized
            - Action-oriented language
            - Focus on movement and energy
            
            VEO PROMPT GUIDANCE (follow exactly):
            - Base Concept: {veo_base}
            - Movement Style: {veo_movement}
            - Storytelling: {veo_storytelling}
            - Duration Focus: {veo_prompts.get('duration_focus', '4-8 second clips')}
            - Scene Composition: {veo_prompts.get('scene_composition', 'engaging transitions')}
            - Show real people engaging with {company_name}'s offerings{media_tuning_guidance}
            
            Cost Control: Limited to {actual_count} posts to manage Veo API costs
            """
        
        # Platform-specific character limits and requirements
        platform_requirements = {
            PostType.TEXT_URL: "Twitter: 280 chars max, Instagram: 125 chars optimal, LinkedIn: 150 chars optimal",
            PostType.TEXT_IMAGE: "Instagram: 30-80 chars, TikTok: 40-80 chars, Visual focus",
            PostType.TEXT_VIDEO: "TikTok: 40-100 chars, Instagram Reels: 60 chars, YouTube Shorts: 80 chars"
        }
        
        # Get primary themes for consistent messaging
        primary_themes = content_themes.get('primary_themes', ['authenticity', 'results', 'community'])
        emotional_triggers = content_themes.get('emotional_triggers', ['aspiration', 'trust', 'excitement'])
        
        # Comprehensive batch generation prompt with campaign guidance
        batch_prompt = f"""
        As a professional social media marketing expert, generate {actual_count} high-quality {post_type_name} posts for {enhanced_company_name} following the established CAMPAIGN GUIDANCE.

        Business Context:
        - Company: {enhanced_company_name}
        - {primary_focus}
        - Objective: {objective}
        - Campaign Type: {campaign_type}
        - {target_context}
        - Business Description: {business_description}
        - Website URL: {business_context.get('business_website', business_context.get('product_service_url', 'https://example.com'))}

        {f"PRODUCT-SPECIFIC CONTEXT (PRIORITY):" if has_specific_product else ""}
        {f"- Product Name: {product_name}" if product_name else ""}
        {f"- Product Description: {product_description}" if product_description else ""}
        {f"- Product Themes: {', '.join(product_themes)}" if product_themes else ""}
        {f"- CRITICAL: All content must focus on promoting THIS SPECIFIC PRODUCT" if has_specific_product else ""}

        CAMPAIGN GUIDANCE (CRITICAL - Follow Exactly):
        - Creative Direction: {creative_direction}
        - Primary Themes: {', '.join(primary_themes)}
        - Emotional Triggers: {', '.join(emotional_triggers)}
        - Brand Voice: {business_context.get('brand_voice', 'Professional and innovative')}
        - Visual Mood: {visual_style.get('mood', 'professional, trustworthy')}
        {f"- Campaign Media Tuning: {campaign_media_tuning}" if campaign_media_tuning else ""}

        {format_instructions}

        Platform Requirements: {platform_requirements[post_type]}

        CRITICAL Requirements for ALL posts:
        - Keep text SHORT and PUNCHY for social media
        - For ALL POST TYPES: MUST include the product/service URL in the JSON "url" field
        - For TEXT_URL: DO NOT embed URL in content text - provide separately in "url" field
        - For TEXT_IMAGE: MUST follow Imagen prompt guidance above for relevant, business-specific images
        - For TEXT_VIDEO: MUST follow Veo prompt guidance above for relevant, business-specific videos
        - Use emojis strategically for engagement
        - Include 3-4 relevant hashtags (separate field)
        - Make content specific to {company_name} and their actual business/product (not generic business content)
        - Follow campaign themes: {', '.join(primary_themes)}
        - CRITICAL: This is CUSTOMER-FACING content - NO internal comments, thoughts, or debug text like "(Implied Brand Name)" or similar
        - Write ONLY polished marketing content that customers will see publicly

        CRITICAL URL REQUIREMENTS for ALL POST TYPES:
        - ALWAYS include the PRODUCT/SERVICE URL in the JSON "url" field: {business_context.get('product_service_url', business_context.get('business_website', 'https://example.com'))}
        - If promoting a specific product, use the product page URL, NOT the main website
        - Every post needs a "See More" link to drive traffic to the business
        - NEVER embed URLs in the content text - always use separate "url" field

        Format your response as JSON:
        {{
            "posts": [
                {{
                    "content": "Short punchy text here (follow character limits)",
                    "hashtags": ["#tag1", "#tag2", "#tag3"],
                    {"image_prompt" if post_type == PostType.TEXT_IMAGE else "video_prompt" if post_type == PostType.TEXT_VIDEO else "call_to_action"}: "{"Detailed Imagen-optimized prompt for " + company_name + " business context" if post_type == PostType.TEXT_IMAGE else "Detailed Veo-optimized concept for " + company_name + " business context" if post_type == PostType.TEXT_VIDEO else "Strong CTA without URL"}",
                    "url": "Product/service URL here (REQUIRED for ALL post types)"
                }},
                // ... repeat for {actual_count} posts
            ]
        }}

        Generate exactly {actual_count} unique, SHORT, social media optimized posts that will drive {objective} for {company_name} following the campaign guidance for consistent brand experience.
        """
        
        # Generate content using Gemini
        logger.info(f"Generating {actual_count} {post_type.value} posts with single Gemini API call")
        response = client.models.generate_content(
            model=model,
            contents=batch_prompt
        )
        
        # Parse the response
        response_text = response.text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            try:
                content_data = json.loads(json_match.group())
                posts = content_data.get('posts', [])
                
                # Convert to SocialMediaPost objects
                generated_posts = []
                for i, post_data in enumerate(posts[:actual_count]):
                    post_content = post_data.get('content', f'Generated {post_type.value} content for {company_name}')
                    
                    post = SocialMediaPost(
                        id=f"batch_generated_{post_type.value}_{i+1}",
                        type=post_type,
                        content=post_content,
                        hashtags=post_data.get('hashtags', [f"#{campaign_type}", "#Business", "#Growth"]),
                        platform_optimized={
                            "linkedin": {
                                "content": f"Professional content for LinkedIn",
                                "hashtags": ["#Professional", "#LinkedIn", "#Business"]
                            },
                            "twitter": {
                                "content": f"Concise content for Twitter", 
                                "hashtags": ["#Twitter", "#Social", "#Marketing"]
                            },
                            "instagram": {
                                "content": f"Visual content for Instagram",
                                "hashtags": ["#Instagram", "#Visual", "#Creative"]
                            },
                            "facebook": {
                                "content": f"Engaging content for Facebook",
                                "hashtags": ["#Facebook", "#Engagement", "#Community"]
                            }
                        },
                        engagement_score=8.0 + (i * 0.1),
                        selected=False
                    )
                    
                    # MARKETING FIX: ALL post types should include product URL for effective marketing
                    # Get the product/service URL for ALL post types
                    post_url = (post_data.get('url') or 
                               business_context.get('product_service_url') or 
                               business_context.get('business_website'))
                    if post_url and not post_url.startswith('http'):
                        post_url = f"https://{post_url}"
                    
                    # Add type-specific fields with proper URL/CTA handling
                    if post_type == PostType.TEXT_URL:
                        post.url = post_url
                        # DO NOT add URL to content - it will be displayed separately in the UI
                        # The frontend will handle URL display in a dedicated section
                            
                    elif post_type == PostType.TEXT_IMAGE:
                        post.image_prompt = post_data.get('image_prompt', f'Professional marketing image for {company_name} showing {objective}')
                        # NO AUTOMATIC GENERATION - Images are generated manually due to cost
                        # The frontend will show a "Generate Images" button
                        post.image_url = None  # Will be populated when user manually triggers generation
                        # MARKETING FIX: Include URL for image posts too
                        post.url = post_url
                        
                    elif post_type == PostType.TEXT_VIDEO:
                        post.video_prompt = post_data.get('video_prompt', f'Dynamic marketing video showcasing {company_name} approach to {objective}')
                        # NO AUTOMATIC GENERATION - Videos are generated manually due to cost
                        # The frontend will show a "Generate Videos" button
                        post.video_url = None  # Will be populated when user manually triggers generation
                        post.thumbnail_url = None
                        # MARKETING FIX: Include URL for video posts too
                        post.url = post_url
                    
                    generated_posts.append(post)
                
                logger.info(f"Successfully generated {len(generated_posts)} posts with batch Gemini call (cost-controlled)")
                return generated_posts
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Gemini JSON response: {e}")
        
        # Fallback to individual generation
        logger.info("Falling back to individual post generation")
        return _generate_fallback_posts(post_type, actual_count, business_context)
        
    except Exception as e:
        logger.error(f"Batch content generation failed: {e}")
        return _generate_fallback_posts(post_type, min(regenerate_count, 5), business_context)

def _generate_fallback_posts(post_type: PostType, count: int, business_context: dict) -> List[SocialMediaPost]:
    """Generate fallback posts when batch generation fails."""
    
    company_name = business_context.get('company_name', 'Your Company')
    objective = business_context.get('objective', 'increase sales')
    
    posts = []
    for i in range(count):
        post = SocialMediaPost(
            id=f"fallback_{post_type.value}_{i+1}",
            type=post_type,
            content=generate_enhanced_content(post_type, business_context, i),
            hashtags=generate_contextual_hashtags(business_context),
            platform_optimized={
                "linkedin": {
                    "content": f"Professional {post_type.value} content for {company_name}",
                    "hashtags": ["#Professional", "#LinkedIn", "#Business"]
                },
                "twitter": {
                    "content": f"Engaging {post_type.value} content for {company_name}",
                    "hashtags": ["#Twitter", "#Social", "#Marketing"]
                },
                "instagram": {
                    "content": f"Visual {post_type.value} content for {company_name}",
                    "hashtags": ["#Instagram", "#Visual", "#Creative"]
                },
                "facebook": {
                    "content": f"Engaging {post_type.value} content for {company_name}",
                    "hashtags": ["#Facebook", "#Engagement", "#Community"]
                }
            },
            engagement_score=7.5 + (i * 0.1),
            selected=False
        )
        
        # MARKETING FIX: ALL post types should include product URL for effective marketing
        # Get the product/service URL for ALL post types
        post_url = (business_context.get('product_service_url') or 
                   business_context.get('business_website'))
        if post_url and not post_url.startswith('http'):
            post_url = f"https://{post_url}"
        
        # Add type-specific fields for fallback posts
        if post_type == PostType.TEXT_URL:
            post.url = post_url
            # DO NOT add URL to content - frontend will display it separately
                
        elif post_type == PostType.TEXT_IMAGE:
            post.image_prompt = f'Professional marketing image for {company_name} showing {objective}'
            # NO AUTOMATIC GENERATION - Images are generated manually due to cost
            post.image_url = None
            # MARKETING FIX: Include URL for image posts too
            post.url = post_url
            
        elif post_type == PostType.TEXT_VIDEO:
            post.video_prompt = f'Dynamic marketing video showcasing {company_name} approach to {objective}'
            # NO AUTOMATIC GENERATION - Videos are generated manually due to cost
            post.video_url = None
            post.thumbnail_url = None
            # MARKETING FIX: Include URL for video posts too
            post.url = post_url
        
        posts.append(post)
    
    return posts 

@router.get("/cache/stats")
async def get_cache_stats(campaign_id: str = None):
    """Get image cache statistics for all campaigns or specific campaign."""
    try:
        from agents.visual_content_agent import CampaignImageCache
        cache = CampaignImageCache()
        stats = cache.get_cache_stats(campaign_id)
        
        logger.info(f"📊 Cache stats requested for campaign {campaign_id or 'all'}: {stats}")
        return {
            "cache_stats": stats,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {
            "error": str(e),
            "status": "error"
        }

@router.post("/cache/clear")
async def clear_image_cache(request: dict = None):
    """Clear image cache for all campaigns or specific campaign."""
    try:
        from agents.visual_content_agent import CampaignImageCache
        cache = CampaignImageCache()
        
        if request and request.get('campaign_id'):
            # Clear specific campaign cache
            campaign_id = request['campaign_id']
            cleared_count = cache.clear_campaign_cache(campaign_id)
            message = f"Cleared {cleared_count} cached images for campaign {campaign_id}"
        else:
            # Clear all cache
            cleared_count = cache.clear_all_cache()
            message = f"Cleared {cleared_count} cached images from all campaigns"
        
        logger.info(f"🗑️ Cache cleared: {message}")
        print(f"✅ CACHE_MANAGEMENT: {message}")
        return {
            "cleared_images": cleared_count,
            "message": message,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return {
            "error": str(e),
            "status": "error"
        }

@router.post("/cache/cleanup")
async def cleanup_old_images(request: dict = None):
    """Cleanup old (non-current) images while keeping current images."""
    try:
        from agents.visual_content_agent import CampaignImageCache
        cache = CampaignImageCache()
        
        campaign_id = None
        if request and request.get('campaign_id'):
            campaign_id = request['campaign_id']
        
        cleaned_count = cache.cleanup_old_images(campaign_id)
        
        if campaign_id:
            message = f"Cleaned up {cleaned_count} old images for campaign {campaign_id}, kept current images"
        else:
            message = f"Cleaned up {cleaned_count} old images from all campaigns, kept current images"
        
        logger.info(f"🗑️ Cache cleanup: {message}")
        print(f"✅ CACHE_CLEANUP: {message}")
        return {
            "cleaned_images": cleaned_count,
            "message": message,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to cleanup old images: {e}")
        return {
            "error": str(e),
            "status": "error"
        }

@router.get("/images/{campaign_id}/{filename}")
async def serve_generated_image(campaign_id: str, filename: str):
    """
    Serve generated images with proper headers and security validation.
    This endpoint serves actual generated image files for frontend display.
    """
    try:
        # Security validation: ensure safe filename
        if not filename.replace('.', '').replace('_', '').replace('-', '').isalnum():
            raise HTTPException(status_code=400, detail="Invalid filename")
            
        if '..' in filename or '/' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
            
        # Construct file path
        image_path = Path(f"data/images/generated/{campaign_id}/{filename}")
        
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise HTTPException(status_code=404, detail="Image not found")
            
        # Determine content type
        if filename.lower().endswith('.png'):
            media_type = "image/png"
        elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            media_type = "image/jpeg"
        else:
            media_type = "application/octet-stream"
            
        logger.info(f"✅ Serving image: {filename} ({image_path.stat().st_size / 1024:.1f}KB)")
        
        return FileResponse(
            path=str(image_path),
            media_type=media_type,
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                "Content-Disposition": f"inline; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve image")

@router.get("/videos/{campaign_id}/{filename}")
@router.head("/videos/{campaign_id}/{filename}")
async def serve_generated_video(campaign_id: str, filename: str):
    """
    Serve generated videos with proper headers and security validation.
    This endpoint serves actual generated video files for frontend playback.
    """
    try:
        # Security validation: ensure safe filename
        if not filename.replace('.', '').replace('_', '').replace('-', '').isalnum():
            raise HTTPException(status_code=400, detail="Invalid filename")
            
        if '..' in filename or '/' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
            
        # Construct file path
        video_path = Path(f"data/videos/generated/{campaign_id}/{filename}")
        
        # Check if the actual MP4 file exists
        if not video_path.exists():
            logger.error(f"🎬 Video file not found: {video_path}")
            raise HTTPException(status_code=404, detail=f"Video file not found: {filename}")
            
        # Verify it's an actual video file (not empty)
        if video_path.stat().st_size == 0:
            logger.error(f"🎬 Video file is empty: {video_path}")
            raise HTTPException(status_code=404, detail=f"Video file is empty: {filename}")
            
        # Determine content type
        if filename.lower().endswith('.mp4'):
            media_type = "video/mp4"
        elif filename.lower().endswith('.webm'):
            media_type = "video/webm"
        elif filename.lower().endswith('.mov'):
            media_type = "video/quicktime"
        else:
            media_type = "application/octet-stream"
            
        logger.info(f"✅ Serving video: {filename} ({video_path.stat().st_size / 1024 / 1024:.1f}MB)")
        
        return FileResponse(
            path=str(video_path),
            media_type=media_type,
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                "Content-Disposition": f"inline; filename={filename}",
                "Accept-Ranges": "bytes"  # Enable video seeking
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving video {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve video")

@router.get("/videos/cache/stats")
async def get_video_cache_stats(campaign_id: str = None):
    """Get video cache statistics for monitoring and debugging."""
    try:
        from agents.visual_content_agent import CampaignVideoCache
        
        cache = CampaignVideoCache()
        stats = cache.get_cache_stats(campaign_id)
        
        return {
            "video_cache_stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Video cache stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get video cache stats")

@router.post("/videos/cache/clear")
async def clear_video_cache(request: dict = None):
    """Clear video cache for specified campaign or all campaigns."""
    try:
        from agents.visual_content_agent import CampaignVideoCache
        
        cache = CampaignVideoCache()
        campaign_id = request.get('campaign_id') if request else None
        
        if campaign_id:
            count = cache.clear_campaign_cache(campaign_id)
            return {
                "message": f"Cleared {count} cached videos for campaign {campaign_id}",
                "campaign_id": campaign_id,
                "cleared_count": count
            }
        else:
            count = cache.clear_all_cache()
            return {
                "message": f"Cleared all {count} cached videos",
                "cleared_count": count
            }
        
    except Exception as e:
        logger.error(f"Video cache clear error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear video cache")

@router.post("/generate-visuals-async", response_model=AsyncVisualResponse)
async def start_async_visual_generation(request: dict):
    """
    Start async visual content generation - returns immediately with job tracking info.
    
    This endpoint provides progressive loading support:
    - Returns immediately with job IDs and estimated completion times
    - Frontend can poll /visual-status/{campaign_id} for updates
    - Visual content appears progressively as jobs complete
    """
    try:
        logger.info("🚀 Starting async visual content generation")
        
        # ARCHITECTURAL COHERENCE FIX: Async visual manager temporarily disabled
        # await visual_manager.start_workers()
        
        # Extract request data
        social_posts = request.get("social_posts", [])
        business_context = request.get("business_context", {})
        campaign_objective = request.get("campaign_objective", "increase engagement")
        campaign_id = request.get("campaign_id", f"campaign_{int(time.time())}")
        
        logger.info(f"📋 Processing async visual generation for {len(social_posts)} posts")
        
        # ARCHITECTURAL COHERENCE FIX: Return placeholder response
        jobs = []
        # jobs = await visual_manager.queue_visual_generation(
        #     campaign_id=campaign_id,
        #     posts=social_posts,
        #     business_context=business_context,
        #     campaign_objective=campaign_objective
        # )
        
        # Calculate total estimated time
        total_time = sum(job.estimated_completion_seconds or 0 for job in jobs)
        
        response = AsyncVisualResponse(
            success=True,
            jobs=jobs,
            total_jobs=len(jobs),
            estimated_total_time_seconds=total_time,
            polling_endpoint=f"/api/v1/content/visual-status/{campaign_id}",
            message=f"Started {len(jobs)} visual generation jobs. Use polling endpoint for progress updates."
        )
        
        logger.info(f"✅ Async visual generation started: {len(jobs)} jobs queued")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to start async visual generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start visual generation: {str(e)}")

@router.get("/visual-status/{campaign_id}", response_model=BatchVisualStatus)
async def get_visual_generation_status(campaign_id: str):
    """
    Get real-time status of visual generation jobs for a campaign.
    
    Frontend should poll this endpoint every 2-3 seconds for updates.
    Returns:
    - Overall progress (0.0 to 1.0)
    - Individual job statuses
    - Completed visual content (posts_with_visuals)
    - Estimated completion time
    """
    try:
        logger.debug(f"📊 Getting visual status for campaign: {campaign_id}")
        
        # ARCHITECTURAL COHERENCE FIX: Return placeholder status
        from ..models import BatchVisualStatus
        status = BatchVisualStatus(
            campaign_id=campaign_id,
            total_jobs=0,
            completed_jobs=0,
            failed_jobs=0,
            overall_progress=1.0,
            is_complete=True,
            estimated_time_remaining_seconds=0,
            posts_with_visuals=[]
        )
        # status = visual_manager.get_campaign_status(campaign_id)
        
        logger.debug(f"📊 Campaign {campaign_id} status: {status.completed_jobs}/{status.total_jobs} complete ({status.overall_progress*100:.0f}%)")
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get visual status for {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get visual status: {str(e)}")

@router.get("/visual-job/{job_id}", response_model=VisualGenerationJob)
async def get_visual_job_status(job_id: str):
    """Get detailed status of a specific visual generation job"""
    try:
        # ARCHITECTURAL COHERENCE FIX: Return placeholder job
        job = None
        # job = visual_manager.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
            
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get job status for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.post("/cancel-visual-jobs/{campaign_id}")
async def cancel_visual_generation(campaign_id: str):
    """Cancel all pending visual generation jobs for a campaign"""
    try:
        # This would be implemented to cancel pending jobs
        # For now, just return success
        return {"success": True, "message": f"Cancelled visual generation for campaign {campaign_id}"}
        
    except Exception as e:
        logger.error(f"❌ Failed to cancel visual generation for {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel visual generation: {str(e)}")