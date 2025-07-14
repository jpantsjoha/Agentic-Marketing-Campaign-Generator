"""
Enhanced Image Generation Agent with Real Imagen 3.0 API Integration

This module implements complete image generation using Google's Imagen 3.0 API
with batch processing, intelligent timeout handling, and cost control.

Implements EPIC 17: Complete Image Generation Implementation from TODO.md

Author: JP + 2025-07-14
"""

import os
import json
import asyncio
import logging
import time
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ADK Framework Imports
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import Gemini

# Google Cloud imports for Imagen 3.0
from google.cloud import storage
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Configuration
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'imagen-3.0-generate-002')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
STORAGE_BUCKET = os.getenv('IMAGE_STORAGE_BUCKET', 'video-venture-launch-images')

# Image generation configuration
IMAGE_GENERATION_TIMEOUT = int(os.getenv('IMAGE_GENERATION_TIMEOUT', '30'))  # seconds
MAX_CONCURRENT_IMAGES = int(os.getenv('MAX_CONCURRENT_IMAGES', '5'))
IMAGE_QUALITY = os.getenv('IMAGE_QUALITY', 'high')
IMAGE_ASPECT_RATIO = os.getenv('IMAGE_ASPECT_RATIO', '1:1')
DAILY_IMAGE_LIMIT = int(os.getenv('DAILY_IMAGE_LIMIT', '100'))

# Circuit breaker configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv('CIRCUIT_BREAKER_FAILURE_THRESHOLD', '5'))
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.getenv('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', '300'))  # 5 minutes

class ImageGenerationCircuitBreaker:
    """Circuit breaker pattern for image generation API failures."""
    
    def __init__(self, failure_threshold: int = CIRCUIT_BREAKER_FAILURE_THRESHOLD, recovery_timeout: int = CIRCUIT_BREAKER_RECOVERY_TIMEOUT):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if we can execute the operation."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        return False
    
    def record_success(self):
        """Record successful operation."""
        self.failure_count = 0
        self.state = "CLOSED"
        logger.info("🔄 Circuit breaker reset to CLOSED state")
    
    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"🔴 Circuit breaker OPEN - too many failures ({self.failure_count})")
        
        logger.warning(f"⚠️ Circuit breaker failure recorded ({self.failure_count}/{self.failure_threshold})")

