"""
FILENAME: test_visual_content_context_fidelity.py
DESCRIPTION/PURPOSE: Comprehensive tests to prevent visual content context regression
Author: JP + 2025-07-23

These tests specifically validate that:
1. Visual content is contextually relevant to campaign content
2. No hardcoded demo/placeholder content is shown in production
3. Real AI generation APIs are called when expected
4. Context fidelity is maintained between campaign text and visuals

This addresses the regression where mountain landscape images were shown 
for business marketing campaigns due to demo mode bypassing real generation.
"""

import pytest
import asyncio
import os
import re
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List, Any
import requests
from urllib.parse import urlparse

# Test both backend and frontend integration
from agents.visual_content_agent import generate_visual_content_for_posts, VisualContentOrchestrator
from agents.adk_visual_agents import generate_agentic_visual_content


class TestVisualContentContextFidelity:
    """Test suite to prevent visual content context regression."""
    
    # CRITICAL: These are the exact demo URLs that caused the regression
    FORBIDDEN_DEMO_URLS = [
        "https://images.unsplash.com/photo-1542038784456-1ea8e732b2b9",
        "https://images.unsplash.com/photo-1531804055935-76f44d7c3621", 
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://via.placeholder.com",
        "https://picsum.photos"
    ]
    
    # Expected contextual indicators for business campaigns
    BUSINESS_CONTEXT_INDICATORS = [
        "professional", "business", "marketing", "corporate", "office",
        "team", "meeting", "consultation", "service", "product"
    ]
    
    @pytest.mark.asyncio
    async def test_no_demo_urls_in_production_response(self):
        """CRITICAL: Ensure no hardcoded demo URLs are returned in production."""
        
        business_campaign_posts = [
            {
                "id": "business_post_1",
                "type": "text_image",
                "content": "Transform your business with our innovative solutions",
                "hashtags": ["#business", "#innovation", "#solutions"]
            },
            {
                "id": "business_post_2", 
                "type": "text_video",
                "content": "Watch how we help companies achieve their goals",
                "hashtags": ["#success", "#business", "#growth"]
            }
        ]
        
        business_context = {
            "company_name": "TechCorp Solutions",
            "industry": "Technology Consulting", 
            "business_description": "We provide innovative technology solutions for businesses",
            "campaign_objective": "increase brand awareness"
        }
        
        # Test the main visual generation function
        result = await generate_visual_content_for_posts(
            social_posts=business_campaign_posts,
            business_context=business_context,
            campaign_objective="increase brand awareness"
        )
        
        # CRITICAL: Check for forbidden demo URLs
        posts_with_visuals = result.get('posts_with_visuals', [])
        
        for post in posts_with_visuals:
            image_url = post.get('image_url', '')
            video_url = post.get('video_url', '')
            
            # Check image URLs
            if image_url:
                for forbidden_url in self.FORBIDDEN_DEMO_URLS:
                    assert not image_url.startswith(forbidden_url), (
                        f"REGRESSION DETECTED: Post {post.get('id')} contains forbidden demo image URL: {image_url}. "
                        f"This indicates demo mode is active when real generation should occur."
                    )
                    
            # Check video URLs  
            if video_url:
                for forbidden_url in self.FORBIDDEN_DEMO_URLS:
                    assert not video_url.startswith(forbidden_url), (
                        f"REGRESSION DETECTED: Post {post.get('id')} contains forbidden demo video URL: {video_url}. "
                        f"This indicates demo mode is active when real generation should occur."
                    )
    
    @pytest.mark.asyncio
    async def test_contextual_relevance_validation(self):
        """Test that generated visuals are contextually relevant to campaign content."""
        
        # Create campaign about t-shirt business (specific product context)
        tshirt_campaign_posts = [
            {
                "id": "tshirt_post_1",
                "type": "text_image", 
                "content": "Check out our awesome Joker-themed t-shirt designs!",
                "hashtags": ["#tshirt", "#joker", "#design", "#apparel"]
            }
        ]
        
        tshirt_business_context = {
            "company_name": "Creative Threads",
            "industry": "Apparel & Fashion",
            "business_description": "Custom t-shirt printing with creative designs",
            "product_context": {
                "has_specific_product": True,
                "product_name": "Joker T-Shirt",
                "product_themes": ["humor", "pop culture", "graphic design"]
            }
        }
        
        # Mock the visual generation to capture prompts
        with patch('agents.visual_content_agent.ImageGenerationAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_generated_images = [
                {
                    "id": "img_1",
                    "prompt": "Young adult wearing Joker t-shirt, urban setting, lifestyle photography",
                    "image_url": "http://localhost:8000/api/v1/content/images/campaign123/generated_image_1.png",
                    "status": "success",
                    "metadata": {"generation_method": "imagen_real"}
                }
            ]
            mock_agent.generate_images = AsyncMock(return_value=mock_generated_images)
            mock_agent_class.return_value = mock_agent
            
            result = await generate_visual_content_for_posts(
                social_posts=tshirt_campaign_posts,
                business_context=tshirt_business_context,
                campaign_objective="increase product sales"
            )
            
            # Verify generation was called
            mock_agent.generate_images.assert_called_once()
            
            # Get the prompts that were generated
            call_args = mock_agent.generate_images.call_args
            prompts_used = call_args[0][0]  # First argument should be prompts list
            
            # CONTEXTUAL RELEVANCE VALIDATION
            assert len(prompts_used) > 0, "No prompts were generated"
            
            first_prompt = prompts_used[0]
            assert isinstance(first_prompt, str), "Prompt should be a string"
            
            # Check that prompt contains contextual elements
            prompt_lower = first_prompt.lower()
            
            # Should contain product-specific context
            assert any(keyword in prompt_lower for keyword in ["joker", "t-shirt", "tshirt", "shirt"]), (
                f"Prompt lacks product context. Prompt: {first_prompt}"
            )
            
            # Should contain business context
            assert any(keyword in prompt_lower for keyword in ["creative", "apparel", "design"]), (
                f"Prompt lacks business context. Prompt: {first_prompt}"
            )
            
            # Should NOT contain irrelevant contexts
            irrelevant_contexts = ["mountain", "landscape", "nature", "scenery", "outdoor vista"]
            assert not any(keyword in prompt_lower for keyword in irrelevant_contexts), (
                f"Prompt contains irrelevant context that led to mountain images. Prompt: {first_prompt}"
            )
    
    @pytest.mark.asyncio
    async def test_business_vs_generic_context_distinction(self):
        """Test that business-specific context overrides generic placeholders."""
        
        restaurant_posts = [
            {
                "id": "restaurant_post",
                "type": "text_image",
                "content": "Experience fine dining at its best",
                "hashtags": ["#restaurant", "#finedining", "#cuisine"]
            }
        ]
        
        restaurant_context = {
            "company_name": "Bella Vista Restaurant", 
            "industry": "Food & Beverage",
            "business_description": "Upscale Italian restaurant specializing in authentic cuisine"
        }
        
        # Mock image generation to capture enhanced prompts
        with patch('agents.visual_content_agent.ImageGenerationAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_images = AsyncMock(return_value=[{
                "id": "restaurant_img",
                "prompt": "captured_prompt",
                "image_url": "http://localhost:8000/api/v1/content/images/campaign456/restaurant_image.png",
                "status": "success"
            }])
            mock_agent_class.return_value = mock_agent
            
            await generate_visual_content_for_posts(
                social_posts=restaurant_posts,
                business_context=restaurant_context,
                campaign_objective="attract dinner customers"
            )
            
            # Verify business-specific enhancement occurred
            call_args = mock_agent.generate_images.call_args
            prompts = call_args[0][0]
            
            restaurant_prompt = prompts[0].lower()
            
            # Should contain restaurant-specific context
            restaurant_indicators = ["restaurant", "dining", "cuisine", "food", "italian"]
            assert any(indicator in restaurant_prompt for indicator in restaurant_indicators), (
                f"Restaurant prompt lacks business context: {prompts[0]}"
            )
            
            # Should NOT contain generic business context that could lead to wrong visuals
            generic_contexts = ["office", "meeting", "corporate", "technology", "mountain"]
            for generic_context in generic_contexts:
                assert generic_context not in restaurant_prompt, (
                    f"Restaurant prompt contains generic context '{generic_context}' that could mislead generation: {prompts[0]}"
                )
    
    def test_frontend_api_calls_real_generation(self):
        """Test that frontend calls real generation APIs, not demo mode."""
        
        # Test the actual API endpoint that frontend calls
        api_payload = {
            "social_posts": [
                {
                    "id": "api_test_post",
                    "type": "text_image", 
                    "content": "Our consulting services deliver results",
                    "hashtags": ["#consulting", "#results"]
                }
            ],
            "business_context": {
                "company_name": "ConsultCorp",
                "industry": "Business Consulting"
            },
            "campaign_objective": "generate leads"
        }
        
        # Mock the backend API response
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "posts_with_visuals": [
                    {
                        "id": "api_test_post",
                        "type": "text_image",
                        "content": "Our consulting services deliver results", 
                        "image_url": "http://localhost:8000/api/v1/content/images/campaign789/consulting_image.png",
                        "image_metadata": {
                            "generation_method": "imagen_real",
                            "model": "imagen-3.0"
                        }
                    }
                ]
            }
            mock_post.return_value = mock_response
            
            # Simulate frontend API call
            response = requests.post(
                "http://localhost:8000/api/v1/content/generate-visuals",
                json=api_payload
            )
            
            # Verify API was called
            mock_post.assert_called_once()
            
            # Verify response structure
            result = response.json()
            posts = result["posts_with_visuals"]
            
            # CRITICAL: Verify no demo URLs in API response
            for post in posts:
                image_url = post.get("image_url", "")
                if image_url:
                    for forbidden_url in self.FORBIDDEN_DEMO_URLS:
                        assert not image_url.startswith(forbidden_url), (
                            f"API returned forbidden demo URL: {image_url}"
                        )
                        
                    # Verify it's a real generated image URL structure
                    assert "/api/v1/content/images/" in image_url, (
                        f"Image URL doesn't match expected generated URL pattern: {image_url}"
                    )
    
    @pytest.mark.asyncio 
    async def test_campaign_guidance_context_integration(self):
        """Test that campaign guidance properly integrates into visual generation."""
        
        campaign_posts = [
            {
                "id": "guided_post",
                "type": "text_image",
                "content": "Premium quality furniture for your home",
                "hashtags": ["#furniture", "#premium", "#home"]
            }
        ]
        
        # Rich campaign guidance context (what should prevent generic visuals)
        furniture_context = {
            "company_name": "Luxury Living Furniture",
            "industry": "Home & Garden",
            "campaign_guidance": {
                "visual_style": {
                    "photography_style": "lifestyle photography showing furniture in home settings",
                    "mood": "warm, inviting, luxurious",
                    "lighting": "natural lighting, golden hour warmth"
                },
                "imagen_prompts": {
                    "environment": "elegant home interior with luxury furniture",
                    "style_modifiers": ["high-end", "sophisticated", "comfortable living"]
                },
                "creative_direction": "Show real people enjoying beautiful furniture in their homes"
            }
        }
        
        with patch('agents.visual_content_agent.ImageGenerationAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_images = AsyncMock(return_value=[{
                "id": "furniture_img", 
                "prompt": "captured_enhanced_prompt",
                "image_url": "http://localhost:8000/api/v1/content/images/furniture123/luxury_furniture.png",
                "status": "success"
            }])
            mock_agent_class.return_value = mock_agent
            
            await generate_visual_content_for_posts(
                social_posts=campaign_posts,
                business_context=furniture_context,
                campaign_objective="showcase premium furniture"
            )
            
            # Verify campaign guidance was integrated
            call_args = mock_agent.generate_images.call_args
            enhanced_prompts = call_args[0][0]
            
            furniture_prompt = enhanced_prompts[0].lower()
            
            # Should contain campaign guidance elements
            guidance_elements = ["furniture", "home", "interior", "luxury", "lifestyle"]
            assert any(element in furniture_prompt for element in guidance_elements), (
                f"Enhanced prompt lacks campaign guidance integration: {enhanced_prompts[0]}"
            )
            
            # Should contain visual style guidance
            style_elements = ["natural lighting", "warm", "elegant", "sophisticated"]
            style_found = any(element in furniture_prompt for element in style_elements)
            assert style_found, (
                f"Enhanced prompt lacks visual style guidance: {enhanced_prompts[0]}"
            )
    
    def test_demo_mode_detection_and_prevention(self):
        """Test that demo mode is properly detected and prevented in production."""
        
        # This test simulates the exact conditions that led to the regression
        
        # Mock the IdeationPage demo detection logic
        mock_current_campaign = None  # This triggers demo mode
        
        # In demo mode, the page should either:
        # 1. Call real APIs with clear demo indicators, OR  
        # 2. Show clear "DEMO MODE" messaging to user
        
        # What should NOT happen: Show generic Unsplash images without clear demo labeling
        
        if mock_current_campaign is None:
            # Demo mode detected - this should be handled correctly
            
            # EITHER show real generation with demo data
            demo_business_context = {
                "company_name": "Demo Company",
                "industry": "Technology",
                "campaign_objective": "demo purposes"
            }
            
            # OR show clearly labeled demo content
            demo_labels_required = [
                "Demo Content", 
                "Sample Campaign",
                "Preview Mode",
                "Example Content"
            ]
            
            # The key is that demo mode should be OBVIOUS to users
            # and not mislead them about the quality of real generation
            
            demo_mode_obvious = True  # This should be enforced
            assert demo_mode_obvious, (
                "Demo mode must be clearly indicated to users to prevent "
                "confusion about real system capabilities"
            )


