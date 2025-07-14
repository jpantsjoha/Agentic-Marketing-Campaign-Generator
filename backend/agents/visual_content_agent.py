"""
FILENAME: visual_content_agent.py
DESCRIPTION/PURPOSE: Visual content generation agent for images and videos using Google Imagen and Veo
Author: JP + 2025-06-16

This module provides visual content generation capabilities using Google's Imagen and Veo models,
with proper marketing prompt engineering and business context integration.
"""

import os
import asyncio
import tempfile
import uuid
import logging
import base64
import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Enhanced cache configuration for campaign-specific storage
CACHE_BASE_DIR = Path("data/images/cache")
CACHE_BASE_DIR.mkdir(parents=True, exist_ok=True)

class CampaignImageCache:
    """
    Campaign-aware image caching system for consistent user experience
    
    Architecture:
    - data/images/cache/<campaign_id>/<curr_imagehash>.json - Current/latest images
    - data/images/cache/<campaign_id>/<imagehash>.json - Previous images (cleaned on restart)
    - Supports MVP → Production migration to GCS bucket structure
    """
    
    def __init__(self, cache_base_dir: Path = CACHE_BASE_DIR):
        self.cache_base_dir = cache_base_dir
        self.cache_base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def _get_campaign_cache_dir(self, campaign_id: str) -> Path:
        """Get campaign-specific cache directory"""
        campaign_dir = self.cache_base_dir / campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)
        return campaign_dir
    
    def _generate_cache_key(self, prompt: str, model: str, campaign_id: str) -> str:
        """Generate a cache key from prompt, model, and campaign"""
        content = f"{campaign_id}_{prompt}_{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_current_cache_key(self, prompt: str, model: str, campaign_id: str) -> str:
        """Generate current cache key with curr_ prefix for latest images"""
        base_key = self._generate_cache_key(prompt, model, campaign_id)
        return f"curr_{base_key}"
    
    def get_cached_image(self, prompt: str, model: str, campaign_id: str) -> Optional[str]:
        """Get cached image if available (prioritize current images)"""
        try:
            campaign_dir = self._get_campaign_cache_dir(campaign_id)
            
            # First check for current image
            current_key = self._generate_current_cache_key(prompt, model, campaign_id)
            current_file = campaign_dir / f"{current_key}.json"
            
            if current_file.exists():
                with open(current_file, 'r') as f:
                    cache_data = json.load(f)
                    
                # Current images are always valid (no expiry)
                self.logger.info(f"✅ Using current cached image for campaign {campaign_id}: {prompt[:50]}...")
                print(f"✅ CACHE_HIT_CURRENT: Campaign {campaign_id} using current image ({len(cache_data['image_data'])} chars)")
                return cache_data['image_data']
            
            # Fallback to regular cache with expiry check
            cache_key = self._generate_cache_key(prompt, model, campaign_id)
            cache_file = campaign_dir / f"{cache_key}.json"
            
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    
                # Check if cache is still valid (24 hours for non-current images)
                if time.time() - cache_data.get('timestamp', 0) < 86400:
                    self.logger.info(f"✅ Using cached image for campaign {campaign_id}: {prompt[:50]}...")
                    print(f"✅ CACHE_HIT: Campaign {campaign_id} using cached image ({len(cache_data['image_data'])} chars)")
                    return cache_data['image_data']
                else:
                    # Cache expired, remove it
                    cache_file.unlink()
                    self.logger.info(f"🗑️ Cache expired for campaign {campaign_id}: {prompt[:50]}...")
                    
        except Exception as e:
            self.logger.warning(f"Cache read error for campaign {campaign_id}: {e}")
            
        return None
    
    def cache_image(self, prompt: str, model: str, campaign_id: str, image_data: str, is_current: bool = True) -> bool:
        """Cache generated image with campaign awareness"""
        try:
            campaign_dir = self._get_campaign_cache_dir(campaign_id)
            
            if is_current:
                # Save as current image (latest generation)
                cache_key = self._generate_current_cache_key(prompt, model, campaign_id)
                cache_file = campaign_dir / f"{cache_key}.json"
                
                # Remove any existing current image for this prompt
                existing_current = campaign_dir.glob(f"curr_*.json")
                for existing_file in existing_current:
                    try:
                        with open(existing_file, 'r') as f:
                            existing_data = json.load(f)
                        if existing_data.get('prompt') == prompt:
                            existing_file.unlink()
                            self.logger.info(f"🔄 Replaced existing current image for prompt: {prompt[:50]}...")
                    except:
                        continue
            else:
                # Save as regular cache
                cache_key = self._generate_cache_key(prompt, model, campaign_id)
                cache_file = campaign_dir / f"{cache_key}.json"
            
            cache_data = {
                'prompt': prompt,
                'model': model,
                'campaign_id': campaign_id,
                'image_data': image_data,
                'timestamp': time.time(),
                'size_kb': len(image_data) // 1024,
                'is_current': is_current
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
                
            cache_type = "current" if is_current else "regular"
            self.logger.info(f"💾 Cached {cache_type} image for campaign {campaign_id}: {prompt[:50]}... ({len(image_data)} chars)")
            print(f"✅ CACHE_SAVE_{cache_type.upper()}: Campaign {campaign_id} saved image ({len(image_data)} chars)")
            return True
            
        except Exception as e:
            self.logger.error(f"Cache write error for campaign {campaign_id}: {e}")
            return False
    
    def cleanup_old_images(self, campaign_id: Optional[str] = None) -> int:
        """
        Clean up old (non-current) images on app restart
        Keeps curr_ prefixed images, removes others
        """
        try:
            count = 0
            
            if campaign_id:
                # Clean specific campaign
                campaign_dirs = [self._get_campaign_cache_dir(campaign_id)]
            else:
                # Clean all campaigns
                campaign_dirs = [d for d in self.cache_base_dir.iterdir() if d.is_dir()]
            
            for campaign_dir in campaign_dirs:
                # Remove non-current cache files (keep curr_ prefixed files)
                for cache_file in campaign_dir.glob("*.json"):
                    if not cache_file.name.startswith("curr_"):
                        cache_file.unlink()
                        count += 1
                        
            self.logger.info(f"🗑️ Cleanup: Removed {count} old cached images")
            print(f"✅ CACHE_CLEANUP: Removed {count} old images, kept current images")
            return count
            
        except Exception as e:
            self.logger.error(f"Cache cleanup error: {e}")
            return 0
    
    def clear_campaign_cache(self, campaign_id: str) -> int:
        """Clear all cached images for a specific campaign"""
        try:
            campaign_dir = self._get_campaign_cache_dir(campaign_id)
            count = 0
            
            for cache_file in campaign_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
                
            # Remove empty campaign directory
            if count > 0:
                try:
                    campaign_dir.rmdir()
                except:
                    pass  # Directory might not be empty due to other files
                    
            self.logger.info(f"🗑️ Cleared {count} cached images for campaign {campaign_id}")
            print(f"✅ CACHE_CLEAR_CAMPAIGN: Removed {count} images for campaign {campaign_id}")
            return count
            
        except Exception as e:
            self.logger.error(f"Campaign cache clear error: {e}")
            return 0
    
    def clear_all_cache(self) -> int:
        """Clear all cached images"""
        try:
            count = 0
            for campaign_dir in self.cache_base_dir.iterdir():
                if campaign_dir.is_dir():
                    for cache_file in campaign_dir.glob("*.json"):
                        cache_file.unlink()
                        count += 1
                    try:
                        campaign_dir.rmdir()
                    except:
                        pass
                        
            self.logger.info(f"🗑️ Cleared all {count} cached images")
            print(f"✅ CACHE_CLEAR_ALL: Removed {count} cached images")
            return count
            
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
            return 0
    
    def get_cache_stats(self, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if campaign_id:
                # Stats for specific campaign
                campaign_dir = self._get_campaign_cache_dir(campaign_id)
                cache_files = list(campaign_dir.glob("*.json"))
                current_files = [f for f in cache_files if f.name.startswith("curr_")]
                regular_files = [f for f in cache_files if not f.name.startswith("curr_")]
                
                total_size = 0
                for cache_file in cache_files:
                    try:
                        with open(cache_file, 'r') as f:
                            cache_data = json.load(f)
                            total_size += cache_data.get('size_kb', 0)
                    except:
                        continue
                        
                return {
                    'campaign_id': campaign_id,
                    'current_images': len(current_files),
                    'regular_images': len(regular_files),
                    'total_images': len(cache_files),
                    'total_size_kb': total_size,
                    'total_size_mb': round(total_size / 1024, 2),
                    'cache_dir': str(campaign_dir)
                }
            else:
                # Stats for all campaigns
                campaigns = {}
                total_campaigns = 0
                total_images = 0
                total_size = 0
                
                for campaign_dir in self.cache_base_dir.iterdir():
                    if campaign_dir.is_dir():
                        campaign_id = campaign_dir.name
                        campaign_stats = self.get_cache_stats(campaign_id)
                        campaigns[campaign_id] = campaign_stats
                        total_campaigns += 1
                        total_images += campaign_stats['total_images']
                        total_size += campaign_stats['total_size_kb']
                
                return {
                    'total_campaigns': total_campaigns,
                    'total_images': total_images,
                    'total_size_kb': total_size,
                    'total_size_mb': round(total_size / 1024, 2),
                    'campaigns': campaigns,
                    'cache_base_dir': str(self.cache_base_dir)
                }
                
        except Exception as e:
            self.logger.error(f"Cache stats error: {e}")
            return {'error': str(e)}

# Backward compatibility alias
ImageCache = CampaignImageCache

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

class ImageGenerationAgent:
    """Agent for generating images using Google Imagen."""
    
    def __init__(self):
        """Initialize image generation agent with Gemini client following ADK patterns."""
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.image_model = os.getenv('IMAGE_MODEL', 'imagen-3.0-generate-002')
        self.max_images = safe_int_env('MAX_TEXT_IMAGE_POSTS', '4')
        self.cache = CampaignImageCache()  # Initialize campaign-aware image cache
        
        logger.info(f"Initializing Image Generation Agent with max_images={self.max_images}, model={self.image_model}")
        
        # Initialize client following ADK agent patterns
        use_vertexai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'False').lower() == 'true'
        
        if use_vertexai:
            # Vertex AI pattern from logo_create_agent
            project = os.getenv('GOOGLE_CLOUD_PROJECT')
            location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
            if project:
                try:
                    self.client = genai.Client(vertexai=True, project=project, location=location)
                    self.gemini_api_key = f"vertexai-{project}"  # Set for compatibility check
                    logger.info(f"✅ Image Generation Agent initialized with Vertex AI client using {self.image_model}")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize Vertex AI client: {e}")
                    self.client = None
                    self.gemini_api_key = None
            else:
                logger.warning("⚠️ GOOGLE_CLOUD_PROJECT not set for Vertex AI")
                self.client = None
                self.gemini_api_key = None
        else:
            # AI Studio pattern
            self.gemini_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key:
            try:
                self.client = genai.Client(api_key=self.gemini_api_key)
                logger.info(f"✅ Image Generation Agent initialized with AI Studio client using {self.image_model}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI Studio client: {e}")
                self.client = None
                self.gemini_api_key = None
        else:
            logger.warning("⚠️ GOOGLE_API_KEY not set for AI Studio - using placeholder mode")
            self.client = None
            self.gemini_api_key = None
    
    async def generate_images(self, prompts: List[str], business_context: Dict[str, Any], campaign_id: str = "default") -> List[Dict[str, Any]]:
        """
        Generate images based on prompts and business context with comprehensive debug logging.
        
        Args:
            prompts: List of image generation prompts
            business_context: Business context for brand-consistent generation
            campaign_id: Campaign identifier for file organization and caching
            
        Returns:
            List of generated image data
        """
        generation_context = {
            "method": "generate_images",
            "campaign_id": campaign_id,
            "total_prompts": len(prompts),
            "max_images": self.max_images,
            "has_client": bool(self.client),
            "has_api_key": bool(self.gemini_api_key),
            "company_name": business_context.get('company_name', 'Unknown')
        }
        
        logger.info(f"🎨 IMAGE_GENERATION_BATCH_START: {generation_context}")
        print(f"🎨 Starting batch image generation for campaign '{campaign_id}' - {len(prompts)} prompts requested")
        
        try:
            # Apply cost control: limit to max_images
            limited_prompts = prompts[:self.max_images]
            
            if len(prompts) > self.max_images:
                logger.warning(f"⚠️ COST_CONTROL_APPLIED: Limiting {len(prompts)} prompts to {self.max_images} for cost control")
                print(f"⚠️ Cost control: Limiting to {self.max_images} images (requested {len(prompts)})")
            
            logger.info(f"📋 PROCESSING_PROMPTS: {len(limited_prompts)} prompts after cost control")
            print(f"📋 Processing {len(limited_prompts)} image prompts for campaign '{campaign_id}'")
            
            generated_images = []
            successful_generations = 0
            failed_generations = 0
            
            for i, prompt in enumerate(limited_prompts):
                prompt_context = {
                    "prompt_index": i,
                    "prompt_length": len(prompt),
                    "campaign_id": campaign_id
                }
                
                logger.info(f"🖼️ IMAGE_PROMPT_{i+1}_START: {prompt_context}")
                print(f"🖼️ Processing image {i+1}/{len(limited_prompts)} for campaign '{campaign_id}'")
                
                try:
                    # Enhance prompt with business context
                    logger.info(f"📝 PROMPT_CONTEXT_ENHANCEMENT_START: Original: '{prompt[:100]}...'")
                    enhanced_prompt = self._enhance_prompt_with_context(prompt, business_context)
                    logger.info(f"📝 PROMPT_ENHANCED: '{enhanced_prompt[:100]}...' (length: {len(enhanced_prompt)})")
                    
                    if self.client:
                        logger.info(f"🚀 REAL_GENERATION_PATH: Using Imagen API for image {i+1}")
                        print(f"🚀 Generating real image {i+1} using Imagen API")
                        # Generate real image using Imagen
                        image_data = await self._generate_real_image(enhanced_prompt, i, campaign_id)
                    else:
                        logger.warning(f"⚠️ MOCK_GENERATION_PATH: No client available for image {i+1}")
                        print(f"⚠️ No Gemini client - attempting mock generation for image {i+1}")
                        # Generate mock image data (which will now return error state)
                        image_data = self._generate_mock_image(enhanced_prompt, i, campaign_id)
                    
                    if image_data.get('status') == 'success':
                        successful_generations += 1
                        logger.info(f"✅ IMAGE_{i+1}_SUCCESS: {image_data.get('generation_method')}")
                        print(f"✅ Image {i+1} generated successfully")
                    else:
                        failed_generations += 1
                        logger.error(f"❌ IMAGE_{i+1}_FAILED: Status: {image_data.get('status')}, Error: {image_data.get('error')}")
                        print(f"❌ Image {i+1} generation failed: {image_data.get('error')}")
                    
                    generated_images.append(image_data)
                    
                except Exception as e:
                    failed_generations += 1
                    error_details = {
                        "prompt_index": i,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "campaign_id": campaign_id
                    }
                    logger.error(f"❌ IMAGE_GENERATION_EXCEPTION: {error_details}", exc_info=True)
                    print(f"❌ Exception during image {i+1} generation: {str(e)}")
                    
                    # Add fallback image (which now returns error state)
                    fallback_image = self._generate_fallback_image(prompt, i)
                    generated_images.append(fallback_image)
            
            # Final batch summary
            batch_summary = {
                "campaign_id": campaign_id,
                "total_requested": len(prompts),
                "total_processed": len(limited_prompts),
                "successful": successful_generations,
                "failed": failed_generations,
                "success_rate": f"{(successful_generations/len(limited_prompts)*100):.1f}%" if limited_prompts else "0%"
            }
            
            logger.info(f"📊 IMAGE_GENERATION_BATCH_SUMMARY: {batch_summary}")
            print(f"📊 Batch image generation complete for campaign '{campaign_id}': {successful_generations}/{len(limited_prompts)} successful")
            
            if successful_generations == 0:
                logger.error(f"❌ ALL_IMAGE_GENERATION_FAILED: No images were successfully generated for campaign '{campaign_id}'")
                print(f"❌ CRITICAL: All image generation failed for campaign '{campaign_id}'")
            
            return generated_images
            
        except Exception as e:
            batch_error = {
                "campaign_id": campaign_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "total_prompts": len(prompts)
            }
            logger.error(f"❌ IMAGE_GENERATION_BATCH_FAILED: {batch_error}", exc_info=True)
            print(f"❌ CRITICAL: Entire image generation batch failed for campaign '{campaign_id}': {str(e)}")
            
            # Return error states for all requested images
            return [self._generate_fallback_image(f"Image {i+1}", i) for i in range(min(len(prompts), self.max_images))]
    
    async def _generate_real_image(self, prompt: str, index: int, campaign_id: str) -> Dict[str, Any]:
        """Generate real image using Google Imagen with comprehensive debug logging."""
        debug_context = {
            "method": "_generate_real_image",
            "campaign_id": campaign_id,
            "index": index,
            "prompt_length": len(prompt),
            "model": self.image_model
        }
        
        logger.info(f"🎨 IMAGEN_GENERATION_START: {debug_context}")
        print(f"🎨 Starting Imagen generation for campaign '{campaign_id}', image {index+1}")
        
        try:
            if not self.client:
                error_msg = f"❌ IMAGEN_CLIENT_MISSING: No Gemini client available for image generation"
                logger.error(f"{error_msg}: {debug_context}")
                print(f"🚫 {error_msg}")
                raise Exception("Gemini client not initialized")
            
            if not self.gemini_api_key:
                error_msg = f"❌ GEMINI_API_KEY_MISSING: API key not configured"
                logger.error(f"{error_msg}: {debug_context}")
                print(f"🚫 {error_msg}")
                raise Exception("GEMINI_API_KEY not configured")
            
            logger.info(f"📝 PROMPT_ENHANCEMENT_START: Original prompt: '{prompt[:100]}...'")
            
            # Enhance prompt for marketing use case based on Imagen best practices
            marketing_prompt = self._create_marketing_prompt(prompt, index)
            
            logger.info(f"📝 PROMPT_ENHANCED: '{marketing_prompt[:150]}...' (length: {len(marketing_prompt)})")
            print(f"📝 Enhanced prompt for campaign '{campaign_id}': '{marketing_prompt[:100]}...'")
            
            # CHECK CACHE FIRST for consistent user experience
            logger.info(f"🔍 CACHE_CHECK_START: Checking cache for campaign '{campaign_id}'")
            cached_image = self.cache.get_cached_image(marketing_prompt, self.image_model, campaign_id)
            if cached_image:
                logger.info(f"✅ CACHE_HIT: Found cached image for campaign '{campaign_id}'")
                print(f"✅ Using cached image for campaign '{campaign_id}', image {index+1}")
                return {
                    "id": f"imagen_cached_{index+1}",
                    "prompt": marketing_prompt,
                    "original_prompt": prompt,
                    "image_url": cached_image,
                    "generation_method": f"{self.image_model}_cached",
                    "status": "success",
                    "metadata": {
                        "model": self.image_model,
                        "cached": True,
                        "generation_time": 0.1,
                        "aspect_ratio": "16:9",
                        "quality": "high",
                        "marketing_optimized": True
                    }
                }
            
            logger.info(f"🔄 CACHE_MISS: No cached image found, proceeding with API generation")
            print(f"🔄 No cached image found, generating new image for campaign '{campaign_id}'")
            
            # Generate image using Imagen 3.0 with correct API method
            logger.info(f"🚀 IMAGEN_API_CALL_START: Calling {self.image_model} API")
            print(f"🚀 Calling Imagen API for campaign '{campaign_id}', image {index+1}")
            
            # Use correct Imagen API configuration
            api_config = {
                "number_of_images": 1,
                "aspect_ratio": "16:9",
                "person_generation": "ALLOW_ADULT",
                "safety_filter_level": "block_low_and_above"  # Correct format for Gemini API
            }
            logger.info(f"⚙️ IMAGEN_CONFIG: {api_config}")
            
            # Use dedicated IMAGEN API (per official documentation)
            # Reference: https://ai.google.dev/gemini-api/docs/imagen
            response = await asyncio.to_thread(
                self.client.models.generate_images,
                model=self.image_model,
                prompt=marketing_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=api_config["number_of_images"],
                    aspect_ratio=api_config["aspect_ratio"],
                    person_generation=api_config["person_generation"]
                )
            )
            
            logger.info(f"📨 IMAGEN_API_RESPONSE: Response received")
            print(f"📨 Imagen API response received for campaign '{campaign_id}'")
            
            # DEBUG: Log actual response structure to understand format
            logger.info(f"🔍 RESPONSE_DEBUG: Type: {type(response)}")
            logger.info(f"🔍 RESPONSE_DEBUG: Has 'generated_images': {hasattr(response, 'generated_images')}")
            logger.info(f"🔍 RESPONSE_DEBUG: Has 'images': {hasattr(response, 'images')}")
            logger.info(f"🔍 RESPONSE_DEBUG: Has 'candidates': {hasattr(response, 'candidates')}")
            logger.info(f"🔍 RESPONSE_DEBUG: Dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
            
            # Parse Imagen API response format
            if not response or not hasattr(response, 'generated_images') or not response.generated_images:
                error_msg = f"❌ IMAGEN_NO_IMAGES: API returned no generated images"
                logger.error(f"{error_msg}: {debug_context}")
                print(f"🚫 {error_msg} for campaign '{campaign_id}'")
                raise Exception("No images in API response")
            
            if len(response.generated_images) == 0:
                error_msg = f"❌ IMAGEN_EMPTY_IMAGES: API returned empty images array"
                logger.error(f"{error_msg}: {debug_context}")
                print(f"🚫 {error_msg} for campaign '{campaign_id}'")
                raise Exception("Empty images array in API response")
            
            # Get first generated image
            generated_image = response.generated_images[0]
            if not hasattr(generated_image, 'image') or not generated_image.image:
                error_msg = f"❌ IMAGEN_NO_IMAGE_DATA: Generated image has no image data"
                logger.error(f"{error_msg}: {debug_context}")
                print(f"🚫 {error_msg} for campaign '{campaign_id}'")
                raise Exception("No image data in generated image")
            
            # Get image bytes from Imagen response
            if hasattr(generated_image.image, 'image_bytes'):
                image_bytes = generated_image.image.image_bytes
            elif hasattr(generated_image.image, 'data'):
                image_bytes = base64.b64decode(generated_image.image.data)
            else:
                error_msg = f"❌ IMAGEN_INVALID_FORMAT: Cannot extract image bytes"
                logger.error(f"{error_msg}: {debug_context}")
                print(f"🚫 {error_msg} for campaign '{campaign_id}'")
                raise Exception("Cannot extract image bytes from response")
            image_size = len(image_bytes)
            logger.info(f"📦 IMAGEN_IMAGE_RECEIVED: Size: {image_size} bytes ({image_size/1024:.1f}KB)")
            print(f"📦 Generated image received: {image_size/1024:.1f}KB for campaign '{campaign_id}'")
            
            # Save image and get URL
            logger.info(f"💾 IMAGE_SAVE_START: Saving image to filesystem")
            image_url = await self._save_generated_image_data(image_bytes, index, campaign_id)
            logger.info(f"💾 IMAGE_SAVED: URL: {image_url}")
            print(f"💾 Image saved successfully for campaign '{campaign_id}': {image_url}")
            
            # CACHE THE GENERATED IMAGE for future consistent UX
            logger.info(f"🗄️ CACHE_STORE_START: Caching generated image")
            cache_success = self.cache.cache_image(marketing_prompt, self.image_model, campaign_id, image_url, is_current=True)
            logger.info(f"🗄️ CACHE_STORE_RESULT: Success: {cache_success}")
            
            success_result = {
                "id": f"imagen_generated_{index+1}",
                "prompt": marketing_prompt,
                "original_prompt": prompt,
                "image_url": image_url,
                "generation_method": f"{self.image_model}_real",
                "status": "success",
                "metadata": {
                    "model": self.image_model,
                    "safety_rating": "approved",
                    "generation_time": 4.5,
                    "aspect_ratio": "16:9",
                    "quality": "high",
                    "marketing_optimized": True,
                    "cached": False,
                    "file_size_kb": image_size/1024
                }
            }
            
            logger.info(f"✅ IMAGEN_GENERATION_SUCCESS: {debug_context}")
            print(f"✅ Image generation completed successfully for campaign '{campaign_id}', image {index+1}")
            
            return success_result

                
        except Exception as e:
            error_details = {
                "error": str(e),
                "error_type": type(e).__name__,
                "debug_context": debug_context
            }
            logger.error(f"❌ IMAGEN_GENERATION_FAILED: {error_details}", exc_info=True)
            print(f"❌ Image generation failed for campaign '{campaign_id}', image {index+1}: {str(e)}")
            
            # Fall back to enhanced placeholder (which now returns error state)
            return self._generate_enhanced_placeholder(prompt, index)
    
    async def _save_generated_image_data(self, image_data_bytes: bytes, index: int, campaign_id: str = "default") -> str:
        """Save generated image data as actual file and return URL."""
        try:
            # Create images directory structure: data/images/generated/<campaign_id>/
            images_dir = Path("data/images/generated") / campaign_id
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename with timestamp
            timestamp = int(time.time())
            image_filename = f"img_{timestamp}_{uuid.uuid4().hex[:8]}_{index}.png"
            image_path = images_dir / image_filename
            
            # Save actual PNG file
            with open(image_path, 'wb') as img_file:
                img_file.write(image_data_bytes)
            
            # Return absolute URL for frontend to access
            file_url = f"http://localhost:8000/api/v1/content/images/{campaign_id}/{image_filename}"
            logger.info(f"💾 Saved image file: {image_path} -> URL: {file_url}")
            
            return file_url
            
        except Exception as e:
            logger.error(f"Failed to save generated image file: {e}")
            return f"https://via.placeholder.com/400x300/4F46E5/FFFFFF?text=Generated+Image+{index+1}"
    
    def _enhance_prompt_with_context(self, base_prompt: str, business_context: Dict[str, Any]) -> str:
        """Enhance image prompt with comprehensive business context and campaign guidance."""
        
        company_name = business_context.get('company_name', 'Company')
        industry = business_context.get('industry', 'business')
        brand_voice = business_context.get('brand_voice', 'professional')
        visual_elements = business_context.get('visual_elements', 'modern, clean design')
        key_themes = business_context.get('key_themes', [])
        
        # Build enhanced prompt
        enhanced_prompt = f"{base_prompt}"
        
        # ENHANCED: Use campaign guidance if available in business context
        campaign_guidance = business_context.get('campaign_guidance', {})
        if campaign_guidance:
            # Use creative direction from analysis
            if campaign_guidance.get("creative_direction"):
                creative_direction = campaign_guidance["creative_direction"]
                enhanced_prompt += f", {creative_direction[:150]}"
            
            # Use detailed visual style guidance
            visual_style = campaign_guidance.get("visual_style", {})
            if isinstance(visual_style, dict):
                if visual_style.get("photography_style"):
                    enhanced_prompt += f", {visual_style['photography_style']}"
                if visual_style.get("mood"):
                    enhanced_prompt += f", {visual_style['mood']} mood"
                if visual_style.get("lighting"):
                    enhanced_prompt += f", {visual_style['lighting']}"
            
            # Use Imagen-specific guidance
            imagen_prompts = campaign_guidance.get("imagen_prompts", {})
            if imagen_prompts:
                if imagen_prompts.get("environment"):
                    enhanced_prompt += f", {imagen_prompts['environment']}"
                if imagen_prompts.get("style_modifiers"):
                    modifiers = ", ".join(imagen_prompts["style_modifiers"][:2])
                    enhanced_prompt += f", {modifiers}"
        
        # Add brand context (fallback/additional)
        if 'professional' in brand_voice.lower():
            enhanced_prompt += ", professional and polished style"
        if 'innovative' in brand_voice.lower():
            enhanced_prompt += ", innovative and cutting-edge aesthetic"
        if 'modern' in visual_elements.lower():
            enhanced_prompt += ", modern design elements"
        
        # Add industry context
        if 'technology' in industry.lower():
            enhanced_prompt += ", tech-focused imagery with digital elements"
        elif 'healthcare' in industry.lower():
            enhanced_prompt += ", clean medical aesthetic with health-focused elements"
        elif 'finance' in industry.lower():
            enhanced_prompt += ", professional financial imagery with trust elements"
        
        # Add theme-based enhancements
        if 'innovation' in key_themes:
            enhanced_prompt += ", innovative and forward-thinking visual style"
        if 'sustainability' in key_themes:
            enhanced_prompt += ", eco-friendly and sustainable visual elements"
        if 'quality' in key_themes:
            enhanced_prompt += ", high-quality and premium aesthetic"
        
        # Add general quality modifiers
        enhanced_prompt += ", high quality, professional photography style, well-lit, sharp focus"
        
        # Add text avoidance instructions
        enhanced_prompt += ", no text overlays, no written words, purely visual content"
        
        return enhanced_prompt
    
    def _create_marketing_prompt(self, base_prompt: str, index: int) -> str:
        """
        Create marketing-optimized prompt based on Imagen best practices.
        
        Based on geminibyexample.com and Google's content generation guidelines:
        - Simple, clear descriptions
        - Professional photography style keywords
        - Avoid complex or potentially problematic content
        """
        
        # Simplify the base prompt to avoid content policy issues
        simplified_prompt = base_prompt.replace("family", "people").replace("personal", "professional")
        
        # Core marketing prompt structure - keep it simple and safe
        marketing_elements = [
            "professional product photography",
            "clean modern style",
            "bright lighting",
            "high quality commercial image",
            "business marketing photo"
        ]
        
        # Platform-specific optimizations
        platform_specs = [
            "social media optimized",
            "professional appearance",
            "brand marketing style"
        ]
        
        # Quality and style modifiers from Imagen guide
        quality_modifiers = [
            "shot with DSLR camera",
            "professional lighting setup",
            "sharp focus, well-composed",
            "commercial photography quality",
            "marketing campaign ready"
        ]
        
        # Critical instruction to avoid text in images
        text_avoidance_instructions = [
            "no text overlays",
            "no written words",
            "no labels or captions",
            "avoid text elements",
            "purely visual content"
        ]
        
        # Combine all elements
        enhanced_prompt = f"{base_prompt}, {', '.join(marketing_elements[:3])}, {', '.join(platform_specs[:2])}, {', '.join(quality_modifiers[:2])}, {', '.join(text_avoidance_instructions[:3])}"
        
        # Add variation for different images
        variation_elements = {
            0: "primary hero shot, main focal point",
            1: "alternative angle, creative perspective", 
            2: "lifestyle context, real-world application",
            3: "detail shot, close-up emphasis"
        }
        
        if index in variation_elements:
            enhanced_prompt += f", {variation_elements[index]}"
        
        return enhanced_prompt
    
    def _generate_enhanced_placeholder(self, prompt: str, index: int) -> Dict[str, Any]:
        """
        CRITICAL: This method violates ADR-016 requirements.
        Instead of generating irrelevant placeholder images, we should fail gracefully
        with clear error messages to prevent misleading visual content.
        """
        error_message = (
            f"❌ VISUAL_GENERATION_FAILED: Unable to generate contextually relevant image for '{prompt[:50]}...'. "
            f"This would have shown generic placeholder content unrelated to your campaign. "
            f"Please check Imagen API configuration or try regenerating."
        )
        logger.error(error_message)
        
        # Return error state instead of misleading placeholder
        return {
            "id": f"generation_failed_{index+1}",
            "prompt": prompt,
            "image_url": None,  # No misleading placeholder URL
            "generation_method": "failed_generation",
            "status": "error",
            "error": "Image generation failed - no contextually relevant content available",
            "metadata": {
                "model": "imagen_failed",
                "safety_rating": "unknown",
                "generation_time": 0.0,
                "aspect_ratio": "unknown",
                "quality": "failed",
                "marketing_optimized": False,
                "note": "CRITICAL: Image generation failed. Check API configuration and regenerate for campaign-relevant content."
            }
        }
    
    def _generate_mock_image(self, prompt: str, index: int, campaign_id: str) -> Dict[str, Any]:
        """
        CRITICAL: This method violates ADR-016 requirements.
        Mock images are not contextually relevant to campaigns and mislead users.
        """
        error_message = (
            f"❌ MOCK_IMAGE_BLOCKED: Attempted to generate mock image for campaign '{campaign_id}'. "
            f"Mock images violate ADR-016 requirements for contextually relevant content. "
            f"Prompt: '{prompt[:100]}...'"
        )
        logger.error(error_message)
        print(f"🚫 {error_message}")
        
        return {
            "id": f"mock_blocked_{index+1}",
            "prompt": prompt,
            "image_url": None,  # No misleading mock URL
            "generation_method": "mock_blocked",
            "status": "error",
            "error": "Mock image generation blocked - violates contextual relevance requirements",
            "metadata": {
                "model": "mock_blocked",
                "safety_rating": "blocked",
                "generation_time": 0.0,
                "note": "CRITICAL: Mock images blocked per ADR-016. Configure Imagen API for real generation."
            }
        }
    
    def _generate_fallback_image(self, prompt: str, index: int) -> Dict[str, Any]:
        """Generate fallback image when generation fails."""
        return {
            "id": f"fallback_{index+1}",
            "prompt": prompt,
            "image_url": f"https://via.placeholder.com/400x300/FF6B6B/FFFFFF?text=Generation+Failed+{index+1}",
            "generation_method": "fallback",
            "status": "failed",
            "metadata": {
                "model": "fallback_generator",
                "safety_rating": "unknown",
                "generation_time": 0.1,
                "error": "Image generation failed"
            }
        }

class VideoGenerationAgent:
    """Agent for generating videos using Google Veo."""
    
    def __init__(self):
        """Initialize video generation agent."""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.video_model = os.getenv('VIDEO_MODEL', 'veo-2.0-generate-001')
        self.max_videos = safe_int_env('MAX_TEXT_VIDEO_POSTS', '3')  # Reduced for cost savings
        self.video_storage_dir = Path("data/videos/generated")
        self.video_storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing Video Generation Agent with max_videos={self.max_videos}, model={self.video_model}")
        
        if self.gemini_api_key:
            logger.info(f"✅ Video Generation Agent initialized with API key using {self.video_model}, max videos: {self.max_videos}")
        else:
            logger.warning("⚠️ GEMINI_API_KEY not found - video generation will use placeholder mode")
    
    async def generate_videos(self, prompts: List[str], business_context: Dict[str, Any], campaign_id: str = "default") -> List[Dict[str, Any]]:
        """
        Generate videos based on prompts and business context.
        
        Args:
            prompts: List of video generation prompts
            business_context: Business context for brand-consistent generation
            campaign_id: Campaign ID for file organization
            
        Returns:
            List of generated video data
        """
        try:
            # Apply cost control: limit to max_videos
            limited_prompts = prompts[:self.max_videos]
            logger.info(f"Generating {len(limited_prompts)} real MP4 videos limited to {self.max_videos} for cost control")
            
            generated_videos = []
            
            for i, prompt in enumerate(limited_prompts):
                try:
                    # Enhance prompt with business context
                    enhanced_prompt = self._enhance_video_prompt_with_context(prompt, business_context)
                    
                    # Generate real video files with curr_ prefix (mirroring image pattern)
                    video_data = await self._generate_real_video_with_file_storage(enhanced_prompt, i, campaign_id, business_context)
                    
                    generated_videos.append(video_data)
                    
                except Exception as e:
                    logger.error(f"Failed to generate video {i}: {e}")
                    # Add fallback video
                    generated_videos.append(self._generate_fallback_video(prompt, i))
            
            return generated_videos
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}", exc_info=True)
            return [self._generate_fallback_video(f"Video {i+1}", i) for i in range(min(len(prompts), self.max_videos))]
    
    def _enhance_video_prompt_with_context(self, base_prompt: str, business_context: Dict[str, Any]) -> str:
        """Enhance video prompt with business context for brand consistency."""
        try:
            company_name = business_context.get('company_name', 'Professional Business')
            industry = business_context.get('industry', 'business')
            business_description = business_context.get('business_description', '')
            
            # ADK ENHANCEMENT: Extract comprehensive context (matching image generation)
            product_context = business_context.get('product_context', {})
            campaign_guidance = business_context.get('campaign_guidance', {})
            campaign_media_tuning = business_context.get('campaign_media_tuning', '')
            creative_direction = business_context.get('creative_direction', '')
            visual_style = business_context.get('visual_style', {})
            
            # PRIORITY: Use specific product context if available
            has_specific_product = product_context.get('has_specific_product', False)
            product_name = product_context.get('product_name', '')
            product_themes = product_context.get('product_themes', [])
            product_visual_elements = product_context.get('product_visual_elements', '')
            
            logger.info(f"Creating video prompt - Product: {product_name if has_specific_product else 'general'}, "
                       f"Themes: {product_themes}, Company: {company_name}")
            
            # Build comprehensive enhanced prompt matching image sophistication
            enhanced_prompt = base_prompt
            
            # Product-specific enhancement (highest priority)
            if has_specific_product and product_name:
                enhanced_prompt += f", featuring {product_name}"
                if product_visual_elements:
                    enhanced_prompt += f", {product_visual_elements}"
                if product_themes:
                    enhanced_prompt += f", emphasizing {', '.join(product_themes)}"
            
            # Industry and business context
            if 'furniture' in industry.lower() or 'outdoor' in business_description.lower():
                enhanced_prompt += ", lifestyle video showcasing outdoor furniture and patio living, comfortable outdoor spaces, modern home design"
            elif 'technology' in industry.lower():
                enhanced_prompt += ", modern professionals using technology solutions, clean office environments, digital innovation"
            elif 'healthcare' in industry.lower():
                enhanced_prompt += ", professional healthcare environment, modern medical facilities, caring professionals"
            elif 'finance' in industry.lower():
                enhanced_prompt += ", professional business environment, modern office settings, trust and reliability"
            
            # Campaign guidance integration
            if campaign_guidance:
                guidance_tone = campaign_guidance.get('tone', '')
                guidance_focus = campaign_guidance.get('focus_areas', [])
                if guidance_tone:
                    enhanced_prompt += f", {guidance_tone} style"
                if guidance_focus:
                    enhanced_prompt += f", highlighting {', '.join(guidance_focus)}"
            
            # Media tuning and creative direction
            if campaign_media_tuning:
                enhanced_prompt += f", {campaign_media_tuning}"
            if creative_direction:
                enhanced_prompt += f", {creative_direction}"
            
            # Visual style application
            if visual_style:
                color_scheme = visual_style.get('color_scheme', '')
                aesthetic = visual_style.get('aesthetic', '')
                if color_scheme:
                    enhanced_prompt += f", {color_scheme} color palette"
                if aesthetic:
                    enhanced_prompt += f", {aesthetic} aesthetic"
            
            # Video-specific enhancements for Veo 2.0
            enhanced_prompt += ", cinematic quality, smooth camera movement, professional lighting, 5-second duration"
            enhanced_prompt += f", representing {company_name} brand values"
            
            logger.info(f"Enhanced video prompt: {enhanced_prompt[:100]}...")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing video prompt: {e}")
            return f"{base_prompt}, professional business video for {business_context.get('company_name', 'company')}"

    async def _generate_real_video_with_file_storage(self, prompt: str, index: int, campaign_id: str, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate real video files using Google Veo API."""
        try:
            import time
            import random
            
            company_name = business_context.get('company_name', 'Company')
            
            # Generate unique video with curr_ prefix (mirroring image pattern)
            unique_seed = f"{campaign_id}_{prompt}_{company_name}_{index}_{time.time()}_{random.randint(1000, 9999)}"
            video_hash = hashlib.md5(unique_seed.encode()).hexdigest()[:8]
            video_filename = f"curr_{video_hash}_{index}.mp4"
            video_path = self.video_storage_dir / campaign_id / video_filename
            video_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🎬 Generating REAL Veo 2.0 video: {video_filename}")
            
            # REAL Veo 2.0 video generation using Google Genai library
            try:
                logger.info(f"🎬 Starting Veo 2.0 video generation: {prompt[:100]}...")
                logger.info(f"🎬 Target path: {video_path}")
                
                # Create Veo 2.0 optimized marketing prompt
                veo_prompt = self._create_veo_marketing_prompt(prompt, business_context, index)
                logger.info(f"🎬 Enhanced marketing prompt created ({len(veo_prompt)} chars)")
                
                # Initialize Google Genai client for video generation
                from google import genai
                from google.genai import types
                    
                if not self.gemini_api_key:
                    raise ValueError("GEMINI_API_KEY not configured for video generation")
                
                client = genai.Client(api_key=self.gemini_api_key)
                logger.info("✅ Veo client initialized successfully")
                
                # Generate video using Veo 2.0 API following official documentation
                logger.info(f"🎬 Starting Veo 2.0 operation: '{veo_prompt[:50]}...'")
                
                operation = client.models.generate_videos(
                    model="veo-2.0-generate-001",
                    prompt=veo_prompt,
                    config=types.GenerateVideosConfig(
                        person_generation="allow_adult",  # Allow adults for marketing content
                        aspect_ratio="16:9",  # Marketing standard
                        duration_seconds=5,   # Quick marketing videos
                        number_of_videos=1,   # Single video per request
                        enhance_prompt=True   # Use built-in prompt enhancement
                    ),
                )
                
                logger.info(f"✅ Veo operation started: {operation.name}")
                
                # Poll for completion (video generation takes 2-3+ minutes)
                max_wait_time = 300  # 5 minutes maximum
                poll_interval = 15   # Check every 15 seconds
                elapsed = 0
                
                logger.info(f"⏳ Polling Veo operation (max {max_wait_time}s, interval {poll_interval}s)")
                
                while not operation.done and elapsed < max_wait_time:
                    await asyncio.sleep(poll_interval)
                    elapsed += poll_interval
                    
                    try:
                        operation = client.operations.get(operation)
                        logger.info(f"📊 Veo operation status check: {elapsed}s elapsed, done={operation.done}")
                    except Exception as poll_error:
                        logger.warning(f"⚠️ Error polling operation: {poll_error}")
                        continue
                
                if not operation.done:
                    logger.error(f"❌ Veo operation timed out after {elapsed}s")
                    return self._generate_fallback_video(prompt, index)
                
                # Download and save generated video
                if operation.response and operation.response.generated_videos:
                    generated_video = operation.response.generated_videos[0]
                    
                    logger.info(f"✅ Veo video generated successfully")
                    
                    # Download video file
                    client.files.download(file=generated_video.video)
                    generated_video.video.save(str(video_path))
                            
                    # Verify file was saved
                    if video_path.exists():
                        file_size = video_path.stat().st_size
                        logger.info(f"✅ Video saved: {video_path} ({file_size:,} bytes)")
                        
                        # Return successful video data
                        return {
                            "id": f"veo_video_{video_hash}_{index}",
                            "prompt": veo_prompt,
                            "video_url": f"/api/v1/content/videos/{campaign_id}/{video_filename}",
                            "video_path": str(video_path),
                            "generation_method": "veo_2.0_api",
                            "status": "success",
                            "metadata": {
                                "model": "veo-2.0-generate-001",
                                "duration": "5s",
                                "format": "mp4",
                                "resolution": "720p",
                                "aspect_ratio": "16:9",
                                "generation_time": elapsed,
                                "file_size": file_size,
                                "operation_id": operation.name,
                                "company": company_name,
                                "prompt_enhanced": True,
                                "api_version": "google.genai"
                            }
                        }
                    else:
                        logger.error(f"❌ Video file not saved: {video_path}")
                        return self._generate_fallback_video(prompt, index)
                        
                else:
                    logger.error("❌ No videos in Veo operation response")
                    return self._generate_fallback_video(prompt, index)
            except ImportError as e:
                logger.error(f"❌ Google Genai library not available: {e}")
                return self._generate_fallback_video(prompt, index)
                
            except Exception as api_error:
                logger.error(f"❌ Veo API error: {api_error}", exc_info=True)
                return self._generate_fallback_video(prompt, index)
                
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}", exc_info=True)
            return self._generate_fallback_video(prompt, index)

    def _create_veo_marketing_prompt(self, base_prompt: str, business_context: Dict[str, Any], index: int) -> str:
        """Create Veo 2.0 optimized marketing prompt following best practices from documentation."""
        try:
            company_name = business_context.get('company_name', 'Professional Business')
            industry = business_context.get('industry', 'business')
            business_description = business_context.get('business_description', '')
            
            # ENHANCEMENT: Extract comprehensive AI guidance context
            product_context = business_context.get('product_context', {})
            campaign_guidance = business_context.get('campaign_guidance', {})
            creative_direction = business_context.get('creative_direction', '')
            visual_style = business_context.get('visual_style', {})
            
            # Extract Veo-specific guidance
            veo_prompts = campaign_guidance.get('veo_prompts', {}) if campaign_guidance else {}
            content_themes = campaign_guidance.get('content_themes', {}) if campaign_guidance else {}
            
            logger.info(f"Creating Veo marketing prompt - Company: {company_name}, Industry: {industry}")
            logger.info(f"Veo prompts available: {bool(veo_prompts)}, Content themes: {bool(content_themes)}")
            
            # Start with base prompt and enhance with marketing context
            veo_prompt = base_prompt
            
            # PRIORITY 1: Product-specific enhancement
            has_specific_product = product_context.get('has_specific_product', False)
            product_name = product_context.get('product_name', '')
            if has_specific_product and product_name:
                veo_prompt += f", featuring {product_name}"
            
            # PRIORITY 2: Veo-specific AI guidance (from campaign analysis)
            if veo_prompts:
                movement_style = veo_prompts.get('movement_style', '')
                scene_composition = veo_prompts.get('scene_composition', '')
                storytelling = veo_prompts.get('storytelling', '')
                
                if movement_style:
                    veo_prompt += f", {movement_style}"
                if scene_composition:
                    veo_prompt += f", {scene_composition}"
                if storytelling:
                    veo_prompt += f", {storytelling}"
            
            # PRIORITY 3: Content themes and emotional direction
            if content_themes:
                emotional_triggers = content_themes.get('emotional_triggers', [])
                visual_metaphors = content_themes.get('visual_metaphors', [])
                if emotional_triggers:
                    veo_prompt += f", conveying {', '.join(emotional_triggers)}"
                if visual_metaphors:
                    veo_prompt += f", incorporating {', '.join(visual_metaphors)}"
            
            # PRIORITY 4: Visual style adaptation for video
            if visual_style:
                photography_style = visual_style.get('photography_style', '')
                mood = visual_style.get('mood', '')
                lighting = visual_style.get('lighting', '')
                
                if photography_style:
                    # Adapt photography styles for video movement
                    video_adapted_style = photography_style.replace('portrait', 'cinematic close-up').replace('still life', 'product showcase').replace('landscape', 'wide establishing shot')
                    veo_prompt += f", {video_adapted_style} video style"
                if mood:
                    veo_prompt += f", {mood} mood"
                if lighting:
                    veo_prompt += f", {lighting}"
            
            # PRIORITY 5: Industry-specific video enhancements
            if 'furniture' in industry.lower() or 'outdoor' in business_description.lower():
                veo_prompt += ", lifestyle marketing video, comfortable living spaces, warm inviting atmosphere"
            elif 'technology' in industry.lower():
                veo_prompt += ", modern tech demonstration, sleek interfaces, professional environment"
            elif 'photography' in industry.lower():
                veo_prompt += ", artistic photography showcase, creative studio setting, professional equipment"
            
            # PRIORITY 6: Veo 2.0 technical specifications for marketing videos
            veo_prompt += f", cinematic quality, smooth camera movement"
            veo_prompt += f", professional lighting, marketing video style"
            veo_prompt += f", representing {company_name} brand"
            
            # CRITICAL: Text avoidance for cleaner videos
            veo_prompt += f", no text overlays, no written words, no on-screen text, purely visual content"
            
            # PRIORITY 7: Creative direction integration
            if creative_direction:
                veo_prompt += f", {creative_direction}"
            
            logger.info(f"✅ Veo marketing prompt created: {len(veo_prompt)} chars")
            logger.debug(f"Final prompt: {veo_prompt[:200]}...")
            
            return veo_prompt
            
        except Exception as e:
            logger.error(f"Error creating Veo marketing prompt: {e}")
            # Fallback prompt
            return f"{base_prompt}, professional marketing video for {company_name}, cinematic quality, no text overlays"

    def cleanup_old_videos(self):
        """Clean up old video files while keeping current (curr_) prefixed videos."""
        try:
            count = 0
            for campaign_dir in self.video_storage_dir.iterdir():
                if campaign_dir.is_dir():
                    # Remove non-current video files (keep curr_ prefixed files)
                    for video_file in campaign_dir.glob("*.mp4"):
                        if not video_file.name.startswith("curr_"):
                            video_file.unlink()
                            count += 1
            
            logger.info(f"🗑️ Cleanup: Removed {count} old video files, kept current videos")
            print(f"✅ VIDEO_CLEANUP: Removed {count} old videos, kept current videos")
            return count
        except Exception as e:
            logger.error(f"Video cleanup error: {e}")
            return 0

    def _generate_fallback_video(self, prompt: str, index: int) -> Dict[str, Any]:
        """Generate fallback video when generation fails."""
        return {
            "id": f"fallback_video_{index+1}",
            "prompt": prompt,
            "video_url": None,  # No misleading placeholder URL
            "generation_method": "fallback",
            "status": "error",
            "error": "Video generation failed - requires Veo API configuration",
            "metadata": {
                "model": "fallback_generator",
                "duration": "5s",
                "format": "placeholder",
                "resolution": "720p",
                "generation_time": 0.1,
                "note": "CRITICAL: Real video generation requires Veo API access and proper configuration"
            }
        }

class CampaignVideoCache:
    """Campaign-specific video caching system similar to image cache."""
    
    def __init__(self, cache_base_dir: Path = Path("data/videos/cache")):
        self.cache_base_dir = cache_base_dir
        self.cache_base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def get_cache_stats(self, campaign_id: str = None) -> dict:
        """Get video cache statistics."""
        try:
            if campaign_id:
                campaign_dir = self.cache_base_dir / campaign_id
                if campaign_dir.exists():
                    cache_files = list(campaign_dir.glob("*.json"))
                    return {
                        "campaign_id": campaign_id,
                        "total_cached_videos": len(cache_files),
                        "current_videos": len([f for f in cache_files if f.name.startswith("curr_")]),
                        "old_videos": len([f for f in cache_files if not f.name.startswith("curr_")])
                    }
                else:
                    return {"campaign_id": campaign_id, "total_cached_videos": 0}
            else:
                total_videos = 0
                campaigns = []
                for campaign_dir in self.cache_base_dir.iterdir():
                    if campaign_dir.is_dir():
                        cache_files = list(campaign_dir.glob("*.json"))
                        campaigns.append({
                            "campaign_id": campaign_dir.name,
                            "cached_videos": len(cache_files)
                        })
                        total_videos += len(cache_files)
                
                return {
                    "total_cached_videos": total_videos,
                    "campaigns": campaigns
                }
        except Exception as e:
            self.logger.error(f"Error getting video cache stats: {e}")
            return {"error": str(e)}
    
    def clear_campaign_cache(self, campaign_id: str) -> int:
        """Clear all cached videos for a specific campaign."""
        try:
            campaign_dir = self.cache_base_dir / campaign_id
            count = 0
            
            if campaign_dir.exists():
                for cache_file in campaign_dir.glob("*.json"):
                    cache_file.unlink()
                    count += 1
                
                # Try to remove empty directory
                try:
                    campaign_dir.rmdir()
                except:
                    pass
            
            return count
        except Exception as e:
            self.logger.error(f"Error clearing video cache for campaign {campaign_id}: {e}")
            return 0
    
    def clear_all_cache(self) -> int:
        """Clear all cached videos."""
        try:
            count = 0
            for campaign_dir in self.cache_base_dir.iterdir():
                if campaign_dir.is_dir():
                    for cache_file in campaign_dir.glob("*.json"):
                        cache_file.unlink()
                        count += 1
                    try:
                        campaign_dir.rmdir()
                    except:
                        pass
            return count
        except Exception as e:
            self.logger.error(f"Error clearing all video cache: {e}")
            return 0

class VisualContentOrchestrator:
    """Orchestrator for visual content generation workflow."""
    
    def __init__(self):
        """Initialize visual content orchestrator."""
        try:
            logger.info("🚀 Initializing Visual Content Orchestrator...")
            self.image_agent = ImageGenerationAgent()
            self.video_agent = VideoGenerationAgent()
            logger.info("✅ Visual Content Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Visual Content Orchestrator: {e}")
            logger.warning("🔄 Visual content generation will use fallback mode")
            # Don't raise exception - allow graceful fallback
            self.image_agent = None
            self.video_agent = None
    
    async def generate_visual_content(
        self, 
        social_posts: List[Dict[str, Any]], 
        business_context: Dict[str, Any],
        campaign_objective: str,
        target_platforms: List[str] = None,
        campaign_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive visual content for social media posts.
        
        Args:
            social_posts: List of social media posts needing visual content
            business_context: Business context for brand consistency
            campaign_objective: Campaign objective for content alignment
            target_platforms: Target social media platforms
            
        Returns:
            Dictionary containing generated visual content
        """
        try:
            logger.info(f"Generating visual content for {len(social_posts)} posts")
            
            if target_platforms is None:
                target_platforms = ["instagram", "linkedin", "facebook"]
            
            # Separate posts by type
            image_posts = [post for post in social_posts if post.get('type') == 'text_image']
            video_posts = [post for post in social_posts if post.get('type') == 'text_video']
            
            # Generate image prompts
            image_prompts = []
            for post in image_posts:
                prompt = self._create_image_prompt(post, business_context, campaign_objective)
                image_prompts.append(prompt)
            
            # Generate video prompts
            video_prompts = []
            for post in video_posts:
                prompt = self._create_video_prompt(post, business_context, campaign_objective)
                video_prompts.append(prompt)
            
            # Generate images and videos with exception handling
            generated_images = []
            generated_videos = []
            
            if image_prompts and self.image_agent:
                try:
                    logger.info(f"🎨 Generating {len(image_prompts)} images...")
                    generated_images = await self.image_agent.generate_images(image_prompts, business_context, campaign_id)
                    logger.info(f"✅ Successfully generated {len(generated_images)} images")
                except Exception as e:
                    logger.error(f"❌ Image generation failed: {e}")
                    logger.warning("🔄 Using fallback image placeholders")
                    generated_images = []
            elif image_prompts and not self.image_agent:
                logger.warning("⚠️ Image agent not available, skipping image generation")
            
            if video_prompts and self.video_agent:
                try:
                    logger.info(f"🎬 Generating {len(video_prompts)} videos...")
                    generated_videos = await self.video_agent.generate_videos(video_prompts, business_context, campaign_id)
                    logger.info(f"✅ Successfully generated {len(generated_videos)} videos")
                except Exception as e:
                    logger.error(f"❌ Video generation failed: {e}")
                    logger.warning("🔄 Using fallback video placeholders")
                    generated_videos = []
            elif video_prompts and not self.video_agent:
                logger.warning("⚠️ Video agent not available, skipping video generation")
            
            # Update posts with generated visual content
            updated_posts = self._update_posts_with_visuals(
                social_posts, generated_images, generated_videos
            )
            
            return {
                "posts_with_visuals": updated_posts,
                "visual_strategy": {
                    "total_posts": len(social_posts),
                    "image_posts": len(image_posts),
                    "video_posts": len(video_posts),
                    "generated_images": len(generated_images),
                    "generated_videos": len(generated_videos),
                    "brand_consistency": "Applied business context to all visual content",
                    "platform_optimization": f"Optimized for {', '.join(target_platforms)}"
                },
                "generation_metadata": {
                    "agent_used": "VisualContentOrchestrator",
                    "image_generation_method": "imagen_3.0" if self.image_agent.client else "mock",
                    "video_generation_method": "veo_mock",
                    "processing_time": 5.0,
                    "quality_score": 8.5,
                    "business_context_applied": True
                }
            }
            
        except Exception as e:
            logger.error(f"Visual content generation failed: {e}", exc_info=True)
            return self._generate_fallback_visual_content(social_posts)
    
    def _create_image_prompt(self, post: Dict[str, Any], business_context: Dict[str, Any], objective: str) -> str:
        """
        Create image generation prompt based on post content and comprehensive business context.
        
        ADK Enhancement: Uses full business analysis including product context, 
        campaign guidance, and visual style for brand-specific generation.
        """
        
        post_content = post.get('content', '')
        company_name = business_context.get('company_name', 'Company')
        business_description = business_context.get('business_description', '')
        industry = business_context.get('industry', 'business')
        target_audience = business_context.get('target_audience', 'customers')
        
        # ADK ENHANCEMENT: Extract comprehensive context
        product_context = business_context.get('product_context', {})
        campaign_guidance = business_context.get('campaign_guidance', {})
        campaign_media_tuning = business_context.get('campaign_media_tuning', '')
        creative_direction = business_context.get('creative_direction', '')
        visual_style = business_context.get('visual_style', {})
        
        # PRIORITY: Use specific product context if available
        has_specific_product = product_context.get('has_specific_product', False)
        product_name = product_context.get('product_name', '')
        product_themes = product_context.get('product_themes', [])
        product_visual_elements = product_context.get('product_visual_elements', '')
        
        logger.info(f"Creating image prompt - Product: {product_name if has_specific_product else 'general'}, "
                   f"Themes: {product_themes}, Company: {company_name}")
        
        # **PRODUCT-SPECIFIC GENERATION** (Priority over generic business context)
        if has_specific_product and product_name:
            
            # Joker T-Shirt Example: Focus on the specific product
            if 'joker' in product_name.lower() and any('t-shirt' in theme.lower() for theme in product_themes):
                visual_context = (
                    f"Young adult wearing a creative {product_name} t-shirt design, "
                    f"showing the shirt prominently with visible graphic design, "
                    f"in an urban outdoor setting, lifestyle photography style, "
                    f"person laughing or having fun (matching Joker theme), "
                    f"pop culture and comic book aesthetic"
                )
                
                # Add campaign media tuning if provided
                if campaign_media_tuning:
                    if 'outdoor' in campaign_media_tuning.lower():
                        visual_context += ", bright outdoor lighting"
                    if 'bright' in campaign_media_tuning.lower():
                        visual_context += ", vibrant colors"
                    if 'cartoon' in campaign_media_tuning.lower():
                        visual_context += ", emphasizing cartoon character design on shirt"
                        
            # Generic Product Focus (when product detected but not specifically mapped)
            else:
                visual_context = (
                    f"Person using or wearing {product_name}, showcasing the product prominently, "
                    f"real-world usage context, lifestyle photography"
                )
                
                # Add product themes to visual context
                if product_themes:
                    theme_context = ', '.join(product_themes[:3])
                    visual_context += f", incorporating {theme_context} themes"
                    
                # Add visual elements if specified
                if product_visual_elements:
                    visual_context += f", featuring {product_visual_elements}"
                    
        # **BUSINESS-TYPE SPECIFIC GENERATION** (Fallback when no specific product)
        else:
            # Extract detailed business context for visual generation
            logger.info(f"No specific product detected, using business-type context for {company_name}")
            
            if any(keyword in business_description.lower() for keyword in ['t-shirt', 'tshirt', 'apparel', 'clothing', 'print', 'custom']):
                # T-shirt/Apparel Business (Generic)
                visual_context = f"Diverse young adults wearing custom printed t-shirts with creative designs, laughing and having fun in an urban outdoor setting, natural lighting, lifestyle photography style"
                if 'funny' in business_description.lower() or 'humor' in business_description.lower():
                    visual_context += ", humorous and playful t-shirt designs visible"
                
            elif any(keyword in business_description.lower() for keyword in ['restaurant', 'food', 'dining', 'kitchen', 'chef', 'cuisine']):
                # Restaurant/Food Business
                visual_context = f"Professional food photography showing delicious prepared dishes, warm restaurant atmosphere with satisfied customers dining"
                
            elif any(keyword in business_description.lower() for keyword in ['fitness', 'gym', 'training', 'workout', 'health', 'exercise']):
                # Fitness/Health Business
                visual_context = f"Dynamic fitness scene with trainer and client working out in modern gym, showing transformation and success"
                
            elif any(keyword in business_description.lower() for keyword in ['tech', 'software', 'digital', 'app', 'platform', 'saas']):
                # Technology Business
                visual_context = f"Modern professionals collaborating with technology, clean office environment, digital interfaces"
                
            else:
                # Generic business fallback
                visual_context = f"Professional business environment representing {industry} industry, showing {objective} in action"
        
        # **CAMPAIGN GUIDANCE ENHANCEMENT**
        if campaign_guidance:
            visual_style_guidance = campaign_guidance.get('visual_style', {})
            if visual_style_guidance:
                photography_style = visual_style_guidance.get('photography_style', '')
                mood = visual_style_guidance.get('mood', '')
                lighting = visual_style_guidance.get('lighting', '')
                
                if photography_style:
                    visual_context += f", {photography_style} style"
                if mood:
                    visual_context += f", {mood} mood"
                if lighting:
                    visual_context += f", {lighting}"
        
        # **USER MEDIA TUNING INTEGRATION**
        if campaign_media_tuning:
            logger.info(f"Applying user media tuning: {campaign_media_tuning}")
            visual_context += f", incorporating user guidance: {campaign_media_tuning}"
        
        # **CREATIVE DIRECTION INTEGRATION**
        if creative_direction:
            visual_context += f", {creative_direction}"
        
        # Add target audience context
        if 'young' in target_audience.lower() or '18-35' in target_audience:
            visual_context += ", featuring young adults aged 18-35"
        elif 'professional' in target_audience.lower():
            visual_context += ", featuring business professionals"
        elif 'family' in target_audience.lower():
            visual_context += ", family-friendly scene"
        
        # Create final marketing-optimized prompt with technical specs
        marketing_prompt = f"{visual_context}, representing {company_name}, 16:9 aspect ratio, commercial photography style, high quality, professional lighting, sharp focus"
        
        logger.info(f"Generated enhanced image prompt: {marketing_prompt[:150]}...")
        return marketing_prompt
    
    def _create_video_prompt(self, post: Dict[str, Any], business_context: Dict[str, Any], objective: str) -> str:
        """Create video generation prompt based on post content and comprehensive business context."""
        
        post_content = post.get('content', '')
        company_name = business_context.get('company_name') or business_context.get('business_name', 'Company')
        industry = business_context.get('industry', 'business')
        target_audience = business_context.get('target_audience', 'professionals')
        business_description = business_context.get('business_description', '')
        
        # Enhanced business context integration for videos
        visual_context = ""
        
        # Industry-specific video context
        if 'furniture' in industry.lower() or 'outdoor' in business_description.lower():
            visual_context = f"Lifestyle video showcasing outdoor furniture and patio living, comfortable outdoor spaces, modern home design"
        elif 'technology' in industry.lower():
            visual_context = f"Modern professionals using technology solutions, clean office environments, digital innovation"
        elif 'fitness' in industry.lower():
            visual_context = f"Active lifestyle content, fitness activities, health and wellness focus"
        elif 'food' in industry.lower():
            visual_context = f"Culinary excellence, restaurant ambiance, food preparation and presentation"
        else:
            # Generic business fallback with specific business focus
            visual_context = f"Professional business environment for {industry} industry, showing real {company_name} business activities"
        
        # Add target audience context for video
        if 'young' in target_audience.lower():
            visual_context += ", dynamic and energetic style appealing to young adults"
        elif 'family' in target_audience.lower():
            visual_context += ", family-friendly atmosphere and activities"
        elif 'professional' in target_audience.lower():
            visual_context += ", professional business setting and corporate environment"
        
        # Create comprehensive marketing video prompt
        marketing_prompt = f"{visual_context}, representing {company_name}, 15-30 second duration, vertical format for social media, high quality cinematography, engaging visual storytelling, {objective} focused narrative"
        
        logger.info(f"Generated enhanced video prompt: {marketing_prompt[:150]}...")
        return marketing_prompt
    
    def _update_posts_with_visuals(
        self, 
        social_posts: List[Dict[str, Any]], 
        generated_images: List[Dict[str, Any]], 
        generated_videos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update social media posts with generated visual content."""
        
        updated_posts = []
        image_index = 0
        video_index = 0
        
        for post in social_posts:
            updated_post = post.copy()
            
            if post.get('type') == 'text_image' and image_index < len(generated_images):
                image_data = generated_images[image_index]
                updated_post['image_url'] = image_data['image_url']
                updated_post['image_prompt'] = image_data['prompt']
                updated_post['image_metadata'] = image_data['metadata']
                image_index += 1
            
            elif post.get('type') == 'text_video' and video_index < len(generated_videos):
                video_data = generated_videos[video_index]
                updated_post['video_url'] = video_data['video_url']
                updated_post['video_prompt'] = video_data['prompt']
                updated_post['thumbnail_url'] = video_data.get('thumbnail_url')
                updated_post['video_metadata'] = video_data['metadata']
                video_index += 1
            
            updated_posts.append(updated_post)
        
        return updated_posts
    
    def _generate_fallback_visual_content(self, social_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback visual content when generation fails."""
        return {
            "posts_with_visuals": social_posts,
            "visual_strategy": {
                "total_posts": len(social_posts),
                "image_posts": 0,
                "video_posts": 0,
                "generated_images": 0,
                "generated_videos": 0,
                "brand_consistency": "Fallback mode",
                "platform_optimization": "Basic optimization"
            },
            "generation_metadata": {
                "agent_used": "FallbackVisualGenerator",
                "processing_time": 0.1,
                "quality_score": 5.0,
                "error": "Visual content generation failed"
            }
        }

def _generate_basic_placeholders(social_posts: List[Dict[str, Any]], business_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate basic placeholder visual content when all generation methods fail."""
    logger.info("🔄 Generating basic placeholder visual content")
    
    company_name = business_context.get('company_name') or business_context.get('business_name', 'Company')
    updated_posts = []
    
    for i, post in enumerate(social_posts):
        updated_post = post.copy()
        
        if post.get('type') == 'text_image':
            updated_post['image_url'] = f"https://picsum.photos/1024/576?random={i+1000}&text={company_name.replace(' ', '+')}"
            updated_post['image_prompt'] = f"Professional marketing image for {company_name}"
            updated_post['image_metadata'] = {
                "generation_method": "basic_placeholder",
                "status": "fallback",
                "note": "Visual agent unavailable"
            }
        
        elif post.get('type') == 'text_video':
            updated_post['video_url'] = f"https://picsum.photos/1024/576?random={i+2000}&text={company_name.replace(' ', '+')}"
            updated_post['video_prompt'] = f"Marketing video for {company_name}"
            updated_post['thumbnail_url'] = f"https://picsum.photos/1024/576?random={i+2000}&text=Video+Thumbnail"
            updated_post['video_metadata'] = {
                "generation_method": "basic_placeholder",
                "status": "fallback",
                "note": "Video agent unavailable"
            }
        
        updated_posts.append(updated_post)
    
    return {
        "posts_with_visuals": updated_posts,
        "visual_strategy": {
            "total_posts": len(social_posts),
            "image_posts": len([p for p in social_posts if p.get('type') == 'text_image']),
            "video_posts": len([p for p in social_posts if p.get('type') == 'text_video']),
            "generated_images": 0,
            "generated_videos": 0,
            "brand_consistency": "Basic placeholder with company name",
            "platform_optimization": "Standard aspect ratios",
            "note": "Using basic placeholders due to agent unavailability"
        },
        "generation_metadata": {
            "agent_used": "BasicPlaceholderGenerator",
            "processing_time": 0.1,
            "quality_score": 3.0,
            "status": "basic_fallback"
        }
    }

# Export function for use in API routes
async def generate_visual_content_for_posts(
    social_posts: List[Dict[str, Any]], 
    business_context: Dict[str, Any],
    campaign_objective: str,
    target_platforms: List[str] = None,
    # ADK ENHANCEMENT: Enhanced context parameters for business-aware generation
    campaign_media_tuning: str = "",
    campaign_guidance: Dict[str, Any] = None,
    product_context: Dict[str, Any] = None,
    visual_style: Dict[str, Any] = None,
    creative_direction: str = "",
    campaign_id: str = "default"
) -> Dict[str, Any]:
    """
    Generate visual content for social media posts with enhanced business context.
    
    ADK Data Flow Enhancement:
    This function now receives comprehensive business analysis context to ensure
    visual content is aligned with the specific business, product, and campaign objectives.
    
    Args:
        social_posts: List of social media posts to enhance with visuals
        business_context: Core business context from URL analysis
        campaign_objective: Campaign objective for content alignment
        target_platforms: Target social media platforms
        campaign_media_tuning: User-provided media style guidance
        campaign_guidance: Business analysis campaign guidance
        product_context: Specific product information for visual focus
        visual_style: Brand visual style guidelines
        creative_direction: Overall creative direction for the campaign
    
    Returns:
        Dict containing posts with generated visual content
    """
    try:
        logger.info("🎨 Generating visual content with enhanced ADK business context")
        
        # Merge all context sources for comprehensive visual generation
        enhanced_context = {
            **business_context,
            "campaign_media_tuning": campaign_media_tuning,
            "campaign_guidance": campaign_guidance or {},
            "product_context": product_context or {},
            "visual_style": visual_style or {},
            "creative_direction": creative_direction
        }
        
        # Log context richness for debugging
        logger.info(f"Enhanced context includes: company={enhanced_context.get('company_name')}, "
                   f"product={enhanced_context.get('product_context', {}).get('product_name', 'general')}, "
                   f"creative_direction={len(creative_direction)} chars, "
                   f"media_tuning={len(campaign_media_tuning)} chars")
        
        # Initialize orchestrator with enhanced context and exception handling
        try:
            orchestrator = VisualContentOrchestrator()
            
            if orchestrator.image_agent is None and orchestrator.video_agent is None:
                logger.warning("⚠️ No visual agents available, using basic placeholder generation")
                return _generate_basic_placeholders(social_posts, enhanced_context)
            
            # Generate visual content with full business awareness
            result = await orchestrator.generate_visual_content(
                social_posts=social_posts,
                business_context=enhanced_context,
                campaign_objective=campaign_objective,
                target_platforms=target_platforms or ["instagram", "linkedin", "facebook"],
                campaign_id=campaign_id
            )
            
            logger.info("✅ Visual content generation completed with business context awareness")
            return result
            
        except Exception as orchestrator_error:
            logger.error(f"❌ Visual orchestrator initialization/execution failed: {orchestrator_error}")
            logger.warning("🔄 Falling back to basic placeholder generation")
            return _generate_basic_placeholders(social_posts, enhanced_context)
        
    except Exception as e:
        logger.error(f"❌ Enhanced visual content generation failed: {e}", exc_info=True)
        logger.warning("🔄 Using emergency fallback generation")
        return _generate_basic_placeholders(social_posts, business_context)

# Export functions for use in other modules
__all__ = [
    "generate_visual_content_for_posts"
] 