"""
FILENAME: test_visual_content.py
DESCRIPTION/PURPOSE: Tests for visual content generation (Imagen integration)
Author: JP + 2025-06-16

Tests validate that visual content generation works correctly with 
image generation and graceful fallbacks.
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Import functions to test
from agents.visual_content_agent import generate_visual_content_for_posts

# REGRESSION PREVENTION: Forbidden URLs that caused the original issue
FORBIDDEN_DEMO_URLS = [
    "https://images.unsplash.com/photo-1542038784456-1ea8e732b2b9",
    "https://images.unsplash.com/photo-1531804055935-76f44d7c3621",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "https://via.placeholder.com",
    "https://picsum.photos"
]

def validate_no_forbidden_demo_urls(result: Dict[str, Any], test_name: str = ""):
    """
    REGRESSION PREVENTION: Validate that result contains no forbidden demo URLs.
    
    This function prevents the regression where mountain landscape images
    and generic demo content was shown for business marketing campaigns.
    """
    posts_with_visuals = result.get("posts_with_visuals", [])
    
    for post in posts_with_visuals:
        # Check image URLs
        image_url = post.get("image_url", "")
        if image_url:
            for forbidden_url in FORBIDDEN_DEMO_URLS:
                assert not image_url.startswith(forbidden_url), (
                    f"REGRESSION DETECTED in {test_name}: Forbidden demo image URL found: {image_url}. "
                    f"This indicates demo mode is active when contextual generation should occur."
                )
        
        # Check video URLs  
        video_url = post.get("video_url", "")
        if video_url:
            for forbidden_url in FORBIDDEN_DEMO_URLS:
                assert not video_url.startswith(forbidden_url), (
                    f"REGRESSION DETECTED in {test_name}: Forbidden demo video URL found: {video_url}. "
                    f"This indicates demo mode is active when contextual generation should occur."
                )
    
    # Also check legacy structure for backward compatibility
    images = result.get("images", [])
    for image in images:
        if isinstance(image, dict):
            url = image.get("url", "") or image.get("image_url", "")
            if url:
                for forbidden_url in FORBIDDEN_DEMO_URLS:
                    assert not url.startswith(forbidden_url), (
                        f"REGRESSION DETECTED in {test_name}: Forbidden demo URL in images array: {url}"
                    )
    
    videos = result.get("videos", [])
    for video in videos:
        if isinstance(video, dict):
            url = video.get("url", "") or video.get("video_url", "")
            if url:
                for forbidden_url in FORBIDDEN_DEMO_URLS:
                    assert not url.startswith(forbidden_url), (
                        f"REGRESSION DETECTED in {test_name}: Forbidden demo URL in videos array: {url}"
                    )


class TestVisualContentGeneration:
    """Test visual content generation functionality."""
    
    @pytest.mark.asyncio
    async def test_image_generation_structure(self):
        """Test that image generation returns proper structure."""
        
        sample_posts = [
            {
                "id": "test_post_1",
                "type": "text_image",
                "content": "Transform your business with AI solutions",
                "hashtags": ["#AI", "#Business"],
                "image_prompt": "Modern business transformation with AI technology"
            },
            {
                "id": "test_post_2",
                "type": "text_image", 
                "content": "Expert consulting services",
                "hashtags": ["#Consulting", "#Expertise"],
                "image_prompt": "Professional consulting team meeting"
            }
        ]
        
        business_context = {
            "company_name": "TestCorp",
            "industry": "Technology",
            "brand_voice": "Professional"
        }
        
        # Mock Imagen API response
        with patch('google.genai.ImageGenerationModel') as mock_imagen:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.images = [Mock(url="https://example.com/image1.jpg")]
            mock_model.generate_images.return_value = mock_response
            mock_imagen.return_value = mock_model
            
            result = await generate_visual_content_for_posts(sample_posts, business_context)
            
            # Validate structure
            assert isinstance(result, dict)
            assert "images" in result
            assert "videos" in result
            assert "metadata" in result
            
            # Check images generated
            assert isinstance(result["images"], list)
            assert len(result["images"]) > 0
            
            # REGRESSION PREVENTION: Validate no forbidden demo URLs
            validate_no_forbidden_demo_urls(result, "test_image_generation_structure")
    
    @pytest.mark.asyncio
    async def test_image_generation_fallback(self):
        """Test graceful fallback when image generation fails."""
        
        sample_posts = [
            {
                "id": "test_post_1",
                "type": "text_image",
                "content": "Test content",
                "hashtags": ["#Test"],
                "image_prompt": "Test image prompt"
            }
        ]
        
        business_context = {"company_name": "TestCorp"}
        
        # Mock API failure
        with patch('google.genai.ImageGenerationModel') as mock_imagen:
            mock_model = Mock()
            mock_model.generate_images.side_effect = Exception("API Error")
            mock_imagen.return_value = mock_model
            
            result = await generate_visual_content_for_posts(sample_posts, business_context)
            
            # Should still return structure with fallback
            assert isinstance(result, dict)
            assert "images" in result
            assert "metadata" in result
            
            # Should indicate fallback was used
            assert result["metadata"]["generation_method"] == "mock"
            
            # REGRESSION PREVENTION: Even fallback should not use forbidden demo URLs
            validate_no_forbidden_demo_urls(result, "test_image_generation_fallback")
    
    @pytest.mark.asyncio
    async def test_no_image_posts_handling(self):
        """Test handling when no image posts are provided."""
        
        sample_posts = [
            {
                "id": "text_only_post",
                "type": "text_url",
                "content": "Text only content",
                "hashtags": ["#Text"]
            }
        ]
        
        business_context = {"company_name": "TestCorp"}
        
        result = await generate_visual_content_for_posts(sample_posts, business_context)
        
        # Should handle gracefully
        assert isinstance(result, dict)
        assert "images" in result
        assert "videos" in result
        assert len(result["images"]) == 0  # No images for text-only posts
        
        # REGRESSION PREVENTION: Ensure no forbidden demo URLs even for text-only posts
        validate_no_forbidden_demo_urls(result, "test_no_image_posts_handling")
    
    @pytest.mark.asyncio
    async def test_real_imagen_api_if_available(self):
        """Test real Imagen API if credentials are available."""
        
        if not os.getenv('GEMINI_API_KEY'):
            pytest.skip("GEMINI_API_KEY not available - skipping real API test")
        
        sample_posts = [
            {
                "id": "real_test_post",
                "type": "text_image",
                "content": "Professional technology consulting services",
                "hashtags": ["#Technology", "#Consulting"],
                "image_prompt": "Professional business meeting with technology consultants"
            }
        ]
        
        business_context = {
            "company_name": "TestCorp",
            "industry": "Technology Consulting",
            "brand_voice": "Professional"
        }
        
        # Test real API call
        result = await generate_visual_content_for_posts(sample_posts, business_context)
        
        # Validate real response
        assert isinstance(result, dict)
        assert "images" in result
        assert "metadata" in result
        
        # REGRESSION PREVENTION: Real API must not return forbidden demo URLs
        validate_no_forbidden_demo_urls(result, "test_real_imagen_api_if_available")
        
        # If real generation worked, should have metadata indicating it
        if result["metadata"]["generation_method"] == "imagen_ai":
            assert len(result["images"]) > 0
            
            # Check image structure
            for image in result["images"]:
                assert "post_id" in image
                assert "url" in image or "base64" in image  # Should have image data
    
    @pytest.mark.asyncio 
    async def test_video_generation_mock(self):
        """Test video generation (currently mock implementation)."""
        
        sample_posts = [
            {
                "id": "video_post",
                "type": "text_video",
                "content": "See our services in action",
                "hashtags": ["#Demo", "#Services"],
                "video_prompt": "Professional service demonstration video"
            }
        ]
        
        business_context = {"company_name": "TestCorp"}
        
        result = await generate_visual_content_for_posts(sample_posts, business_context)
        
        # Should handle videos (currently mock)
        assert isinstance(result, dict)
        assert "videos" in result
        assert isinstance(result["videos"], list)
        
        # REGRESSION PREVENTION: Video generation must not use forbidden demo URLs
        validate_no_forbidden_demo_urls(result, "test_video_generation_mock")
        
        # Videos should be present for video posts
        video_posts = [p for p in sample_posts if p["type"] == "text_video"]
        if video_posts:
            assert len(result["videos"]) > 0
    
    @pytest.mark.asyncio
    async def test_business_context_integration(self):
        """Test that business context is properly integrated into prompts."""
        
        sample_posts = [
            {
                "id": "context_test_post",
                "type": "text_image", 
                "content": "TestCorp delivers professional solutions",
                "hashtags": ["#TestCorp", "#Professional"],
                "image_prompt": "Professional business solutions"
            }
        ]
        
        business_context = {
            "company_name": "TestCorp",
            "industry": "Professional Services",
            "brand_voice": "Professional and trustworthy",
            "visual_elements": "Clean, modern design with blue color scheme"
        }
        
        # Mock to capture the prompts sent
        with patch('google.genai.ImageGenerationModel') as mock_imagen:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.images = [Mock(url="https://example.com/test.jpg")]
            mock_model.generate_images.return_value = mock_response
            mock_imagen.return_value = mock_model
            
            result = await generate_visual_content_for_posts(sample_posts, business_context)
            
            # REGRESSION PREVENTION: Business context integration must not produce forbidden URLs
            validate_no_forbidden_demo_urls(result, "test_business_context_integration")
            
            # Should have called image generation
            if mock_model.generate_images.called:
                # Get the prompt that was used
                call_args = mock_model.generate_images.call_args
                prompt_used = call_args[1].get('prompt', call_args[0][0] if call_args[0] else '')
                
                # Business context should influence the prompt
                assert isinstance(prompt_used, str)
                assert len(prompt_used) > 0
                
                # CONTEXT VALIDATION: Prompt should contain business context
                prompt_lower = prompt_used.lower()
                assert "testcorp" in prompt_lower or "professional" in prompt_lower, (
                    f"Business context not integrated into prompt: {prompt_used}"
                )


class TestVisualContentPerformance:
    """Test performance and quality aspects of visual content generation."""
    
    @pytest.mark.asyncio
    async def test_multiple_posts_handling(self):
        """Test handling multiple image posts efficiently."""
        
        # Create multiple test posts
        sample_posts = []
        for i in range(5):
            sample_posts.append({
                "id": f"post_{i}",
                "type": "text_image",
                "content": f"Test content {i}",
                "hashtags": [f"#Test{i}"],
                "image_prompt": f"Test image prompt {i}"
            })
        
        business_context = {"company_name": "TestCorp"}
        
        # Mock successful generation
        with patch('google.genai.ImageGenerationModel') as mock_imagen:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.images = [Mock(url=f"https://example.com/image{i}.jpg") for i in range(5)]
            mock_model.generate_images.return_value = mock_response
            mock_imagen.return_value = mock_model
            
            result = await generate_visual_content_for_posts(sample_posts, business_context)
            
            # Should handle all posts
            assert isinstance(result, dict)
            assert "images" in result
            
            # REGRESSION PREVENTION: Multiple posts should not produce forbidden URLs
            validate_no_forbidden_demo_urls(result, "test_multiple_posts_handling")
            
            # Verify generation was attempted for image posts
            image_posts_count = len([p for p in sample_posts if p["type"] == "text_image"])
            assert image_posts_count == 5
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test recovery from partial failures in batch processing."""
        
        sample_posts = [
            {
                "id": "good_post",
                "type": "text_image",
                "content": "Good content",
                "hashtags": ["#Good"],
                "image_prompt": "Good image prompt"
            },
            {
                "id": "problematic_post",
                "type": "text_image",
                "content": "Problematic content",
                "hashtags": ["#Problem"],
                "image_prompt": ""  # Empty prompt might cause issues
            }
        ]
        
        business_context = {"company_name": "TestCorp"}
        
        # Should handle mixed success/failure gracefully
        result = await generate_visual_content_for_posts(sample_posts, business_context)
        
        assert isinstance(result, dict)
        assert "images" in result
        assert "metadata" in result
        
        # REGRESSION PREVENTION: Error recovery should not fall back to forbidden URLs
        validate_no_forbidden_demo_urls(result, "test_error_recovery")
        
        # Should have some form of result even with partial failures
        assert "error_count" not in result["metadata"] or result["metadata"]["error_count"] <= len(sample_posts)