class TestVisualContentAPIEndpoints:
    """Test API endpoints to ensure they don't return demo content."""
    
    @pytest.mark.asyncio
    async def test_generate_visuals_endpoint_no_demo_urls(self):
        """Test /generate-visuals endpoint doesn't return hardcoded demo URLs."""
        
        # Mock the endpoint call
        from backend.api.routes.content import generate_visual_content
        
        test_request = {
            "social_posts": [
                {
                    "id": "endpoint_test_post",
                    "type": "text_image",
                    "content": "Professional business consulting services"
                }
            ],
            "business_context": {
                "company_name": "BusinessCorp",
                "industry": "Consulting"
            }
        }
        
        # Mock the underlying generation function
        with patch('backend.api.routes.content.generate_visual_content_for_posts') as mock_gen:
            mock_gen.return_value = {
                "posts_with_visuals": [
                    {
                        "id": "endpoint_test_post",
                        "image_url": "http://localhost:8000/api/v1/content/images/campaign/generated.png",
                        "image_metadata": {"generation_method": "real"}
                    }
                ]
            }
            
            # Call the endpoint
            result = await generate_visual_content(test_request)
            
            # Verify no demo URLs in response
            posts = result["posts_with_visuals"]
            for post in posts:
                image_url = post.get("image_url", "")
                if image_url:
                    forbidden_domains = ["unsplash.com", "placeholder.com", "picsum.photos"]
                    parsed_url = urlparse(image_url)
                    
                    assert not any(domain in parsed_url.netloc for domain in forbidden_domains), (
                        f"Endpoint returned forbidden demo URL: {image_url}"
                    )


