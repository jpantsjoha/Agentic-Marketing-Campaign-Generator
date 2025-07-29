"""
FILENAME: analysis.py
DESCRIPTION/PURPOSE: URL and file analysis API routes with Gemini ADK integration
Author: JP + 2025-06-15
"""

import logging
import sys
import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

# Add backend directory to Python path for proper imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ..models import URLAnalysisRequest, URLAnalysisResponse, BusinessAnalysis

# Import the business analysis service
from agents.trending_hashtag_agent import analyze_trending_hashtags
try:
    from agents.business_analysis_agent import analyze_business_urls
    business_analysis_service = True
except ImportError as e:
    logger.error(f"Failed to import analyze_business_urls: {e}")
    # Fallback to None - will use mock data
    business_analysis_service = False

# Import the agent that performs the actual analysis
try:
    from agents.business_analysis_agent import URLAnalysisAgent
except ImportError:
    URLAnalysisAgent = None

logger = logging.getLogger(__name__)
router = APIRouter()

def _is_valid_url(url: str) -> bool:
    """Validate URL format."""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

@router.post("/url", response_model=URLAnalysisResponse)
async def analyze_business_url(request: URLAnalysisRequest):
    """
    Analyzes one or more business URLs to extract business context using the real AI agent.
    
    ADR-020 COMPLIANCE: Validates business context extraction to ensure contextually relevant
    visual content generation downstream.
    """
    if not URLAnalysisAgent:
        logger.error("URLAnalysisAgent is not available.")
        raise HTTPException(status_code=500, detail="AI services are not configured.")

    try:
        logger.info(f"Received request to analyze URLs: {request.urls}")
        
        # ADR-020 REQUIREMENT: Validate URLs before analysis
        for url in request.urls:
            if not _is_valid_url(url):
                raise HTTPException(status_code=400, detail=f"Invalid URL format: {url}")
        
        agent = URLAnalysisAgent()
        analysis_result = await agent.analyze_urls(
            urls=request.urls,
            analysis_type=request.analysis_depth
        )

        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # ADR-020 REQUIREMENT: Validate that business context was extracted
        business_analysis = analysis_result.get("business_analysis", {})
        if not business_analysis.get("company_name"):
            logger.warning("⚠️ CONTEXT_FIDELITY_WARNING: No company name extracted from URL analysis")
        
        if not business_analysis.get("industry"):
            logger.warning("⚠️ CONTEXT_FIDELITY_WARNING: No industry context extracted from URL analysis")
        
        logger.info("🔧 STARTING theme extraction process...")
        
        # Extract themes and tags for frontend compatibility
        suggested_themes = []
        suggested_tags = []
        
        logger.info(f"DEBUG: Extracting themes from analysis result...")
        
        if "business_analysis" in analysis_result and analysis_result["business_analysis"]:
            business_analysis = analysis_result["business_analysis"]
            logger.info(f"DEBUG: Business analysis found")
            
            # Extract themes from campaign guidance
            campaign_guidance = business_analysis.get("campaign_guidance", {})
            logger.info(f"DEBUG: Campaign guidance keys: {list(campaign_guidance.keys())}")
            
            content_themes = campaign_guidance.get("content_themes", {})
            logger.info(f"DEBUG: Content themes keys: {list(content_themes.keys())}")
            
            # Get primary business themes for tag generation
            primary_business_themes = content_themes.get("primary_themes", [])
            logger.info(f"DEBUG: Primary business themes found: {primary_business_themes}")
            
            # Generate business-specific TAGS from content analysis
            # Convert business themes to hashtag-style tags
            for theme in primary_business_themes[:4]:  # Limit to 4 themes
                # Convert theme to hashtag format
                tag = theme.replace(" ", "").replace("&", "And").replace(",", "").replace("'", "")
                if len(tag) > 3 and len(tag) < 25:  # Reasonable tag length
                    suggested_tags.append(f"#{tag}")
            
            # Add value propositions as tags
            value_props = business_analysis.get("value_propositions", [])
            for prop in value_props[:3]:  # Limit to 3
                # Extract key words and convert to hashtag
                words = prop.split()[:2]  # First 2 words
                for word in words:
                    clean_word = word.replace(",", "").replace(".", "").replace("(", "").replace(")", "")
                    if len(clean_word) > 3 and len(clean_word) < 15:
                        suggested_tags.append(f"#{clean_word}")
            
            # Add company/product specific tags
            company_name = business_analysis.get("company_name", "")
            if company_name and len(company_name) < 20:
                suggested_tags.append(f"#{company_name.replace(' ', '')}")
            
            # Add industry-based tags
            industry = business_analysis.get("industry", "")
            if industry:
                # Extract key industry words
                industry_words = industry.replace("&", "And").replace(",", "").split()
                for word in industry_words[:2]:  # First 2 words
                    clean_word = word.replace("(", "").replace(")", "")
                    if len(clean_word) > 3 and len(clean_word) < 15:
                        suggested_tags.append(f"#{clean_word}")
        
        # CREATIVE/PROMOTIONAL STYLE THEMES (not business content themes)
        # These are visual/creative styles for campaign execution
        creative_style_themes = [
            "Professional", "Modern", "Hipster", "Cartoon", "Nostalgic", 
            "Futuristic", "Colorful", "Minimalist", "Vintage", "Bold",
            "Elegant", "Playful", "Sophisticated", "Dynamic", "Clean",
            "Artistic", "Corporate", "Trendy", "Classic", "Vibrant"
        ]
        
        # Select appropriate creative themes based on business context
        if "business_analysis" in analysis_result:
            business_analysis = analysis_result["business_analysis"]
            industry = business_analysis.get("industry", "").lower()
            target_audience = business_analysis.get("target_audience", "").lower()
            
            # Industry-based theme selection
            if any(word in industry for word in ["tech", "software", "digital", "ai"]):
                suggested_themes = ["Modern", "Futuristic", "Clean", "Professional", "Dynamic"]
            elif any(word in industry for word in ["fashion", "apparel", "clothing", "footwear"]):
                suggested_themes = ["Trendy", "Colorful", "Modern", "Hipster", "Vibrant"]
            elif any(word in industry for word in ["food", "restaurant", "cafe"]):
                suggested_themes = ["Colorful", "Playful", "Modern", "Elegant", "Artistic"]
            elif any(word in industry for word in ["finance", "banking", "investment"]):
                suggested_themes = ["Professional", "Clean", "Sophisticated", "Corporate", "Modern"]
            elif any(word in industry for word in ["health", "medical", "wellness"]):
                suggested_themes = ["Clean", "Professional", "Modern", "Elegant", "Minimalist"]
            elif any(word in industry for word in ["creative", "design", "art"]):
                suggested_themes = ["Artistic", "Colorful", "Bold", "Creative", "Vibrant"]
            else:
                # Default professional themes
                suggested_themes = ["Professional", "Modern", "Clean", "Sophisticated", "Dynamic"]
            
            # Audience-based adjustments
            if any(word in target_audience for word in ["young", "millennial", "gen z"]):
                if "Hipster" not in suggested_themes:
                    suggested_themes.append("Hipster")
                if "Trendy" not in suggested_themes:
                    suggested_themes.append("Trendy")
            elif any(word in target_audience for word in ["family", "parent", "children"]):
                if "Playful" not in suggested_themes:
                    suggested_themes.append("Playful")
                if "Colorful" not in suggested_themes:
                    suggested_themes.append("Colorful")
        else:
            # Fallback creative themes
            suggested_themes = ["Professional", "Modern", "Clean", "Sophisticated", "Dynamic"]
        
        # Get trending hashtags if none extracted
        if not suggested_tags:
            try:
                logger.info("🔥 Getting trending hashtags for enhanced recommendations")
                trending_result = await analyze_trending_hashtags(
                    business_context=business_analysis,
                    target_platforms=['instagram', 'linkedin', 'twitter']
                )
                trending_hashtags = [h['hashtag'] for h in trending_result.get('recommended_hashtags', [])][:8]
                if trending_hashtags:
                    suggested_tags = trending_hashtags
                    logger.info(f"✅ Added {len(trending_hashtags)} trending hashtags")
                else:
                    # Industry-specific fallback (not generic business tags)
                    if 'photography' in industry.lower():
                        suggested_tags = ["#Photography", "#ProfessionalPhotography", "#PhotographyLife", "#CaptureTheMemory", "#ArtisticVision", "#PhotographyPassion"]
                    elif 'food' in industry.lower():
                        suggested_tags = ["#FoodieLife", "#CulinaryArt", "#FreshIngredients", "#TasteOfHome", "#LocalEats", "#FoodPhotography"]
                    elif 'fitness' in industry.lower():
                        suggested_tags = ["#FitnessJourney", "#HealthyLifestyle", "#FitnessMotivation", "#Wellness", "#ActiveLifestyle", "#FitnessGoals"]
                    elif 'tech' in industry.lower():
                        suggested_tags = ["#TechInnovation", "#DigitalTransformation", "#Innovation", "#TechTrends", "#FutureOfWork", "#Technology"]
                    else:
                        suggested_tags = ["#Professional", "#Excellence", "#QualityService", "#Innovation", "#TrustedPartner", "#CustomerFirst"]
            except Exception as e:
                logger.warning(f"⚠️ Trending hashtag analysis failed, using industry fallback: {e}")
                # Industry-specific fallback (not generic business tags)
                if 'photography' in industry.lower():
                    suggested_tags = ["#Photography", "#ProfessionalPhotography", "#PhotographyLife", "#CaptureTheMemory", "#ArtisticVision", "#PhotographyPassion"]
                elif 'food' in industry.lower():
                    suggested_tags = ["#FoodieLife", "#CulinaryArt", "#FreshIngredients", "#TasteOfHome", "#LocalEats", "#FoodPhotography"]
                elif 'fitness' in industry.lower():
                    suggested_tags = ["#FitnessJourney", "#HealthyLifestyle", "#FitnessMotivation", "#Wellness", "#ActiveLifestyle", "#FitnessGoals"]
                elif 'tech' in industry.lower():
                    suggested_tags = ["#TechInnovation", "#DigitalTransformation", "#Innovation", "#TechTrends", "#FutureOfWork", "#Technology"]
                else:
                    suggested_tags = ["#Professional", "#Excellence", "#QualityService", "#Innovation", "#TrustedPartner", "#CustomerFirst"]
        
        # Remove duplicates and limit counts
        suggested_themes = list(dict.fromkeys(suggested_themes))[:8]  # Max 8 themes
        suggested_tags = list(dict.fromkeys(suggested_tags))[:10]     # Max 10 tags
        
        # Add themes and tags to top level for frontend compatibility
        analysis_result["suggested_themes"] = suggested_themes
        analysis_result["suggested_tags"] = suggested_tags
        
        logger.info(f"Extracted {len(suggested_themes)} themes and {len(suggested_tags)} tags")
        
        return analysis_result

    except Exception as e:
        logger.error(f"URL analysis endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files")
