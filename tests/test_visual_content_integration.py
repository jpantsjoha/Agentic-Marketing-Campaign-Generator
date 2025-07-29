"""
FILENAME: test_visual_content_integration.py
DESCRIPTION/PURPOSE: Integration tests for end-to-end visual content generation workflow
Author: JP + 2025-07-23

These integration tests validate the complete workflow from campaign creation
through visual content generation, ensuring context fidelity is maintained
throughout the entire user journey.

Tests the integration between:
- Campaign creation (frontend)
- Business context analysis (backend)
- Visual content generation (AI agents)
- Content delivery (API endpoints)
- User interface display (frontend)
"""

import pytest
import asyncio
import json
import time
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock
import requests
from pathlib import Path
import tempfile

# Test both API and agent integration
from backend.api.routes.content import generate_visual_content
from backend.api.routes.campaigns import create_campaign
from agents.marketing_orchestrator import execute_campaign_workflow
from agents.visual_content_agent import generate_visual_content_for_posts


class TestVisualContentEndToEndIntegration:
    """Test complete workflow from campaign creation to visual display."""
    
    # Test data representing different business types
    TEST_BUSINESSES = {
        "restaurant": {
            "name": "Bella Vista Italian Restaurant",
            "industry": "Food & Beverage", 
            "description": "Authentic Italian cuisine in an upscale dining environment",
            "website": "https://bellavista-restaurant.com",
            "expected_visual_context": ["restaurant", "dining", "italian", "food", "cuisine"]
        },
        "consulting": {
            "name": "TechCorp Solutions",
            "industry": "Technology Consulting",
            "description": "Professional technology consulting services for enterprise clients",
            "website": "https://techcorp-solutions.com", 
            "expected_visual_context": ["technology", "consulting", "professional", "business", "office"]
        },
        "tshirt": {
            "name": "Creative Threads",
            "industry": "Apparel & Fashion",
            "description": "Custom t-shirt printing with creative graphic designs",
            "website": "https://creative-threads.com",
            "product_context": {
                "has_specific_product": True,
                "product_name": "Joker T-Shirt",
                "product_themes": ["humor", "pop culture", "graphic design"]
            },
            "expected_visual_context": ["t-shirt", "joker", "apparel", "design", "creative"]
        }
    }
    
    @pytest.mark.asyncio
    async def test_complete_campaign_to_visual_workflow(self):
        """Test the complete workflow from campaign creation to visual generation."""
        
        for business_type, business_data in self.TEST_BUSINESSES.items():
            print(f"\n🔄 Testing complete workflow for {business_type} business...")
            
            # Step 1: Campaign Creation (simulating frontend API call)
            campaign_request = {
                "name": f"{business_data['name']} Marketing Campaign",
                "objective": "increase brand awareness and customer engagement",
                "business_context": {
                    "company_name": business_data["name"],
                    "industry": business_data["industry"], 
                    "business_description": business_data["description"],
                    "business_website": business_data["website"],
                    "product_context": business_data.get("product_context", {})
                },
                "campaign_type": "awareness",
                "creativity_level": 7,
                "post_count": 3
            }
            
            # Step 2: Execute Campaign Workflow (backend orchestration)
            with patch('agents.marketing_orchestrator.execute_campaign_workflow') as mock_workflow:
                # Mock the campaign workflow to return structured data
                mock_campaign_result = {
                    "generated_content": [
                        {
                            "id": f"{business_type}_post_1",
                            "type": "text_image",
                            "content": f"Discover {business_data['name']}'s exceptional services",
                            "hashtags": [f"#{business_type}", "#quality", "#professional"]
                        },
                        {
                            "id": f"{business_type}_post_2", 
                            "type": "text_video",
                            "content": f"See why customers choose {business_data['name']}",
                            "hashtags": [f"#{business_type}", "#customers", "#success"]
                        }
                    ],
                    "business_analysis": {
                        "company_name": business_data["name"],
                        "industry": business_data["industry"],
                        "campaign_guidance": {
                            "visual_style": {
                                "photography_style": f"professional {business_type} photography",
                                "mood": "trustworthy and professional"
                            }
                        }
                    }
                }
                mock_workflow.return_value = mock_campaign_result
                
                # Step 3: Visual Content Generation Request
                visual_request = {
                    "social_posts": mock_campaign_result["generated_content"],
                    "business_context": {
                        **campaign_request["business_context"],
                        "campaign_guidance": mock_campaign_result["business_analysis"]["campaign_guidance"]
                    },
                    "campaign_objective": campaign_request["objective"],
                    "campaign_id": f"test_campaign_{business_type}"
                }
                
                # Step 4: Test Visual Generation with Context Validation
                with patch('agents.visual_content_agent.ImageGenerationAgent') as mock_img_agent, \
                     patch('agents.visual_content_agent.VideoGenerationAgent') as mock_vid_agent:
                    
                    # Mock image generation with contextually relevant responses
                    mock_img_instance = Mock()
                    mock_img_instance.generate_images = AsyncMock(return_value=[
                        {
                            "id": f"{business_type}_img_1",
                            "prompt": f"Professional {business_type} image for {business_data['name']}",
                            "image_url": f"http://localhost:8000/api/v1/content/images/{business_type}_campaign/image_1.png",
                            "status": "success",
                            "metadata": {"generation_method": "imagen_real"}
                        }
                    ])
                    mock_img_agent.return_value = mock_img_instance
                    
                    # Mock video generation with contextually relevant responses  
                    mock_vid_instance = Mock()
                    mock_vid_instance.generate_videos = AsyncMock(return_value=[
                        {
                            "id": f"{business_type}_vid_1",
                            "prompt": f"Professional {business_type} video for {business_data['name']}",
                            "video_url": f"http://localhost:8000/api/v1/content/videos/{business_type}_campaign/video_1.mp4",
                            "status": "success", 
                            "metadata": {"generation_method": "veo_real"}
                        }
                    ])
                    mock_vid_agent.return_value = mock_vid_instance
                    
                    # Execute visual generation
                    visual_result = await generate_visual_content_for_posts(
                        social_posts=visual_request["social_posts"],
                        business_context=visual_request["business_context"],
                        campaign_objective=visual_request["campaign_objective"],
                        campaign_id=visual_request["campaign_id"]
                    )
                    
                    # Step 5: Validate Integration Results
                    assert "posts_with_visuals" in visual_result
                    posts_with_visuals = visual_result["posts_with_visuals"]
                    
                    # Validate that generation was called with enhanced prompts
                    mock_img_instance.generate_images.assert_called_once()
                    mock_vid_instance.generate_videos.assert_called_once()
                    
                    # Get the prompts that were generated
                    img_call_args = mock_img_instance.generate_images.call_args
                    vid_call_args = mock_vid_instance.generate_videos.call_args
                    
                    img_prompts = img_call_args[0][0]
                    vid_prompts = vid_call_args[0][0]
                    
                    # CRITICAL: Validate context integration in prompts
                    for prompt in img_prompts + vid_prompts:
                        prompt_lower = prompt.lower()
                        
                        # Must contain business-specific context
                        business_name = business_data["name"].lower()
                        assert any(word in prompt_lower for word in business_name.split()), (
                            f"Prompt missing business name context: {prompt}"
                        )
                        
                        # Must contain expected visual context for business type
                        expected_contexts = business_data["expected_visual_context"]
                        context_found = any(context in prompt_lower for context in expected_contexts)
                        assert context_found, (
                            f"INTEGRATION FAILURE: Prompt for {business_type} business lacks expected context. "
                            f"Expected one of {expected_contexts}, got: {prompt}"
                        )
                        
                        # Must NOT contain irrelevant context that caused regression
                        irrelevant_contexts = ["mountain", "landscape", "nature", "scenery"]
                        for irrelevant in irrelevant_contexts:
                            assert irrelevant not in prompt_lower, (
                                f"REGRESSION DETECTED: Prompt contains irrelevant context '{irrelevant}': {prompt}"
                            )
                    
                    # Validate response structure
                    assert len(posts_with_visuals) == len(visual_request["social_posts"])
                    
                    for post in posts_with_visuals:
                        post_type = post.get("type", "")
                        
                        if post_type == "text_image":
                            image_url = post.get("image_url")
                            assert image_url is not None, f"Missing image_url for {post['id']}"
                            assert image_url.startswith("http://localhost:8000/api/v1/content/images/"), (
                                f"Invalid image URL format: {image_url}"
                            )
                            
                        elif post_type == "text_video":
                            video_url = post.get("video_url")
                            assert video_url is not None, f"Missing video_url for {post['id']}"
                            assert video_url.startswith("http://localhost:8000/api/v1/content/videos/"), (
                                f"Invalid video URL format: {video_url}"
                            )
            
            print(f"✅ Complete workflow test passed for {business_type} business")
    
    @pytest.mark.asyncio
    async def test_api_endpoint_integration(self):
        """Test API endpoint integration with context validation."""
        
        # Test the actual API endpoint that the frontend calls
        for business_type, business_data in self.TEST_BUSINESSES.items():
            print(f"\n🔌 Testing API endpoint integration for {business_type}...")
            
            api_request = {
                "social_posts": [
                    {
                        "id": f"api_test_{business_type}",
                        "type": "text_image",
                        "content": f"Experience {business_data['name']}'s quality service"
                    }
                ],
                "business_context": {
                    "company_name": business_data["name"],
                    "industry": business_data["industry"],
                    "business_description": business_data["description"],
                    "product_context": business_data.get("product_context", {})
                },
                "campaign_objective": "increase engagement"
            }
            
            # Mock the underlying generation to focus on integration
            with patch('backend.api.routes.content.generate_visual_content_for_posts') as mock_gen:
                mock_gen.return_value = {
                    "posts_with_visuals": [
                        {
                            "id": f"api_test_{business_type}",
                            "type": "text_image",
                            "content": f"Experience {business_data['name']}'s quality service",
                            "image_url": f"http://localhost:8000/api/v1/content/images/{business_type}/generated.png",
                            "image_metadata": {
                                "generation_method": "imagen_real",
                                "context_fidelity": "validated"
                            }
                        }
                    ],
                    "generation_metadata": {
                        "agent_used": "VisualContentOrchestrator",
                        "context_applied": True
                    }
                }
                
                # Call the API endpoint
                result = await generate_visual_content(api_request)
                
                # Validate API response structure
                assert "posts_with_visuals" in result
                assert "generation_metadata" in result or "processing_time" in result
                
                # Validate that generation function was called with proper context
                mock_gen.assert_called_once()
                call_args = mock_gen.call_args
                
                # Verify business context was passed through
                passed_context = call_args.kwargs.get("business_context") or call_args[1]
                assert passed_context["company_name"] == business_data["name"]
                assert passed_context["industry"] == business_data["industry"]
                
            print(f"✅ API endpoint integration test passed for {business_type}")
    
    @pytest.mark.asyncio  
    async def test_error_handling_integration(self):
        """Test error handling throughout the integration workflow."""
        
        print("\n⚡ Testing error handling integration...")
        
        # Test scenario: API generation fails
        error_request = {
            "social_posts": [
                {
                    "id": "error_test_post",
                    "type": "text_image",
                    "content": "Test content for error handling"
                }
            ],
            "business_context": {
                "company_name": "ErrorTest Corp",
                "industry": "Testing"
            },
            "campaign_objective": "test error handling"
        }
        
        # Mock generation failure
        with patch('agents.visual_content_agent.ImageGenerationAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.generate_images = AsyncMock(side_effect=Exception("API temporarily unavailable"))
            mock_agent.return_value = mock_instance
            
            # Execute with error
            result = await generate_visual_content_for_posts(
                social_posts=error_request["social_posts"],
                business_context=error_request["business_context"],
                campaign_objective=error_request["campaign_objective"]
            )
            
            # Validate error handling
            assert "posts_with_visuals" in result
            posts = result["posts_with_visuals"]
            
            for post in posts:
                # Should indicate error state, not return forbidden demo URLs
                image_url = post.get("image_url")
                status = post.get("status", "unknown")
                
                if image_url:
                    # If URL is provided, must not be forbidden demo URL
                    forbidden_domains = ["unsplash.com", "placeholder.com", "picsum.photos"]
                    for domain in forbidden_domains:
                        assert domain not in image_url, (
                            f"Error handling returned forbidden demo URL: {image_url}"
                        )
                else:
                    # If no URL, should indicate error appropriately
                    assert status in ["error", "failed"] or "error" in post.get("metadata", {}), (
                        f"Error state not properly indicated: {post}"
                    )
        
        print("✅ Error handling integration test passed")
    
    def test_context_enhancement_pipeline(self):
        """Test the complete context enhancement pipeline."""
        
        print("\n🔧 Testing context enhancement pipeline...")
        
        # Test different business contexts
        test_cases = [
            {
                "business_type": "restaurant",
                "base_prompt": "Professional marketing image",
                "business_context": {
                    "company_name": "Mario's Pizza",
                    "industry": "Food & Beverage",
                    "business_description": "Authentic Italian pizza restaurant"
                },
                "expected_enhancements": ["mario's pizza", "restaurant", "food", "italian"]
            },
            {
                "business_type": "tech_consulting", 
                "base_prompt": "Business service image",
                "business_context": {
                    "company_name": "DataCorp Analytics", 
                    "industry": "Technology Consulting",
                    "business_description": "Data analytics consulting for enterprises"
                },
                "expected_enhancements": ["datacorp", "technology", "consulting", "analytics"]
            }
        ]
        
        for test_case in test_cases:
            # Import the context enhancement function
            from agents.visual_content_agent import VisualContentOrchestrator
            orchestrator = VisualContentOrchestrator()
            
            # Test prompt enhancement
            enhanced_prompt = orchestrator._create_image_prompt(
                {"content": test_case["base_prompt"]},
                test_case["business_context"],
                "increase engagement"
            )
            
            enhanced_lower = enhanced_prompt.lower()
            
            # Validate expected enhancements are present
            for expected in test_case["expected_enhancements"]:
                assert expected in enhanced_lower, (
                    f"Context enhancement missing '{expected}' for {test_case['business_type']}. "
                    f"Enhanced prompt: {enhanced_prompt}"
                )
            
            # Validate prohibited contexts are absent
            prohibited = ["mountain", "landscape", "nature", "generic"]
            for forbidden in prohibited:
                assert forbidden not in enhanced_lower, (
                    f"Prohibited context '{forbidden}' found in enhanced prompt: {enhanced_prompt}"
                )
        
        print("✅ Context enhancement pipeline test passed")


class TestVisualContentAPIIntegration:
    """Test API-level integration for visual content generation."""
    
    @pytest.mark.asyncio
    async def test_generate_visuals_api_endpoint(self):
        """Test the /api/v1/content/generate-visuals endpoint integration."""
        
        print("\n🌐 Testing generate-visuals API endpoint...")
        
        # Prepare test request
        api_request = {
            "social_posts": [
                {
                    "id": "api_integration_test",
                    "type": "text_image",
                    "content": "Professional consulting services that deliver results"
                }
            ],
            "business_context": {
                "company_name": "IntegrationTest Consulting",
                "industry": "Professional Services",
                "business_description": "Management consulting for Fortune 500 companies"
            },
            "campaign_objective": "generate qualified leads"
        }
        
        # Test with successful generation mock
        with patch('backend.api.routes.content.generate_visual_content_for_posts') as mock_generation:
            mock_generation.return_value = {
                "posts_with_visuals": [
                    {
                        "id": "api_integration_test",
                        "type": "text_image",
                        "content": "Professional consulting services that deliver results",
                        "image_url": "http://localhost:8000/api/v1/content/images/integration_test/consulting.png",
                        "image_metadata": {
                            "generation_method": "imagen_real",
                            "context_validation": "passed"
                        }
                    }
                ],
                "generation_metadata": {
                    "processing_time": 3.2,
                    "context_fidelity": "maintained"
                }
            }
            
            # Import and call the API endpoint function
            from backend.api.routes.content import generate_visual_content
            
            result = await generate_visual_content(api_request)
            
            # Validate API response
            assert "posts_with_visuals" in result
            posts = result["posts_with_visuals"]
            
            assert len(posts) == 1
            test_post = posts[0]
            
            # Validate image URL format
            image_url = test_post["image_url"]
            assert image_url.startswith("http://localhost:8000/api/v1/content/images/")
            assert "consulting" in image_url  # Should reflect business context
            
            # Validate that business context was passed to generation
            mock_generation.assert_called_once()
            call_kwargs = mock_generation.call_args.kwargs
            
            passed_context = call_kwargs["business_context"]
            assert passed_context["company_name"] == "IntegrationTest Consulting"
            assert passed_context["industry"] == "Professional Services"
        
        print("✅ Generate-visuals API endpoint integration test passed")
    
    @pytest.mark.asyncio
    async def test_bulk_generation_integration(self):
        """Test bulk content generation with visual integration."""
        
        print("\n📦 Testing bulk generation integration...")
        
        # Test bulk generation request
        bulk_request = {
            "post_type": "text_image",
            "regenerate_count": 3,
            "business_context": {
                "company_name": "BulkTest Industries",
                "industry": "Manufacturing",
                "business_description": "Industrial equipment manufacturing"
            },
            "creativity_level": 7
        }
        
        # Mock the bulk generation endpoint
        with patch('backend.api.routes.content._generate_batch_content_with_gemini') as mock_bulk:
            mock_posts = []
            for i in range(3):
                mock_posts.append(Mock())
                mock_posts[i].id = f"bulk_post_{i+1}"
                mock_posts[i].type.value = "text_image"
                mock_posts[i].content = f"Industrial equipment solutions - post {i+1}"
                mock_posts[i].hashtags = ["#manufacturing", "#industrial", "#equipment"]
                mock_posts[i].platform_optimized = {}
                mock_posts[i].engagement_score = 8.0 + (i * 0.1)
                mock_posts[i].selected = False
            
            mock_bulk.return_value = mock_posts
            
            # Import and call bulk generation
            from backend.api.routes.content import generate_bulk_content
            
            result = await generate_bulk_content(bulk_request)
            
            # Validate bulk generation response
            assert "new_posts" in result
            new_posts = result["new_posts"]
            
            assert len(new_posts) == 3
            
            # Validate each post has proper structure for visual generation
            for i, post in enumerate(new_posts):
                assert post["id"] == f"bulk_post_{i+1}"
                assert post["type"] == "text_image"
                assert "industrial" in post["content"].lower() or "manufacturing" in post["content"].lower()
                assert "#manufacturing" in post["hashtags"]
                
                # Image URL should be None initially (generated separately)
                assert post["image_url"] is None
        
        print("✅ Bulk generation integration test passed")


class TestVisualContentCacheIntegration:
    """Test caching integration for visual content."""
    
    @pytest.mark.asyncio
    async def test_campaign_cache_integration(self):
        """Test campaign-specific caching integration."""
        
        print("\n💾 Testing campaign cache integration...")
        
        # Test with cache operations
        from agents.visual_content_agent import CampaignImageCache
        
        cache = CampaignImageCache()
        test_campaign_id = "cache_integration_test"
        test_prompt = "Professional business consulting image for IntegrationTest Corp"
        test_model = "imagen-3.0"
        test_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        # Test cache miss initially
        cached_result = cache.get_cached_image(test_prompt, test_model, test_campaign_id)
        assert cached_result is None, "Cache should be empty initially"
        
        # Test cache storage
        cache_success = cache.cache_image(
            test_prompt, 
            test_model, 
            test_campaign_id, 
            test_image_data, 
            is_current=True
        )
        assert cache_success, "Cache storage should succeed"
        
        # Test cache retrieval
        cached_result = cache.get_cached_image(test_prompt, test_model, test_campaign_id)
        assert cached_result == test_image_data, "Cached image should match stored data"
        
        # Test cache stats
        stats = cache.get_cache_stats(test_campaign_id)
        assert stats["campaign_id"] == test_campaign_id
        assert stats["current_images"] >= 1
        assert stats["total_images"] >= 1
        
        # Test cache cleanup
        cleaned_count = cache.cleanup_old_images(test_campaign_id)
        assert isinstance(cleaned_count, int), "Cleanup should return count"
        
        print("✅ Campaign cache integration test passed")


if __name__ == "__main__":
    # Run integration tests
    print("🚀 Starting Visual Content Integration Tests...")
    pytest.main([__file__, "-v", "--tb=short", "-s"])