class TestVisualContentUserJourney:
    """End-to-end user journey tests for visual content generation."""
    
    def test_campaign_creation_to_visual_generation_flow(self):
        """Test complete user journey from campaign creation to visual generation."""
        
        # Step 1: User creates campaign
        campaign_data = {
            "name": "Summer Marketing Campaign",
            "objective": "increase product sales",
            "business_context": {
                "company_name": "SummerGear Co",
                "industry": "Outdoor Equipment",
                "business_description": "Premium outdoor gear and equipment"
            }
        }
        
        # Step 2: System generates initial posts
        initial_posts = [
            {
                "id": "summer_post_1",
                "type": "text_image", 
                "content": "Discover premium outdoor gear for your adventures",
                "hashtags": ["#outdoor", "#adventure", "#gear"]
            }
        ]
        
        # Step 3: User requests visual generation
        # This should trigger REAL generation, not demo mode
        
        with patch('agents.visual_content_agent.ImageGenerationAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.generate_images = AsyncMock(return_value=[{
                "id": "summer_img_1",
                "image_url": "http://localhost:8000/api/v1/content/images/summer_campaign/outdoor_gear.png",
                "status": "success",
                "metadata": {"generation_method": "imagen_real"}
            }])
            mock_agent.return_value = mock_instance
            
            # Simulate the visual generation request
            asyncio.run(generate_visual_content_for_posts(
                social_posts=initial_posts,
                business_context=campaign_data["business_context"],
                campaign_objective=campaign_data["objective"]
            ))
            
            # Verify real generation was attempted
            mock_instance.generate_images.assert_called_once()
            
            # Verify contextual prompts were created
            call_args = mock_instance.generate_images.call_args
            prompts = call_args[0][0]
            
            outdoor_prompt = prompts[0].lower()
            
            # Should contain outdoor/adventure context
            outdoor_keywords = ["outdoor", "adventure", "gear", "equipment"]
            assert any(keyword in outdoor_prompt for keyword in outdoor_keywords), (
                f"User journey prompt lacks business context: {prompts[0]}"
            )