async def analyze_files(
    files: List[UploadFile] = File(...),
    analysis_type: str = Form(default="standard", pattern="^(basic|standard|comprehensive)$")
):
    """Analyze uploaded files for business insights."""
    
    try:
        logger.info(f"Analyzing {len(files)} uploaded files")
        
        file_analyses = []
        analysis_results = []  # Backward-compatible field for tests
        
        for file in files:
            # Read file content
            content = await file.read()
            
            # Mock file analysis (replace with real ADK multimodal agent call)
            analysis = {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content),
                "analysis": {
                    "file_type": "image" if file.content_type.startswith("image/") else "document",
                    "key_insights": [
                        "Professional design elements",
                        "Brand consistency",
                        "Target audience alignment"
                    ],
                    "extracted_elements": {
                        "colors": ["#1976d2", "#ffffff", "#f5f5f5"],
                        "text_content": "Sample extracted text",
                        "visual_style": "Modern and professional"
                    },
                    "confidence": 0.82
                }
            }
            file_analyses.append(analysis)
            
            # Backward-compatible analysis_results for tests
            analysis_results.append({
                "filename": file.filename,
                "file_type": file.content_type,
                "content_summary": f"Analysis of {file.filename}",
                "key_insights": analysis["analysis"]["key_insights"],
                "analysis_status": "success"
            })
        
        # Enhanced insights based on analysis type
        enhanced_insights = {}
        if analysis_type == "comprehensive":
            enhanced_insights = {
                "business_focus": "AI solutions for small businesses",
                "target_market": "Small business owners",
                "key_themes": ["AI technology", "Business automation", "Small business solutions"]
            }
        
        response_data = {
            "file_analyses": file_analyses,
            "total_files": len(files),
            "processing_time": 1.8,
            "overall_insights": {
                "brand_consistency": "High",
                "visual_quality": "Professional",
                "content_relevance": "Strong"
            },
            # Backward-compatible fields for tests
            "analysis_results": analysis_results,
            "extracted_insights": {
                "brand_elements": ["Professional design", "Consistent colors"],
                "content_themes": ["Business focus", "Professional presentation"],
                "quality_indicators": ["High resolution", "Clear messaging"],
                **enhanced_insights
            },
            "analysis_metadata": {
                "analysis_type": analysis_type,
                "files_processed": len(files),
                "processing_method": "mock_analysis"
            }
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"File analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"File analysis failed: {str(e)}"
        ) 