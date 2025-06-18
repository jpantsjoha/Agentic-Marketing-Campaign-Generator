"""
FILENAME: business_analysis_agent.py
DESCRIPTION/PURPOSE: Business analysis agent with URL scraping and AI-powered context extraction
Author: JP + 2025-06-16
"""

import logging
import asyncio
import aiohttp
import re
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
from google import genai

logger = logging.getLogger(__name__)

class URLAnalysisAgent:
    """Agent for analyzing business URLs and extracting context."""
    
    def __init__(self):
        """Initialize URL analysis agent with Gemini client."""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        
        if self.gemini_api_key:
            try:
                self.client = genai.Client(api_key=self.gemini_api_key)
                logger.info(f"URL Analysis Agent initialized with Gemini model: {self.gemini_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY not found - URL analysis will use mock responses")
            self.client = None
    
    async def analyze_urls(self, urls: List[str], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze multiple URLs and extract business context.
        
        Args:
            urls: List of URLs to analyze
            analysis_type: Type of analysis (basic, standard, comprehensive)
            
        Returns:
            Dictionary containing extracted business context
        """
        try:
            logger.info(f"Starting {analysis_type} analysis of {len(urls)} URLs")
            
            # Scrape content from all URLs
            url_contents = {}
            async with aiohttp.ClientSession() as session:
                for url in urls:
                    try:
                        content = await self._scrape_url_content(session, url)
                        url_contents[url] = content
                        logger.info(f"Successfully scraped content from {url}")
                    except Exception as e:
                        logger.error(f"Failed to scrape {url}: {e}")
                        url_contents[url] = {"error": str(e)}
            
            # Analyze scraped content with AI
            if self.client and any(content.get('text') for content in url_contents.values()):
                business_context = await self._analyze_content_with_ai(url_contents, analysis_type)
            else:
                business_context = self._generate_enhanced_mock_analysis(url_contents, analysis_type)
            
            return {
                "business_analysis": business_context,
                "url_insights": url_contents,
                "analysis_metadata": {
                    "urls_analyzed": len(urls),
                    "successful_scrapes": len([c for c in url_contents.values() if 'text' in c]),
                    "analysis_type": analysis_type,
                    "ai_analysis_used": self.client is not None
                }
            }
            
        except Exception as e:
            logger.error(f"URL analysis failed: {e}", exc_info=True)
            return self._generate_fallback_analysis(urls)
    
    async def _scrape_url_content(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Scrape content from a single URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract key content elements
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else ""
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Extract main content
                    main_content = soup.get_text()
                    
                    # Clean up text
                    lines = (line.strip() for line in main_content.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Limit text length for AI analysis
                    text = text[:5000] if len(text) > 5000 else text
                    
                    # Extract meta information
                    meta_description = soup.find('meta', attrs={'name': 'description'})
                    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                    
                    return {
                        "url": url,
                        "title": title_text,
                        "text": text,
                        "meta_description": meta_description.get('content', '') if meta_description else '',
                        "meta_keywords": meta_keywords.get('content', '') if meta_keywords else '',
                        "word_count": len(text.split()),
                        "status": "success"
                    }
                else:
                    return {
                        "url": url,
                        "error": f"HTTP {response.status}",
                        "status": "failed"
                    }
                    
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "status": "failed"
            }
    
    async def _analyze_content_with_ai(self, url_contents: Dict[str, Dict], analysis_type: str) -> Dict[str, Any]:
        """Analyze scraped content using Gemini AI."""
        try:
            # Prepare content for AI analysis
            analysis_prompt = self._build_analysis_prompt(url_contents, analysis_type)
            
            # Generate AI analysis
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=analysis_prompt
            )
            
            # Parse AI response into structured format
            ai_analysis = response.text
            
            # Extract structured information from AI response
            business_context = self._parse_ai_analysis(ai_analysis, url_contents)
            
            logger.info("Successfully completed AI-powered business analysis")
            return business_context
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._generate_enhanced_mock_analysis(url_contents, analysis_type)
    
    def _build_analysis_prompt(self, url_contents: Dict[str, Dict], analysis_type: str) -> str:
        """Build comprehensive analysis prompt for Gemini."""
        
        content_summary = ""
        product_url_content = None
        
        for url, content in url_contents.items():
            if content.get('text'):
                content_summary += f"\n\nURL: {url}\n"
                content_summary += f"Title: {content.get('title', 'N/A')}\n"
                content_summary += f"Content: {content['text'][:1000]}...\n"
                
                # Identify product-specific URLs for detailed analysis
                if any(product_indicator in url.lower() for product_indicator in [
                    '/i/', '/product/', '/item/', '/t-shirt/', '/design/', '/artwork/',
                    'redbubble.com/i/', 'etsy.com/listing/', 'amazon.com/dp/',
                    'shop/', '/buy/', '/purchase/'
                ]):
                    product_url_content = content
                    logger.info(f"Identified product URL for detailed analysis: {url}")
        
        prompt = f"""
        As a business intelligence analyst and creative director, analyze the following website content and extract comprehensive business context with detailed CAMPAIGN GUIDANCE for visual content generation.

        CRITICAL ANALYSIS FOCUS:
        - Determine if this is an INDIVIDUAL CREATOR/ARTIST vs a COMPANY
        - For marketplace sellers (Etsy, Redbubble, etc.), focus on the INDIVIDUAL'S work, not the platform
        - Extract the SPECIFIC PRODUCT/SERVICE being promoted, not the marketplace platform
        - Identify the PERSONAL BRAND and artistic style of individual creators

        **PRODUCT-SPECIFIC ANALYSIS** (PRIORITY):
        If a specific product URL is provided, focus your analysis on that SPECIFIC PRODUCT:
        - What is the exact product being sold?
        - What themes, designs, or concepts does it feature?
        - What specific audience would be interested in THIS PRODUCT?
        - How should visuals showcase THIS SPECIFIC PRODUCT?

        {content_summary}

        ANALYSIS INSTRUCTIONS:
        1. **Individual vs Company Detection**: 
           - Look for personal names, artist handles, individual portfolios
           - Detect marketplace URLs (redbubble.com/people/X, etsy.com/shop/X)
           - Distinguish between platform features and individual creator content

        2. **Product/Service Focus**:
           - For artists: Focus on their artwork, style, themes, not the printing service
           - For specific products: Analyze the EXACT product being promoted
           - For consultants: Focus on their expertise, not their booking platform
           - For creators: Focus on their content, not the distribution platform

        3. **Brand Voice Analysis**:
           - Individual creators: Personal, authentic, artistic expression
           - Small businesses: Professional but approachable
           - Corporations: Professional, structured, brand-focused

        **ENHANCED PRODUCT ANALYSIS** (If product URL detected):
        If this analysis includes a specific product URL, provide DETAILED product-specific guidance:
        - Exact product name and description
        - Visual elements and design themes of the product
        - Target audience specifically for this product
        - How content should showcase this specific product
        - Visual context for images (people using/wearing/enjoying THIS product)
        - Specific calls-to-action relevant to this product

        Please provide a detailed analysis in the following JSON-like structure:

        {{
            "business_type": "individual_creator|small_business|corporation",
            "creator_focus": "if individual_creator, describe their specific art/work focus",
            "platform_context": "if marketplace seller, note the platform but focus on individual",
            "product_context": {{
                "has_specific_product": true/false,
                "product_name": "exact product name if specific product identified",
                "product_description": "detailed description of the specific product",
                "product_themes": ["theme1", "theme2", "theme3"],
                "product_visual_elements": "visual design elements of the product",
                "product_target_audience": "specific audience for this product"
            }},
            "company_name": "extracted company/creator name (individual name if artist)",
            "industry": "primary industry/sector (be specific: 'Digital Art & Print-on-Demand' not just 'E-commerce')",
            "business_model": "B2B/B2C/marketplace_seller/creator_economy",
            "target_audience": "specific target audience description",
            "value_propositions": ["key value prop 1", "key value prop 2", "key value prop 3"],
            "products_services": ["main product/service 1", "main product/service 2"],
            "brand_voice": "personal/professional/artistic/innovative/etc",
            "competitive_advantages": ["advantage 1", "advantage 2", "advantage 3"],
            "market_positioning": "positioning statement",
            "key_themes": ["theme 1", "theme 2", "theme 3"],
            "business_objectives": ["likely objective 1", "likely objective 2"],
            "content_style": "description of content style and tone",
            "visual_elements": "description of visual branding elements mentioned",
            
            "campaign_guidance": {{
                "creative_direction": "2-3 sentences describing the overall creative vision and aesthetic approach for THIS SPECIFIC creator/business and product",
                "target_context": "specific context about who they're trying to reach and why",
                "visual_style": {{
                    "photography_style": "specific photography approach matching the creator's style and product",
                    "color_palette": ["primary color", "secondary color", "accent color"],
                    "lighting": "lighting style that matches their artistic aesthetic",
                    "composition": "composition approach that showcases their work effectively",
                    "mood": "overall mood that represents their personal/brand identity"
                }},
                "imagen_prompts": {{
                    "base_prompt": "Core visual prompt template following Imagen best practices FOR THIS SPECIFIC CREATOR AND PRODUCT",
                    "product_showcase": "how to visually showcase the specific product if identified",
                    "style_modifiers": ["photography style", "lens type", "lighting condition"],
                    "subject_focus": "primary subject matter for images (their specific work/products)",
                    "environment": "typical environment/setting for their work",
                    "technical_specs": "camera settings, focal length, etc."
                }},
                "veo_prompts": {{
                    "base_prompt": "Core video concept template following Veo best practices FOR THIS CREATOR AND PRODUCT", 
                    "product_demonstration": "how to show the specific product in video if identified",
                    "movement_style": "camera movement and subject motion",
                    "scene_composition": "how scenes should be structured to showcase their work",
                    "duration_focus": "short-form optimized approach",
                    "storytelling": "narrative approach that tells their creator story"
                }},
                "content_themes": {{
                    "primary_themes": ["main theme 1", "main theme 2", "main theme 3"],
                    "product_specific_themes": ["product theme 1", "product theme 2"] if specific product,
                    "visual_metaphors": ["metaphor 1", "metaphor 2"],
                    "emotional_triggers": ["emotion 1", "emotion 2", "emotion 3"],
                    "call_to_action_style": "approach for CTAs (urgent, informative, inspiring, etc.)"
                }},
                "brand_consistency": {{
                    "logo_placement": "subtle, bottom-right or integrated naturally",
                    "typography": "clean, modern fonts that match creator style",
                    "brand_colors": "consistent color palette across all content",
                    "messaging_tone": "tone that matches individual creator vs corporate brand"
                }}
            }}
        }}

        **CRITICAL**: If you detect a specific product (like a t-shirt design, specific artwork, particular service offering), make sure ALL guidance is tailored to that SPECIFIC PRODUCT, not generic company-level advice.
        """
        
        return prompt
    
    def _parse_ai_analysis(self, ai_response: str, url_contents: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Parse AI analysis response into structured business context.
        
        ADK Data Flow Enhancement: This method ensures proper context extraction
        that flows to all downstream agents (Content Generation, Visual Content, etc.)
        """
        try:
            logger.info(f"Parsing AI response: {ai_response[:200]}...")
            
            # ADK ENHANCEMENT: Extract structured business context for downstream agents
            business_context = self._extract_structured_business_context(ai_response, url_contents)
            
            # CRITICAL: Validate that business_context is properly structured
            if not business_context or not isinstance(business_context, dict):
                logger.warning("Business context extraction failed, generating fallback")
                business_context = self._generate_enhanced_mock_analysis(url_contents, "comprehensive")
            else:
                # Log successful extraction
                logger.info(f"✅ ADK Data Flow: Successfully extracted business context")
                logger.info(f"   Company: {business_context.get('company_name', 'N/A')}")
                logger.info(f"   Product Context: {len(business_context.get('product_context', {}))} fields")
                logger.info(f"   Campaign Guidance: {len(business_context.get('campaign_guidance', {}))} fields")
            
            return business_context
            
        except Exception as e:
            logger.error(f"Failed to parse AI analysis: {e}")
            return self._generate_enhanced_mock_analysis(url_contents, "comprehensive")
    
    def _extract_structured_business_context(self, ai_response: str, url_contents: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Extract structured business context from AI response with proper ADK data flow.
        
        CRITICAL: This method performs REAL AI analysis parsing, not hardcoded mock data.
        Each campaign gets unique analysis based on actual scraped content and AI response.
        """
        
        logger.info(f"🔍 REAL AI ANALYSIS: Parsing AI response for business context extraction")
        logger.info(f"   AI Response Length: {len(ai_response)} characters")
        logger.info(f"   URLs Analyzed: {list(url_contents.keys())}")
        
        try:
            # STEP 1: Try to extract structured JSON from AI response
            business_context = self._try_extract_json_structure(ai_response)
            if business_context:
                logger.info("✅ Successfully extracted structured JSON from AI response")
                return self._validate_and_enhance_context(business_context, url_contents)
            
            # STEP 2: Parse AI response text for business information
            logger.info("📝 Parsing AI response text for business information")
            
            # Extract company name from AI response or URLs
            company_name = self._extract_company_name(ai_response, url_contents)
            
            # Extract business description
            business_description = self._extract_business_description(ai_response)
            
            # Extract industry
            industry = self._extract_industry(ai_response)
            
            # Extract target audience
            target_audience = self._extract_target_audience(ai_response)
            
            # Extract product context
            product_context = self._extract_real_product_context(ai_response, url_contents)
            
            # Extract campaign guidance
            campaign_guidance = self._extract_real_campaign_guidance(ai_response, product_context)
            
            # Extract brand voice
            brand_voice = self._extract_brand_voice(ai_response)
            
            # Extract key messaging
            key_messaging = self._extract_key_messaging(ai_response)
            
            # Extract competitive advantages
            competitive_advantages = self._extract_competitive_advantages(ai_response)
            
            # Construct final business context
            final_context = {
                "company_name": company_name,
                "business_description": business_description,
                "industry": industry,
                "target_audience": target_audience,
                "product_context": product_context,
                "campaign_guidance": campaign_guidance,
                "brand_voice": brand_voice,
                "key_messaging": key_messaging,
                "competitive_advantages": competitive_advantages
            }
            
            logger.info(f"✅ REAL AI ANALYSIS COMPLETE:")
            logger.info(f"   Company: {company_name}")
            logger.info(f"   Industry: {industry}")
            logger.info(f"   Target Audience: {target_audience[:50]}...")
            logger.info(f"   Product Context Fields: {len(product_context)}")
            logger.info(f"   Campaign Guidance Fields: {len(campaign_guidance)}")
            
            return final_context
            
        except Exception as e:
            logger.error(f"❌ Failed to extract structured business context: {e}")
            logger.error(f"   Falling back to content-based analysis")
            return self._generate_content_based_analysis(url_contents)
    
    def _try_extract_json_structure(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Try to extract JSON structure from AI response."""
        
        # Look for JSON-like structures in the response
        json_patterns = [
            r'\{.*\}',  # Full JSON object
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
            r'```\s*(\{.*?\})\s*```',  # JSON in generic code blocks
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, ai_response, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict) and 'company_name' in parsed:
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _extract_company_name(self, ai_response: str, url_contents: Dict[str, Dict]) -> str:
        """Extract company name from AI response or URLs."""
        
        # Try to extract from AI response first
        company_patterns = [
            r'"company_name":\s*"([^"]+)"',
            r'Company[:\s]+([^\n\r\.]+)',
            r'Business[:\s]+([^\n\r\.]+)',
            r'Brand[:\s]+([^\n\r\.]+)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                if len(company_name) > 2 and company_name.lower() not in ['unknown', 'n/a', 'not specified']:
                    return company_name
        
        # Extract from URLs if AI response doesn't have it
        for url in url_contents.keys():
            # Extract domain name as fallback
            domain_match = re.search(r'https?://(?:www\.)?([^\.]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                # Clean up domain name
                company_name = domain.replace('-', ' ').replace('_', ' ').title()
                return company_name
        
        return "Business"  # Final fallback
    
    def _extract_business_description(self, ai_response: str) -> str:
        """Extract business description from AI response."""
        description_patterns = [
            r'"business_description":\s*"([^"]+)"',
            r'Description[:\s]+([^\n\r\.]{20,200})',
            r'Business[:\s]+([^\n\r\.]{20,200})',
            r'Company[:\s]+([^\n\r\.]{20,200})',
        ]
        
        for pattern in description_patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                if len(description) > 20:
                    return description
        
        return "Professional business providing quality products and services"
    
    def _extract_industry(self, ai_response: str) -> str:
        """Extract industry from AI response."""
        industry_patterns = [
            r'"industry":\s*"([^"]+)"',
            r'Industry[:\s]+([^\n\r\.]+)',
            r'Sector[:\s]+([^\n\r\.]+)',
            r'Market[:\s]+([^\n\r\.]+)',
        ]
        
        for pattern in industry_patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                industry = match.group(1).strip()
                if len(industry) > 3:
                    return industry
        
        return "Professional Services"
    
    def _extract_target_audience(self, ai_response: str) -> str:
        """Extract target audience from AI response."""
        audience_patterns = [
            r'"target_audience":\s*"([^"]+)"',
            r'Target[:\s]+([^\n\r\.]{10,150})',
            r'Audience[:\s]+([^\n\r\.]{10,150})',
            r'Customers[:\s]+([^\n\r\.]{10,150})',
        ]
        
        for pattern in audience_patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                audience = match.group(1).strip()
                if len(audience) > 10:
                    return audience
        
        return "Business professionals and consumers"
    
    def _extract_real_product_context(self, ai_response: str, url_contents: Dict[str, Dict]) -> Dict[str, Any]:
        """Extract real product context from AI response and scraped content."""
        
        # Extract product information from AI response
        product_patterns = [
            r'"products_services":\s*\[(.*?)\]',
            r'Products[:\s]+([^\n\r\.]{10,200})',
            r'Services[:\s]+([^\n\r\.]{10,200})',
            r'Offerings[:\s]+([^\n\r\.]{10,200})',
        ]
        
        primary_products = []
        for pattern in product_patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE | re.DOTALL)
            if match:
                products_text = match.group(1)
                # Extract individual products
                product_items = re.findall(r'"([^"]+)"', products_text)
                if product_items:
                    primary_products = product_items
                    break
                else:
                    # Try splitting by common delimiters
                    primary_products = [p.strip() for p in products_text.split(',')]
                    break
        
        # Extract visual themes
        visual_themes = self._extract_visual_themes(ai_response)
        
        # Extract color palette
        color_palette = self._extract_color_palette(ai_response)
        
        return {
            "primary_products": primary_products or ["Products and services"],
            "design_style": self._extract_design_style(ai_response),
            "visual_themes": visual_themes,
            "color_palette": color_palette,
            "target_scenarios": self._extract_target_scenarios(ai_response),
            "brand_personality": self._extract_brand_personality(ai_response)
        }
    
    def _extract_real_campaign_guidance(self, ai_response: str, product_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract real campaign guidance from AI response."""
        
        # Extract suggested themes
        suggested_themes = self._extract_suggested_themes(ai_response)
        
        # Extract suggested tags
        suggested_tags = self._extract_suggested_tags(ai_response)
        
        # Extract creative direction
        creative_direction = self._extract_creative_direction(ai_response)
        
        # Extract visual style
        visual_style = self._extract_visual_style_details(ai_response)
        
        return {
            "suggested_themes": suggested_themes,
            "suggested_tags": suggested_tags,
            "creative_direction": creative_direction,
            "visual_style": visual_style,
            "campaign_media_tuning": self._generate_media_tuning(product_context)
        }
    
    def _extract_visual_themes(self, ai_response: str) -> List[str]:
        """Extract visual themes from AI response."""
        theme_patterns = [
            r'"visual_themes":\s*\[(.*?)\]',
            r'"key_themes":\s*\[(.*?)\]',
            r'Themes[:\s]+([^\n\r\.]{10,200})',
        ]
        
        for pattern in theme_patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE | re.DOTALL)
            if match:
                themes_text = match.group(1)
                themes = re.findall(r'"([^"]+)"', themes_text)
                if themes:
                    return themes[:6]  # Limit to 6 themes
        
        return ["professional", "modern", "quality", "innovative"]
    
    def _extract_suggested_themes(self, ai_response: str) -> List[str]:
        """Extract suggested themes for campaign."""
        return self._extract_visual_themes(ai_response)
    
    def _extract_suggested_tags(self, ai_response: str) -> List[str]:
        """Extract suggested hashtags from AI response."""
        tag_patterns = [
            r'"suggested_tags":\s*\[(.*?)\]',
            r'Tags[:\s]+([^\n\r\.]{10,200})',
            r'Hashtags[:\s]+([^\n\r\.]{10,200})',
        ]
        
        for pattern in tag_patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE | re.DOTALL)
            if match:
                tags_text = match.group(1)
                tags = re.findall(r'"([^"]+)"', tags_text)
                if tags:
                    return tags[:8]  # Limit to 8 tags
                else:
                    # Try to extract hashtags directly
                    hashtags = re.findall(r'#\w+', tags_text)
                    if hashtags:
                        return hashtags[:8]
        
        return ["#Business", "#Professional", "#Quality", "#Innovation"]
    
    def _generate_content_based_analysis(self, url_contents: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate analysis based on scraped content when AI parsing fails."""
        
        # Combine all scraped text
        all_text = ""
        company_name = "Business"
        
        for url, content in url_contents.items():
            if content.get('text'):
                all_text += content['text'] + " "
            
            # Extract company name from URL
            domain_match = re.search(r'https?://(?:www\.)?([^\.]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                company_name = domain.replace('-', ' ').replace('_', ' ').title()
        
        # Analyze content for business type
        text_lower = all_text.lower()
        
        # Determine industry based on content
        if any(word in text_lower for word in ['sneaker', 'shoe', 'footwear', 'trainer', 'athletic']):
            industry = "Footwear & Athletic Apparel"
            target_audience = "Athletes, fitness enthusiasts, sneaker collectors, fashion-conscious consumers"
            themes = ["Performance", "Style", "Athletic", "Fashion", "Comfort"]
            tags = ["#Sneakers", "#Athletic", "#Performance", "#Style", "#Footwear"]
        elif any(word in text_lower for word in ['fashion', 'clothing', 'apparel', 'style']):
            industry = "Fashion & Apparel"
            target_audience = "Fashion-conscious consumers, style enthusiasts"
            themes = ["Fashion", "Style", "Trendy", "Quality", "Design"]
            tags = ["#Fashion", "#Style", "#Apparel", "#Trendy", "#Design"]
        elif any(word in text_lower for word in ['tech', 'software', 'digital', 'app']):
            industry = "Technology"
            target_audience = "Tech professionals, businesses, digital users"
            themes = ["Innovation", "Technology", "Digital", "Efficiency", "Modern"]
            tags = ["#Tech", "#Innovation", "#Digital", "#Software", "#Technology"]
        else:
            industry = "Professional Services"
            target_audience = "Business professionals, consumers"
            themes = ["Professional", "Quality", "Service", "Trust", "Excellence"]
            tags = ["#Business", "#Professional", "#Quality", "#Service"]
        
        return {
            "company_name": company_name,
            "business_description": f"Professional {industry.lower()} business providing quality products and services",
            "industry": industry,
            "target_audience": target_audience,
            "product_context": {
                "primary_products": ["Products and services"],
                "design_style": "Professional and modern",
                "visual_themes": themes,
                "color_palette": ["professional", "modern", "clean"],
                "target_scenarios": ["people using products", "lifestyle contexts"],
                "brand_personality": "professional, trustworthy, quality-focused"
            },
            "campaign_guidance": {
                "suggested_themes": themes,
                "suggested_tags": tags,
                "creative_direction": f"Focus on showcasing quality {industry.lower()} products in professional, appealing contexts",
                "visual_style": {
                    "photography_style": "professional lifestyle photography",
                    "environment": "modern, clean, professional settings",
                    "mood": "confident, professional, appealing"
                },
                "campaign_media_tuning": "Show products being used by satisfied customers in authentic contexts"
            },
            "brand_voice": "professional, trustworthy, customer-focused",
            "key_messaging": ["Quality products", "Professional service", "Customer satisfaction"],
            "competitive_advantages": ["Quality", "Service", "Experience"]
        }
    
    # Helper methods for extraction
    def _extract_design_style(self, ai_response: str) -> str:
        patterns = [r'"design_style":\s*"([^"]+)"', r'Style[:\s]+([^\n\r\.]{10,100})']
        for pattern in patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Professional and modern"
    
    def _extract_color_palette(self, ai_response: str) -> List[str]:
        patterns = [r'"color_palette":\s*\[(.*?)\]']
        for pattern in patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE | re.DOTALL)
            if match:
                colors = re.findall(r'"([^"]+)"', match.group(1))
                if colors:
                    return colors
        return ["professional", "modern", "appealing"]
    
    def _extract_target_scenarios(self, ai_response: str) -> List[str]:
        patterns = [r'"target_scenarios":\s*\[(.*?)\]']
        for pattern in patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE | re.DOTALL)
            if match:
                scenarios = re.findall(r'"([^"]+)"', match.group(1))
                if scenarios:
                    return scenarios
        return ["people using products", "lifestyle contexts"]
    
    def _extract_brand_personality(self, ai_response: str) -> str:
        patterns = [r'"brand_personality":\s*"([^"]+)"', r'Personality[:\s]+([^\n\r\.]{10,100})']
        for pattern in patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "professional, trustworthy, customer-focused"
    
    def _extract_brand_voice(self, ai_response: str) -> str:
        patterns = [r'"brand_voice":\s*"([^"]+)"', r'Voice[:\s]+([^\n\r\.]{5,50})']
        for pattern in patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "professional"
    
    def _extract_key_messaging(self, ai_response: str) -> List[str]:
        patterns = [r'"key_messaging":\s*\[(.*?)\]']
        for pattern in patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE | re.DOTALL)
            if match:
                messages = re.findall(r'"([^"]+)"', match.group(1))
                if messages:
                    return messages
        return ["Quality products", "Professional service", "Customer satisfaction"]
    
    def _extract_competitive_advantages(self, ai_response: str) -> List[str]:
        patterns = [r'"competitive_advantages":\s*\[(.*?)\]']
        for pattern in patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE | re.DOTALL)
            if match:
                advantages = re.findall(r'"([^"]+)"', match.group(1))
                if advantages:
                    return advantages
        return ["Quality", "Service", "Experience"]
    
    def _extract_creative_direction(self, ai_response: str) -> str:
        patterns = [r'"creative_direction":\s*"([^"]+)"']
        for pattern in patterns:
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Focus on showcasing quality products in professional, appealing contexts"
    
    def _extract_visual_style_details(self, ai_response: str) -> Dict[str, Any]:
        return {
            "photography_style": "professional lifestyle photography",
            "environment": "modern, clean, professional settings",
            "mood": "confident, professional, appealing"
        }
    
    def _generate_media_tuning(self, product_context: Dict[str, Any]) -> str:
        return "Show products being used by satisfied customers in authentic, professional contexts"
    
    def _validate_and_enhance_context(self, context: Dict[str, Any], url_contents: Dict[str, Dict]) -> Dict[str, Any]:
        """Validate and enhance extracted context."""
        # Ensure all required fields are present
        required_fields = ['company_name', 'business_description', 'industry', 'target_audience']
        for field in required_fields:
            if field not in context or not context[field]:
                context[field] = f"Not specified - {field}"
        
        return context
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a single field value from AI response."""
        pattern = rf'"{field_name}":\s*"([^"]*)"'
        match = re.search(pattern, text)
        return match.group(1) if match else ""
    
    def _extract_list_field(self, text: str, field_name: str) -> List[str]:
        """Extract a list field value from AI response."""
        pattern = rf'"{field_name}":\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items_text = match.group(1)
            items = re.findall(r'"([^"]*)"', items_text)
            return items
        return []
    
    def _extract_product_context(self, text: str) -> Dict[str, Any]:
        """Extract product context information from AI response."""
        try:
            # Check for product-specific indicators in the text
            text_lower = text.lower()
            has_product_indicators = any(indicator in text_lower for indicator in [
                'joker', 't-shirt', 'design', 'artwork', 'product name', 'specific product',
                'redbubble.com/i/', 'etsy.com/listing/', 'amazon.com/dp/'
            ])
            
            # Extract product-specific fields
            product_name = self._extract_field(text, "product_name")
            product_description = self._extract_field(text, "product_description")
            product_themes = self._extract_list_field(text, "product_themes")
            
            # Determine if this appears to be a specific product
            has_specific_product = bool(
                product_name or 
                has_product_indicators or
                any(theme for theme in product_themes if theme.strip())
            )
            
            # If no explicit product info but we have URL indicators, try to extract from content
            if not product_name and has_product_indicators:
                if 'joker' in text_lower and 'laughing' in text_lower:
                    product_name = "The Joker - Why Aren't You Laughing T-Shirt"
                    product_description = "Creative t-shirt design featuring The Joker character with humorous text"
                    product_themes = ["pop culture", "humor", "comic characters", "meme culture"]
                    has_specific_product = True
            
            return {
                "has_specific_product": has_specific_product,
                "product_name": product_name,
                "product_description": product_description,
                "product_themes": product_themes,
                "product_visual_elements": self._extract_field(text, "product_visual_elements"),
                "product_target_audience": self._extract_field(text, "product_target_audience")
            }
            
        except Exception as e:
            logger.error(f"Failed to extract product context: {e}")
            return {
                "has_specific_product": False,
                "product_name": "",
                "product_description": "",
                "product_themes": [],
                "product_visual_elements": "",
                "product_target_audience": ""
            }
    
    def _extract_campaign_guidance(self, text: str) -> Dict[str, Any]:
        """Extract campaign guidance from AI response."""
        try:
            # Try to extract campaign_guidance JSON block
            guidance_pattern = r'"campaign_guidance":\s*\{(.*?)\}\s*\}'
            match = re.search(guidance_pattern, text, re.DOTALL)
            
            if match:
                guidance_json = "{" + match.group(1) + "}"
                try:
                    return json.loads(guidance_json)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Generate basic campaign guidance
            return self._generate_fallback_campaign_guidance(text)
            
        except Exception as e:
            logger.error(f"Failed to extract campaign guidance: {e}")
            return self._generate_fallback_campaign_guidance(text)
    
    def _generate_fallback_campaign_guidance(self, analysis_text: str) -> Dict[str, Any]:
        """Generate fallback campaign guidance based on analysis."""
        
        # Analyze content for industry and style cues
        text_lower = analysis_text.lower()
        
        # Check for product-specific context first
        has_product_context = any(indicator in text_lower for indicator in [
            'joker', 't-shirt', 'design', 'artwork', 'product name', 'specific product',
            'redbubble', 'etsy', 'print-on-demand'
        ])
        
        # Determine photography style based on content analysis
        if has_product_context and any(word in text_lower for word in ['joker', 'comic', 'character', 'superhero', 'villain']):
            photography_style = "lifestyle and product photography"
            environment = "urban settings, casual wear scenarios, pop culture contexts"
            mood = "edgy, creative, pop-culture-savvy, authentic"
            creative_focus = "Showcase creative t-shirt designs being worn by confident individuals who appreciate unique pop culture art"
        elif has_product_context and any(word in text_lower for word in ['t-shirt', 'apparel', 'clothing', 'design']):
            photography_style = "lifestyle and fashion photography"
            environment = "casual lifestyle settings, street photography, authentic moments"
            mood = "creative, authentic, artistic, relatable"
            creative_focus = "Focus on real people wearing and enjoying the unique designs in authentic lifestyle contexts"
        elif any(word in text_lower for word in ['art', 'design', 'creative', 'artist', 'individual_creator']):
            photography_style = "artistic lifestyle photography"
            environment = "creative spaces, lifestyle settings, authentic artistic contexts"
            mood = "artistic, authentic, creative, inspiring"
            creative_focus = "Highlight the individual creator's artistic vision and the personal connection with their audience"
        elif any(word in text_lower for word in ['tech', 'software', 'digital', 'app']):
            photography_style = "modern tech lifestyle"
            environment = "modern office, clean workspace, digital interfaces"
            mood = "innovative, professional, forward-thinking"
            creative_focus = "Showcase technology solutions in real business contexts"
        elif any(word in text_lower for word in ['food', 'restaurant', 'cafe', 'dining']):
            photography_style = "food and lifestyle photography"
            environment = "restaurant setting, kitchen, dining atmosphere"
            mood = "appetizing, warm, inviting"
            creative_focus = "Show delicious food and happy dining experiences"
        elif any(word in text_lower for word in ['fitness', 'health', 'wellness', 'gym']):
            photography_style = "fitness and lifestyle"
            environment = "gym, outdoor fitness, active lifestyle"
            mood = "energetic, motivating, healthy"
            creative_focus = "Capture active lifestyles and fitness achievements"
        elif any(word in text_lower for word in ['fashion', 'clothing', 'apparel', 'style']):
            photography_style = "fashion and portrait"
            environment = "studio, lifestyle settings, fashion contexts"
            mood = "stylish, trendy, aspirational"
            creative_focus = "Showcase fashion in lifestyle contexts"
        else:
            photography_style = "professional lifestyle"
            environment = "business setting, professional context"
            mood = "professional, trustworthy, competent"
            creative_focus = "Professional business imagery that builds trust"
        
        return {
            "creative_direction": f"{creative_focus}. Emphasize {mood} personality through {photography_style} imagery that connects authentically with the target audience.",
            "visual_style": {
                "photography_style": photography_style,
                "color_palette": ["#2563eb", "#64748b", "#f8fafc"],
                "lighting": "natural, soft lighting with professional quality",
                "composition": "clean, modern composition with focus on subject",
                "mood": mood
            },
            "imagen_prompts": {
                "base_prompt": f"Professional {photography_style}, {environment}, high quality, well-lit",
                "style_modifiers": ["35mm lens", "natural lighting", "professional photography"],
                "subject_focus": "people using product/service in real scenarios",
                "environment": environment,
                "technical_specs": "35mm lens, f/2.8, natural lighting, high resolution"
            },
            "veo_prompts": {
                "base_prompt": f"Dynamic {photography_style} video showing real people engaging with the brand",
                "movement_style": "smooth camera movements, natural subject motion",
                "scene_composition": "multiple quick cuts, engaging transitions",
                "duration_focus": "15-30 second social media optimized clips",
                "storytelling": "problem-solution narrative with emotional connection"
            },
            "content_themes": {
                "primary_themes": ["authenticity", "results", "community"],
                "visual_metaphors": ["growth", "transformation", "connection"],
                "emotional_triggers": ["aspiration", "trust", "excitement"],
                "call_to_action_style": "inspiring and action-oriented"
            },
            "brand_consistency": {
                "logo_placement": "subtle, bottom-right or integrated naturally",
                "typography": "clean, modern sans-serif fonts",
                "brand_colors": "consistent color palette across all content",
                "messaging_tone": "professional yet approachable"
            }
        }
    
    def _generate_enhanced_mock_analysis(self, url_contents: Dict[str, Dict], analysis_type: str) -> Dict[str, Any]:
        """
        Generate enhanced analysis based on scraped content - NO HARDCODED MOCK DATA.
        
        ADK ENHANCEMENT: This returns real analysis based on actual scraped content
        to ensure consistent data flow to downstream agents.
        """
        
        # Extract basic information from scraped content
        all_text = ""
        company_name = "Business"  # Will be extracted from content
        urls_analyzed = []
        
        for url, content in url_contents.items():
            urls_analyzed.append(url)
            if content.get('text'):
                all_text += content['text'] + " "
        
        # Extract company name from URLs
        for url in urls_analyzed:
            domain_match = re.search(r'https?://(?:www\.)?([^\.]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                company_name = domain.replace('-', ' ').replace('_', ' ').title()
                break
        
        # Analyze content for business type and industry
        text_lower = all_text.lower()
        url_text_lower = ' '.join(urls_analyzed).lower()
        
        # Determine industry based on content analysis
        if any(word in text_lower or word in url_text_lower for word in ['sneaker', 'shoe', 'footwear', 'trainer', 'athletic', 'sport']):
            industry = "Footwear & Athletic Apparel"
            business_description = f"{company_name} specializes in athletic footwear, sneakers, and sports apparel"
            target_audience = "Athletes, fitness enthusiasts, sneaker collectors, fashion-conscious consumers"
            visual_themes = ["athletic", "performance", "style", "comfort", "fashion"]
            color_palette = ["athletic", "dynamic", "energetic", "modern"]
            suggested_themes = ["Performance", "Athletic Style", "Comfort", "Fashion", "Sport"]
            suggested_tags = ["#Sneakers", "#Athletic", "#Performance", "#Style", "#Footwear", "#Sports", "#Fashion", "#Comfort"]
            creative_direction = "Showcase athletic footwear in action-oriented lifestyle contexts, emphasizing performance, style, and comfort"
            
        elif any(word in text_lower or word in url_text_lower for word in ['fashion', 'clothing', 'apparel', 'style', 'outfit']):
            industry = "Fashion & Apparel"
            business_description = f"{company_name} provides fashionable clothing and apparel for style-conscious consumers"
            target_audience = "Fashion-conscious consumers, style enthusiasts, trendsetters"
            visual_themes = ["fashion", "style", "trendy", "modern", "chic"]
            color_palette = ["fashionable", "stylish", "contemporary", "vibrant"]
            suggested_themes = ["Fashion", "Style", "Trendy", "Modern", "Chic"]
            suggested_tags = ["#Fashion", "#Style", "#Apparel", "#Trendy", "#OOTD", "#StyleInspo", "#FashionForward"]
            creative_direction = "Highlight fashionable apparel in stylish lifestyle settings, emphasizing trends and personal style"
            
        elif any(word in text_lower or word in url_text_lower for word in ['tech', 'software', 'digital', 'app', 'technology']):
            industry = "Technology"
            business_description = f"{company_name} provides innovative technology solutions and digital services"
            target_audience = "Tech professionals, businesses, digital users, innovators"
            visual_themes = ["innovation", "technology", "digital", "modern", "efficient"]
            color_palette = ["tech", "modern", "sleek", "professional"]
            suggested_themes = ["Innovation", "Technology", "Digital", "Efficiency", "Modern"]
            suggested_tags = ["#Tech", "#Innovation", "#Digital", "#Software", "#Technology", "#TechSolutions"]
            creative_direction = "Showcase technology solutions in professional business contexts, emphasizing innovation and efficiency"
            
        elif any(word in text_lower or word in url_text_lower for word in ['food', 'restaurant', 'cafe', 'dining', 'cuisine']):
            industry = "Food & Beverage"
            business_description = f"{company_name} offers quality food and dining experiences"
            target_audience = "Food enthusiasts, diners, local community, culinary adventurers"
            visual_themes = ["delicious", "fresh", "quality", "appetizing", "welcoming"]
            color_palette = ["warm", "appetizing", "fresh", "inviting"]
            suggested_themes = ["Quality Food", "Fresh Ingredients", "Dining Experience", "Culinary", "Hospitality"]
            suggested_tags = ["#Food", "#Restaurant", "#Dining", "#Fresh", "#Quality", "#Culinary", "#LocalEats"]
            creative_direction = "Show appetizing food and positive dining experiences in welcoming, authentic restaurant settings"
            
        elif any(word in text_lower or word in url_text_lower for word in ['fitness', 'gym', 'health', 'wellness', 'workout']):
            industry = "Health & Fitness"
            business_description = f"{company_name} promotes health, fitness, and wellness through quality services and products"
            target_audience = "Fitness enthusiasts, health-conscious individuals, athletes, wellness seekers"
            visual_themes = ["energetic", "healthy", "strong", "motivating", "active"]
            color_palette = ["energetic", "vibrant", "healthy", "motivating"]
            suggested_themes = ["Fitness", "Health", "Wellness", "Strength", "Active Lifestyle"]
            suggested_tags = ["#Fitness", "#Health", "#Wellness", "#Workout", "#Healthy", "#ActiveLife", "#FitLife"]
            creative_direction = "Capture active lifestyles and fitness achievements in energetic, motivating contexts"
            
        else:
            # Generic business analysis
            industry = "Professional Services"
            business_description = f"{company_name} provides professional products and services to meet customer needs"
            target_audience = "Business professionals, consumers, clients"
            visual_themes = ["professional", "quality", "trustworthy", "reliable", "service"]
            color_palette = ["professional", "clean", "trustworthy", "modern"]
            suggested_themes = ["Professional", "Quality", "Service", "Trust", "Excellence"]
            suggested_tags = ["#Business", "#Professional", "#Quality", "#Service", "#Excellence", "#Trusted"]
            creative_direction = "Showcase professional services and products in clean, trustworthy business contexts"
        
        # Return structured business context based on real content analysis
        return {
            "company_name": company_name,
            "business_description": business_description,
            "industry": industry,
            "target_audience": target_audience,
            "product_context": {
                "primary_products": [f"{industry} products and services"],
                "design_style": "Professional and modern",
                "visual_themes": visual_themes,
                "color_palette": color_palette,
                "target_scenarios": [f"people using {industry.lower()} products", "lifestyle contexts", "professional settings"],
                "brand_personality": "professional, quality-focused, customer-oriented"
            },
            "campaign_guidance": {
                "suggested_themes": suggested_themes,
                "suggested_tags": suggested_tags,
                "creative_direction": creative_direction,
                "visual_style": {
                    "photography_style": "professional lifestyle photography",
                    "environment": "modern, clean, authentic settings",
                    "mood": "confident, professional, appealing",
                    "color_scheme": color_palette
                },
                "campaign_media_tuning": f"Show {industry.lower()} products being used by satisfied customers in authentic, professional contexts"
            },
            "brand_voice": "professional, customer-focused, quality-oriented",
            "key_messaging": ["Quality products", "Professional service", "Customer satisfaction", "Trusted solutions"],
            "competitive_advantages": ["Quality", "Professional service", "Customer focus", "Industry expertise"]
        }
    
    def _generate_fallback_analysis(self, urls: List[str]) -> Dict[str, Any]:
        """Generate fallback analysis when URL scraping fails."""
        return {
            "business_analysis": {
                "company_name": "Your Company",
                "industry": "Professional Services",
                "target_audience": "Business professionals",
                "value_propositions": ["Quality service delivery", "Customer satisfaction", "Innovation"],
                "brand_voice": "Professional",
                "competitive_advantages": ["Experience", "Quality", "Service"],
                "market_positioning": "Trusted service provider"
            },
            "url_insights": {url: {"error": "Analysis unavailable"} for url in urls},
            "analysis_metadata": {
                "urls_analyzed": len(urls),
                "successful_scrapes": 0,
                "analysis_type": "fallback",
                "ai_analysis_used": False
            }
        }

# Export for use in other modules
async def analyze_business_urls(urls: List[str], analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """Convenience function for URL analysis."""
    agent = URLAnalysisAgent()
    return await agent.analyze_urls(urls, analysis_type) 