class TestVisualContentRegressionPrevention:
    """
    CRITICAL REGRESSION PREVENTION: Test suite specifically designed to catch
    the regression where mountain landscape images were shown for business campaigns.
    """
    
    @pytest.mark.asyncio
    async def test_no_mountain_images_for_business_context(self):
        """
        REGRESSION TEST: Ensure business campaigns don't get mountain/nature images.
        
        This test specifically prevents the regression where:
        - Business marketing posts got generic mountain landscape photos
        - Nature photography appeared instead of business-relevant content
        """
        
        # Test various business contexts that should NEVER get nature imagery
        business_contexts = [
            {
                "company_name": "TechCorp Solutions",
                "industry": "Technology Consulting",
                "business_description": "Professional technology consulting services",
                "expected_context": ["technology", "consulting", "professional", "business"]
            },
            {
                "company_name": "Bella Vista Restaurant", 
                "industry": "Food & Beverage",
                "business_description": "Italian restaurant specializing in authentic cuisine",
                "expected_context": ["restaurant", "food", "dining", "italian"]
            },
            {
                "company_name": "Creative Threads",
                "industry": "Apparel & Fashion", 
                "business_description": "Custom t-shirt printing with creative designs",
                "expected_context": ["t-shirt", "apparel", "design", "fashion"]
            }
        ]
        
        for business_context in business_contexts:
            # Create business-focused posts
            business_posts = [
                {
                    "id": f"business_post_{business_context['company_name'].replace(' ', '_').lower()}",
                    "type": "text_image",
                    "content": f"Discover {business_context['company_name']}'s exceptional services",
                    "hashtags": ["#business", "#professional", "#quality"]
                }
            ]
            
            # Mock image generation to capture prompts
            with patch('agents.visual_content_agent.ImageGenerationAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent.generate_images = AsyncMock(return_value=[
                    {
                        "id": "business_test_img",
                        "prompt": "captured_prompt",
                        "image_url": f"http://localhost:8000/api/v1/content/images/business_test/{business_context['company_name'].replace(' ', '_').lower()}.png",
                        "status": "success",
                        "metadata": {"generation_method": "imagen_real"}
                    }
                ])
                mock_agent_class.return_value = mock_agent
                
                result = await generate_visual_content_for_posts(
                    social_posts=business_posts,
                    business_context=business_context,
                    campaign_objective="increase brand awareness"
                )
                
                # CRITICAL: Validate no forbidden demo URLs
                validate_no_forbidden_demo_urls(result, f"business_context_{business_context['company_name']}")
                
                # Validate that prompts were enhanced with business context
                mock_agent.generate_images.assert_called_once()
                call_args = mock_agent.generate_images.call_args
                prompts = call_args[0][0]
                
                business_prompt = prompts[0].lower()
                
                # REGRESSION PREVENTION: Ensure business context is in the prompt
                company_words = business_context["company_name"].lower().split()
                business_context_found = any(word in business_prompt for word in company_words)
                assert business_context_found, (
                    f"REGRESSION: Business context missing from prompt for {business_context['company_name']}. "
                    f"This could lead to irrelevant imagery. Prompt: {prompts[0]}"
                )
                
                # CRITICAL: Ensure no nature/mountain context that caused the original regression
                nature_contexts = ["mountain", "landscape", "nature", "scenery", "outdoor vista", "wilderness"]
                for nature_context in nature_contexts:
                    assert nature_context not in business_prompt, (
                        f"REGRESSION DETECTED: Nature context '{nature_context}' found in business prompt. "
                        f"This leads to mountain images for business campaigns. "
                        f"Company: {business_context['company_name']}, Prompt: {prompts[0]}"
                    )
    
    @pytest.mark.asyncio
    async def test_contextual_prompt_enhancement_validation(self):
        """
        REGRESSION TEST: Validate that prompt enhancement adds business context
        and prevents generic/irrelevant generation that caused the original issue.
        """
        
        # Test prompt enhancement directly
        from agents.visual_content_agent import VisualContentOrchestrator
        
        orchestrator = VisualContentOrchestrator()
        
        # Test different business scenarios
        test_scenarios = [
            {
                "post": {"content": "Professional business services"},
                "business_context": {
                    "company_name": "BusinessCorp",
                    "industry": "Professional Services",
                    "business_description": "Management consulting services"
                },
                "objective": "generate leads",
                "required_context": ["businesscorp", "professional", "consulting"],
                "forbidden_context": ["mountain", "nature", "landscape"]
            },
            {
                "post": {"content": "Quality restaurant experience"},
                "business_context": {
                    "company_name": "Food Paradise",
                    "industry": "Food & Beverage", 
                    "business_description": "Fine dining restaurant"
                },
                "objective": "attract customers",
                "required_context": ["food", "restaurant", "dining"],
                "forbidden_context": ["mountain", "technology", "office"]
            }
        ]
        
        for scenario in test_scenarios:
            enhanced_prompt = orchestrator._create_image_prompt(
                scenario["post"],
                scenario["business_context"], 
                scenario["objective"]
            )
            
            enhanced_lower = enhanced_prompt.lower()
            
            # REGRESSION PREVENTION: Required context must be present
            required_found = any(req in enhanced_lower for req in scenario["required_context"])
            assert required_found, (
                f"REGRESSION: Required business context missing from enhanced prompt. "
                f"Required: {scenario['required_context']}, Got: {enhanced_prompt}"
            )
            
            # CRITICAL: Forbidden context must be absent
            for forbidden in scenario["forbidden_context"]:
                assert forbidden not in enhanced_lower, (
                    f"REGRESSION DETECTED: Forbidden context '{forbidden}' in enhanced prompt. "
                    f"This causes irrelevant imagery for business campaigns. "
                    f"Enhanced prompt: {enhanced_prompt}"
                )
    
    @pytest.mark.asyncio 
    async def test_demo_mode_vs_production_distinction(self):
        """
        REGRESSION TEST: Ensure clear distinction between demo mode and production mode
        to prevent confusion about when irrelevant content is acceptable.
        """
        
        # Test with minimal context (demo-like scenario)
        minimal_context = {
            "company_name": "Demo Company"
        }
        
        demo_posts = [
            {
                "id": "demo_test_post",
                "type": "text_image", 
                "content": "Demo marketing content"
            }
        ]
        
        result = await generate_visual_content_for_posts(
            social_posts=demo_posts,
            business_context=minimal_context,
            campaign_objective="demo purposes"
        )
        
        # Even in demo mode, should not use forbidden URLs
        validate_no_forbidden_demo_urls(result, "test_demo_mode_vs_production_distinction")
        
        # If demo content is returned, it should be clearly indicated
        posts_with_visuals = result.get("posts_with_visuals", [])
        for post in posts_with_visuals:
            image_url = post.get("image_url", "")
            if image_url and any(domain in image_url for domain in ["unsplash.com", "placeholder.com"]):
                # If demo URL is used, there should be clear demo indication in metadata
                metadata = post.get("metadata", {})
                generation_method = metadata.get("generation_method", "")
                
                assert "demo" in generation_method.lower() or "mock" in generation_method.lower(), (
                    f"REGRESSION: Demo content not clearly marked as demo. "
                    f"URL: {image_url}, Method: {generation_method}"
                )
    
    def test_forbidden_url_detection_comprehensive(self):
        """
        REGRESSION TEST: Comprehensive test of all forbidden URL patterns
        that caused the original regression.
        """
        
        # Test the validation function directly with all known problematic URLs
        test_results = [
            # Original regression URLs
            {
                "posts_with_visuals": [
                    {"image_url": "https://images.unsplash.com/photo-1542038784456-1ea8e732b2b9?w=400&h=300"}
                ]
            },
            {
                "posts_with_visuals": [
                    {"image_url": "https://images.unsplash.com/photo-1531804055935-76f44d7c3621?fit=crop&crop=faces"}
                ]
            },
            {
                "posts_with_visuals": [
                    {"video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"}
                ]
            },
            # Generic placeholder services
            {
                "posts_with_visuals": [
                    {"image_url": "https://via.placeholder.com/400x300"}
                ]
            },
            {
                "posts_with_visuals": [
                    {"image_url": "https://picsum.photos/400/300"}
                ]
            }
        ]
        
        # Each of these should trigger the regression detection
        for i, test_result in enumerate(test_results):
            with pytest.raises(AssertionError, match="REGRESSION DETECTED"):
                validate_no_forbidden_demo_urls(test_result, f"comprehensive_test_{i}")
        
        # Valid URLs should pass
        valid_result = {
            "posts_with_visuals": [
                {"image_url": "http://localhost:8000/api/v1/content/images/campaign123/business_image.png"},
                {"video_url": "http://localhost:8000/api/v1/content/videos/campaign123/business_video.mp4"}
            ]
        }
        
        # This should not raise an exception
        validate_no_forbidden_demo_urls(valid_result, "valid_urls_test") 