class ImageGenerationCostController:
    """Controls daily image generation costs and limits."""
    
    def __init__(self, daily_limit: int = DAILY_IMAGE_LIMIT):
        self.daily_limit = daily_limit
        self.current_date = datetime.now().date()
        self.daily_count = 0
        self.cost_per_image = 0.05  # Estimated cost per image
        self.daily_cost = 0.0
    
    def can_generate_image(self) -> bool:
        """Check if we can generate another image today."""
        today = datetime.now().date()
        
        # Reset counter if it's a new day
        if today != self.current_date:
            self.current_date = today
            self.daily_count = 0
            self.daily_cost = 0.0
        
        return self.daily_count < self.daily_limit
    
    def record_image_generation(self):
        """Record that an image was generated."""
        self.daily_count += 1
        self.daily_cost += self.cost_per_image
        
        if self.daily_count % 10 == 0:  # Log every 10 images
            logger.info(f"💰 Daily image generation: {self.daily_count}/{self.daily_limit} (${self.daily_cost:.2f})")
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily generation statistics."""
        return {
            "date": self.current_date.isoformat(),
            "images_generated": self.daily_count,
            "daily_limit": self.daily_limit,
            "estimated_cost": self.daily_cost,
            "remaining_quota": self.daily_limit - self.daily_count
        }

class ImageCacheManager:
    """Manages intelligent image caching with smart invalidation."""
    
    def __init__(self, cache_dir: str = "data/images/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_index = {}
        self.load_cache_index()
    
    def load_cache_index(self):
        """Load cache index from disk."""
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self.cache_index = json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load cache index: {e}")
                self.cache_index = {}
    
    def save_cache_index(self):
        """Save cache index to disk."""
        index_file = self.cache_dir / "cache_index.json"
        try:
            with open(index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save cache index: {e}")
    
    def get_cache_key(self, prompt: str, business_context: Dict[str, Any]) -> str:
        """Generate cache key from prompt and business context."""
        cache_content = f"{prompt}_{business_context.get('company_name', '')}_{business_context.get('industry', '')}"
        return hashlib.md5(cache_content.encode()).hexdigest()
    
    def get_cached_image(self, prompt: str, business_context: Dict[str, Any]) -> Optional[str]:
        """Get cached image URL if available and valid."""
        cache_key = self.get_cache_key(prompt, business_context)
        
        if cache_key in self.cache_index:
            cache_entry = self.cache_index[cache_key]
            
            # Check if cache is still valid (24 hours)
            cache_time = datetime.fromisoformat(cache_entry['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=24):
                logger.info(f"✅ Cache hit for image: {prompt[:50]}...")
                return cache_entry['image_url']
            else:
                # Remove expired cache entry
                del self.cache_index[cache_key]
                self.save_cache_index()
        
        return None
    
    def cache_image(self, prompt: str, business_context: Dict[str, Any], image_url: str):
        """Cache image URL with metadata."""
        cache_key = self.get_cache_key(prompt, business_context)
        
        self.cache_index[cache_key] = {
            'prompt': prompt,
            'business_context': business_context,
            'image_url': image_url,
            'timestamp': datetime.now().isoformat()
        }
        
        self.save_cache_index()
        logger.info(f"💾 Image cached: {prompt[:50]}...")
    
    def cleanup_expired_cache(self):
        """Remove expired cache entries."""
        expired_keys = []
        
        for key, entry in self.cache_index.items():
            cache_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cache_time > timedelta(hours=24):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache_index[key]
        
        if expired_keys:
            self.save_cache_index()
            logger.info(f"🗑️ Cleaned up {len(expired_keys)} expired cache entries")

class EnhancedImageGenerationAgent(LlmAgent):
    """Enhanced image generation agent with real Imagen 3.0 API integration."""
    
    def __init__(self):
        super().__init__(
            name="EnhancedImageGenerationAgent",
            model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
            instruction="""You are an expert image generation agent using Google Imagen 3.0 API.

Your capabilities:
1. Create compelling image generation prompts from post content
2. Generate high-quality images using Imagen 3.0 API
3. Implement batch processing for multiple images
4. Use intelligent caching to avoid redundant generations
5. Apply circuit breaker pattern for API failure handling
6. Control costs with daily limits and monitoring
7. Validate image quality and relevance

For each image generation request:
1. Check cache for existing similar images
2. Validate daily limits and API availability
3. Create detailed, campaign-aware image prompts
4. Generate images with timeout handling
5. Validate generated images for quality
6. Cache successful generations
7. Return image URLs with metadata