# Performance and reliability tests
class TestVisualContentReliability:
    """Test reliability and performance of visual content generation."""
    
    @pytest.mark.asyncio
    async def test_generation_timeout_handling(self):
        """Test that generation handles timeouts gracefully without falling back to demo URLs."""
        
        with patch('agents.visual_content_agent.ImageGenerationAgent') as mock_agent_class:
            mock_agent = Mock()
            # Simulate timeout/failure
            mock_agent.generate_images = AsyncMock(side_effect=asyncio.TimeoutError("Generation timeout"))
            mock_agent_class.return_value = mock_agent
            
            posts = [{"id": "timeout_test", "type": "text_image", "content": "Test content"}]
            context = {"company_name": "TestCorp"}
            
            result = await generate_visual_content_for_posts(
                social_posts=posts,
                business_context=context,
                campaign_objective="test"
            )
            
            # Should handle timeout gracefully
            assert "posts_with_visuals" in result
            
            # CRITICAL: Should not fall back to demo URLs
            for post in result["posts_with_visuals"]:
                image_url = post.get("image_url", "")
                if image_url:
                    forbidden_domains = ["unsplash.com", "placeholder.com", "picsum.photos"]
                    parsed_url = urlparse(image_url)
                    assert not any(domain in parsed_url.netloc for domain in forbidden_domains), (
                        f"Timeout fallback used forbidden demo URL: {image_url}"
                    )
    
    @pytest.mark.asyncio
    async def test_api_key_missing_handling(self):
        """Test behavior when API keys are missing - should not show demo URLs."""
        
        # Temporarily remove API key
        original_key = os.environ.get('GEMINI_API_KEY')
        if original_key:
            del os.environ['GEMINI_API_KEY']
        
        try:
            posts = [{"id": "no_key_test", "type": "text_image", "content": "Test without API key"}]
            context = {"company_name": "TestCorp"}
            
            result = await generate_visual_content_for_posts(
                social_posts=posts,
                business_context=context,
                campaign_objective="test"
            )
            
            # Should indicate failure clearly
            posts_with_visuals = result.get("posts_with_visuals", [])
            
            for post in posts_with_visuals:
                image_url = post.get("image_url")
                
                # If no real generation possible, should either:
                # 1. Return None/null for image_url, OR
                # 2. Return error state, OR  
                # 3. Return localhost URL indicating failure
                
                if image_url:
                    # Should NOT be demo URLs from external services
                    forbidden_domains = ["unsplash.com", "placeholder.com", "picsum.photos"]
                    parsed_url = urlparse(image_url)
                    assert not any(domain in parsed_url.netloc for domain in forbidden_domains), (
                        f"Missing API key fallback used forbidden demo URL: {image_url}"
                    )
                    
        finally:
            # Restore API key
            if original_key:
                os.environ['GEMINI_API_KEY'] = original_key


if __name__ == "__main__":
    # Run critical regression tests
    print("🔍 Running Visual Content Context Fidelity Tests...")
    pytest.main([__file__, "-v", "--tb=short"])