Always prioritize:
- Cost efficiency and resource optimization
- High-quality, relevant image generation
- Brand consistency and campaign alignment
- Robust error handling and recovery
- User experience optimization""",
            description="Enhanced image generation with real Imagen 3.0 API integration"
        )
        
        self._circuit_breaker = ImageGenerationCircuitBreaker()
        self._cost_controller = ImageGenerationCostController()
        self._cache_manager = ImageCacheManager()
        self._storage_client = storage.Client() if GOOGLE_CLOUD_PROJECT else None
    
    @property
    def circuit_breaker(self) -> ImageGenerationCircuitBreaker:
        """Get circuit breaker."""
        return self._circuit_breaker
    
    @property
    def cost_controller(self) -> ImageGenerationCostController:
        """Get cost controller."""
        return self._cost_controller
    
    @property
    def cache_manager(self) -> ImageCacheManager:
        """Get cache manager."""
        return self._cache_manager
    
    async def generate_images_batch(self, prompts: List[str], business_context: Dict[str, Any], campaign_guidance: Dict[str, Any] = None) -> List[Optional[str]]:
        """Generate multiple images concurrently with timeout handling."""
        
        if not prompts:
            return []
        
        logger.info(f"🖼️ Starting batch image generation for {len(prompts)} prompts")
        
        # Check circuit breaker
        if not self._circuit_breaker.can_execute():
            logger.error("🔴 Circuit breaker is OPEN - skipping image generation")
            return [None] * len(prompts)
        
        # Check cost limits
        if not self._cost_controller.can_generate_image():
            logger.warning("💰 Daily image generation limit reached")
            return [None] * len(prompts)
        
        # Clean up expired cache
        self._cache_manager.cleanup_expired_cache()
        
        # Prepare tasks for batch processing
        tasks = []
        for i, prompt in enumerate(prompts):
            task = self._generate_single_image_with_timeout(
                prompt=prompt,
                business_context=business_context,
                campaign_guidance=campaign_guidance,
                timeout=IMAGE_GENERATION_TIMEOUT
            )
            tasks.append(task)
        
        # Execute batch with concurrency limit
        results = []
        
        # Process in batches to avoid overwhelming the API
        batch_size = min(MAX_CONCURRENT_IMAGES, len(tasks))
        
        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Image generation failed: {result}")
                    results.append(None)
                    self._circuit_breaker.record_failure()
                else:
                    results.append(result)
                    if result:
                        self._circuit_breaker.record_success()
                        self._cost_controller.record_image_generation()
        
        success_count = sum(1 for r in results if r is not None)
        logger.info(f"✅ Batch image generation completed: {success_count}/{len(prompts)} successful")
        
        return results
    
    async def _generate_single_image_with_timeout(
        self, 
        prompt: str, 
        business_context: Dict[str, Any],
        campaign_guidance: Dict[str, Any] = None,
        timeout: int = IMAGE_GENERATION_TIMEOUT
    ) -> Optional[str]:
        """Generate a single image with timeout handling."""
        
        try:
            # Check cache first
            cached_url = self._cache_manager.get_cached_image(prompt, business_context)
            if cached_url:
                return cached_url
            
            # Create enhanced prompt
            enhanced_prompt = self._create_enhanced_image_prompt(
                prompt, business_context, campaign_guidance
            )
            
            # Generate image with timeout
            image_url = await asyncio.wait_for(
                self._generate_image_with_imagen(enhanced_prompt),
                timeout=timeout
            )
            
            if image_url:
                # Cache successful generation
                self._cache_manager.cache_image(prompt, business_context, image_url)
                
                logger.info(f"✅ Image generated successfully: {prompt[:50]}...")
                return image_url
            else:
                logger.warning(f"⚠️ Image generation returned no result: {prompt[:50]}...")
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"⏰ Image generation timeout ({timeout}s): {prompt[:50]}...")
            return None
        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            return None
    
    async def _generate_image_with_imagen(self, prompt: str) -> Optional[str]:
        """Generate image using Google Imagen 3.0 API."""
        
        if not GEMINI_API_KEY:
            logger.error("❌ GEMINI_API_KEY not configured for Imagen 3.0")
            return None
        
        try:
            # Initialize Gemini client
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            logger.info(f"🎨 Generating image with Imagen 3.0: {prompt[:50]}...")
            
            # Generate image
            response = await client.agenerate_images(
                model=IMAGE_MODEL,
                prompt=prompt,
                number_of_images=1,
                aspect_ratio=IMAGE_ASPECT_RATIO,
                quality=IMAGE_QUALITY,
                safety_filter_level="block_few"
            )
            
            if response and response.images:
                # Get the first (and only) image
                image = response.images[0]
                
                # Upload to cloud storage if available
                if self._storage_client:
                    image_url = await self._upload_image_to_storage(image.image_data, prompt)
                    return image_url
                else:
                    # Return base64 data URL as fallback
                    return f"data:image/png;base64,{image.image_data}"
            else:
                logger.error("❌ No images received from Imagen 3.0")
                return None
                
        except Exception as e:
            logger.error(f"❌ Imagen 3.0 image generation failed: {e}")
            return None
    
    async def _upload_image_to_storage(self, image_data: bytes, prompt: str) -> str:
        """Upload image to cloud storage and return public URL."""
        
        try:
            bucket = self._storage_client.bucket(STORAGE_BUCKET)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"images/{timestamp}_{uuid.uuid4().hex[:8]}.png"
            
            # Upload to storage
            blob = bucket.blob(filename)
            blob.upload_from_string(image_data, content_type='image/png')
            
            # Set metadata
            blob.metadata = {
                'prompt': prompt[:500],  # Limit metadata size
                'model': IMAGE_MODEL,
                'generated_at': datetime.now().isoformat(),
                'aspect_ratio': IMAGE_ASPECT_RATIO,
                'quality': IMAGE_QUALITY
            }
            blob.patch()
            
            # Make publicly accessible
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"❌ Failed to upload image to storage: {e}")
            return None
    
    def _create_enhanced_image_prompt(
        self, 
        base_prompt: str, 
        business_context: Dict[str, Any],
        campaign_guidance: Dict[str, Any] = None
    ) -> str:
        """Create enhanced image prompt with campaign context."""
        
        company_name = business_context.get('company_name', 'Company')
        industry = business_context.get('industry', 'Business')
        brand_voice = business_context.get('brand_voice', 'professional')
        
        # Create campaign-aware image prompt
        enhanced_prompt = f"""
        Create a high-quality, professional marketing image for {company_name} in the {industry} industry.
        
        Base concept: {base_prompt}
        
        Visual requirements:
        - Style: {brand_voice}, modern, and visually appealing
        - Quality: High-resolution, sharp, and professional
        - Composition: Well-balanced, engaging, and suitable for social media
        - Colors: Cohesive color palette that matches brand aesthetic
        - Lighting: Professional lighting that enhances the subject
        
        Content guidance:
        - Showcase {company_name}'s brand personality
        - Appeal to target audience: {business_context.get('target_audience', 'general audience')}
        - Align with campaign objective: {campaign_guidance.get('objective', 'brand awareness') if campaign_guidance else 'brand awareness'}
        - Reflect {industry} industry standards and expectations
        
        Visual elements to include:
        - Professional photography or illustration style
        - Relevant props, settings, or backgrounds for {industry}
        - People or products that represent the target audience
        - Brand-appropriate mood and atmosphere
        
        Avoid:
        - Text overlays or captions
        - Low-quality or pixelated imagery
        - Inappropriate or off-brand content
        - Cluttered or confusing compositions
        - Overly busy or distracting backgrounds
        """
        
        return enhanced_prompt.strip()
    
    async def generate_images_for_posts(
        self, 
        posts: List[Dict[str, Any]], 
        business_context: Dict[str, Any],
        campaign_guidance: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate images for posts with image prompts."""
        
        image_posts = [post for post in posts if post.get('type') == 'text_image' and post.get('image_prompt')]
        
        if not image_posts:
            logger.info("🖼️ No image posts found, skipping image generation")
            return {"images_generated": 0, "results": []}
        
        logger.info(f"🎨 Starting image generation for {len(image_posts)} posts")
        
        # Extract prompts
        prompts = [post['image_prompt'] for post in image_posts]
        
        # Generate images in batch
        image_urls = await self.generate_images_batch(prompts, business_context, campaign_guidance)
        
        # Update posts with image URLs
        results = []
        for post, image_url in zip(image_posts, image_urls):
            if image_url:
                post['image_url'] = image_url
                results.append({
                    'post_id': post['id'],
                    'status': 'success',
                    'image_url': image_url
                })
            else:
                results.append({
                    'post_id': post['id'],
                    'status': 'failed',
                    'error': 'Image generation failed'
                })
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"✅ Image generation completed: {success_count}/{len(image_posts)} successful")
        
        return {
            "images_generated": success_count,
            "results": results,
            "cost_stats": self._cost_controller.get_daily_stats()
        }
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get current generation statistics."""
        return {
            "cost_stats": self._cost_controller.get_daily_stats(),
            "circuit_breaker_state": self._circuit_breaker.state,
            "circuit_breaker_failures": self._circuit_breaker.failure_count
        }

# Factory function
async def create_enhanced_image_generation_agent() -> EnhancedImageGenerationAgent:
    """Create an enhanced image generation agent instance."""
    return EnhancedImageGenerationAgent()

# Backward compatibility function
async def generate_images_for_posts(
    posts: List[Dict[str, Any]], 
    business_context: Dict[str, Any],
    campaign_guidance: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate images for posts with backward compatibility."""
    agent = await create_enhanced_image_generation_agent()
    return await agent.generate_images_for_posts(posts, business_context, campaign_guidance)