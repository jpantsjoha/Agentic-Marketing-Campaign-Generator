"""
Enhanced Video Generation Agent with Real Veo 2.0 API Integration

This module implements complete video generation using Google's Veo 2.0 API
with asynchronous processing, cloud storage, and comprehensive error handling.

Implements EPIC 15: Complete Video Generation Implementation from TODO.md

Author: JP + 2025-07-14
"""

import os
import json
import asyncio
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

# ADK Framework Imports
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import Gemini

# Google Cloud imports for Veo 2.0 and storage
from google.cloud import storage
from google.cloud import aiplatform
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Configuration
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
VIDEO_MODEL = os.getenv('VIDEO_MODEL', 'veo-2')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
GOOGLE_CLOUD_LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
STORAGE_BUCKET = os.getenv('VIDEO_STORAGE_BUCKET', 'video-venture-launch-videos')

# Video generation configuration
MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', '10'))  # seconds
VIDEO_QUALITY = os.getenv('VIDEO_QUALITY', 'high')
VIDEO_ASPECT_RATIO = os.getenv('VIDEO_ASPECT_RATIO', '16:9')
VIDEO_GENERATION_TIMEOUT = int(os.getenv('VIDEO_GENERATION_TIMEOUT', '180'))  # seconds

class VideoStorageManager:
    """Manages video storage in Google Cloud Storage."""
    
    def __init__(self, bucket_name: str = STORAGE_BUCKET):
        self.bucket_name = bucket_name
        self.client = storage.Client() if GOOGLE_CLOUD_PROJECT else None
        
        if self.client:
            try:
                self.bucket = self.client.bucket(bucket_name)
                logger.info(f"✅ Connected to storage bucket: {bucket_name}")
            except Exception as e:
                logger.error(f"❌ Failed to connect to storage bucket: {e}")
                self.bucket = None
        else:
            self.bucket = None
            logger.warning("⚠️ Google Cloud Storage not configured")
    
    async def upload_video(self, video_content: bytes, filename: str, metadata: Dict[str, Any] = None) -> str:
        """Upload video to cloud storage and return public URL."""
        if not self.bucket:
            logger.error("❌ Storage bucket not available")
            return None
        
        try:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"videos/{timestamp}_{filename}"
            
            # Upload to cloud storage
            blob = self.bucket.blob(unique_filename)
            blob.upload_from_string(video_content, content_type='video/mp4')
            
            # Set metadata
            if metadata:
                blob.metadata = metadata
                blob.patch()
            
            # Make publicly accessible
            blob.make_public()
            
            public_url = blob.public_url
            logger.info(f"✅ Video uploaded successfully: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Failed to upload video: {e}")
            return None
    
    async def cleanup_old_videos(self, max_age_days: int = 30):
        """Clean up videos older than specified days."""
        if not self.bucket:
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            blobs = self.bucket.list_blobs(prefix="videos/")
            deleted_count = 0
            
            for blob in blobs:
                if blob.time_created < cutoff_date:
                    blob.delete()
                    deleted_count += 1
            
            logger.info(f"🗑️ Cleaned up {deleted_count} old videos")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old videos: {e}")

class VideoGenerationQueue:
    """Manages asynchronous video generation queue."""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.active_jobs = {}
        self.completed_jobs = {}
        self.failed_jobs = {}
        self.processing = False
    
    async def add_job(self, job_id: str, prompt: str, metadata: Dict[str, Any]) -> str:
        """Add video generation job to queue."""
        job = {
            'id': job_id,
            'prompt': prompt,
            'metadata': metadata,
            'status': 'queued',
            'created_at': datetime.now(),
            'retries': 0
        }
        
        await self.queue.put(job)
        self.active_jobs[job_id] = job
        
        logger.info(f"📋 Video generation job queued: {job_id}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of video generation job."""
        if job_id in self.completed_jobs:
            return self.completed_jobs[job_id]
        elif job_id in self.failed_jobs:
            return self.failed_jobs[job_id]
        elif job_id in self.active_jobs:
            return self.active_jobs[job_id]
        else:
            return {'status': 'not_found'}
    
    async def start_processing(self):
        """Start processing video generation queue."""
        if self.processing:
            return
        
        self.processing = True
        logger.info("🚀 Started video generation queue processing")
        
        try:
            while self.processing:
                try:
                    # Get next job from queue (wait max 1 second)
                    job = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                    
                    # Process the job
                    await self._process_job(job)
                    
                except asyncio.TimeoutError:
                    # No jobs in queue, continue
                    continue
                except Exception as e:
                    logger.error(f"❌ Error processing video generation queue: {e}")
                    
        finally:
            self.processing = False
            logger.info("🛑 Stopped video generation queue processing")
    
    async def _process_job(self, job: Dict[str, Any]):
        """Process individual video generation job."""
        job_id = job['id']
        
        try:
            job['status'] = 'processing'
            job['started_at'] = datetime.now()
            
            # Generate video using Veo 2.0
            video_url = await self._generate_video_with_veo(job['prompt'], job['metadata'])
            
            if video_url:
                job['status'] = 'completed'
                job['completed_at'] = datetime.now()
                job['video_url'] = video_url
                job['duration'] = (job['completed_at'] - job['started_at']).total_seconds()
                
                # Move to completed jobs
                self.completed_jobs[job_id] = job
                del self.active_jobs[job_id]
                
                logger.info(f"✅ Video generation completed: {job_id}")
                
            else:
                raise Exception("Video generation failed")
                
        except Exception as e:
            logger.error(f"❌ Video generation job failed: {job_id} - {e}")
            
            job['retries'] += 1
            
            if job['retries'] < 3:
                # Retry the job
                job['status'] = 'retry'
                await self.queue.put(job)
                logger.info(f"🔄 Retrying video generation job: {job_id} (attempt {job['retries']})")
            else:
                # Max retries reached, mark as failed
                job['status'] = 'failed'
                job['error'] = str(e)
                job['failed_at'] = datetime.now()
                
                self.failed_jobs[job_id] = job
                del self.active_jobs[job_id]
    
    async def _generate_video_with_veo(self, prompt: str, metadata: Dict[str, Any]) -> str:
        """Generate video using Google Veo 2.0 API."""
        try:
            if not GEMINI_API_KEY:
                logger.error("❌ GEMINI_API_KEY not configured for Veo 2.0")
                return None
            
            # Initialize Gemini client
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Generate video with Veo 2.0
            logger.info(f"🎬 Generating video with Veo 2.0: {prompt[:50]}...")
            
            response = await client.agenerate_video(
                model=VIDEO_MODEL,
                prompt=prompt,
                duration=min(MAX_VIDEO_DURATION, metadata.get('duration', 5)),
                aspect_ratio=VIDEO_ASPECT_RATIO,
                quality=VIDEO_QUALITY
            )
            
            if response and response.video_data:
                # Upload to cloud storage
                storage_manager = VideoStorageManager()
                filename = f"generated_video_{uuid.uuid4().hex[:8]}.mp4"
                
                video_url = await storage_manager.upload_video(
                    video_content=response.video_data,
                    filename=filename,
                    metadata={
                        'prompt': prompt,
                        'model': VIDEO_MODEL,
                        'duration': str(MAX_VIDEO_DURATION),
                        'quality': VIDEO_QUALITY,
                        'generated_at': datetime.now().isoformat()
                    }
                )
                
                return video_url
            else:
                logger.error("❌ No video data received from Veo 2.0")
                return None
                
        except Exception as e:
            logger.error(f"❌ Veo 2.0 video generation failed: {e}")
            return None

class EnhancedVideoGenerationAgent(LlmAgent):
    """Enhanced video generation agent with real Veo 2.0 API integration."""
    
    def __init__(self):
        self.storage_manager = VideoStorageManager()
        self.generation_queue = VideoGenerationQueue()
        
        super().__init__(
            name="EnhancedVideoGenerationAgent",
            model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
            instruction="""You are an expert video generation agent using Google Veo 2.0 API.

Your capabilities:
1. Create compelling video generation prompts from post content
2. Generate high-quality videos using Veo 2.0 API
3. Validate video quality and relevance
4. Handle asynchronous video generation with progress tracking
5. Manage cloud storage for video assets
6. Implement retry logic for failed generations

For each video generation request:
1. Analyze post content and campaign context
2. Create detailed, campaign-aware video prompts
3. Generate videos with appropriate duration and quality
4. Validate generated videos for quality and relevance
5. Store videos in cloud storage with metadata
6. Return video URLs and generation metadata

Always prioritize:
- Brand consistency and campaign alignment
- Professional video quality
- Efficient resource usage
- Error handling and recovery
- User experience optimization""",
            description="Enhanced video generation with real Veo 2.0 API integration"
        )
    
    async def generate_videos_for_posts(
        self, 
        posts: List[Dict[str, Any]], 
        business_context: Dict[str, Any],
        campaign_guidance: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate videos for posts with video prompts."""
        
        video_posts = [post for post in posts if post.get('type') == 'text_video' and post.get('video_prompt')]
        
        if not video_posts:
            logger.info("📹 No video posts found, skipping video generation")
            return {"videos_generated": 0, "results": []}
        
        logger.info(f"🎬 Starting video generation for {len(video_posts)} posts")
        
        # Start queue processing if not already running
        if not self.generation_queue.processing:
            asyncio.create_task(self.generation_queue.start_processing())
        
        generation_results = []
        
        for post in video_posts:
            try:
                # Create enhanced video prompt
                enhanced_prompt = self._create_enhanced_video_prompt(
                    post, business_context, campaign_guidance
                )
                
                # Add to generation queue
                job_id = f"video_{post['id']}_{uuid.uuid4().hex[:8]}"
                
                await self.generation_queue.add_job(
                    job_id=job_id,
                    prompt=enhanced_prompt,
                    metadata={
                        'post_id': post['id'],
                        'business_context': business_context,
                        'campaign_guidance': campaign_guidance,
                        'duration': 5  # Default 5 seconds
                    }
                )
                
                generation_results.append({
                    'post_id': post['id'],
                    'job_id': job_id,
                    'status': 'queued',
                    'prompt': enhanced_prompt
                })
                
            except Exception as e:
                logger.error(f"❌ Failed to queue video generation for post {post['id']}: {e}")
                generation_results.append({
                    'post_id': post['id'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"✅ Video generation queued for {len(generation_results)} posts")
        
        return {
            "videos_generated": len(generation_results),
            "results": generation_results,
            "queue_status": "processing"
        }
    
    def _create_enhanced_video_prompt(
        self, 
        post: Dict[str, Any], 
        business_context: Dict[str, Any],
        campaign_guidance: Dict[str, Any] = None
    ) -> str:
        """Create enhanced video prompt with campaign context."""
        
        base_prompt = post.get('video_prompt', '')
        company_name = business_context.get('company_name', 'Company')
        industry = business_context.get('industry', 'Business')
        brand_voice = business_context.get('brand_voice', 'professional')
        
        # Create campaign-aware video prompt
        enhanced_prompt = f"""
        Create a {MAX_VIDEO_DURATION}-second professional marketing video for {company_name} in the {industry} industry.
        
        Base concept: {base_prompt}
        
        Video requirements:
        - Duration: {MAX_VIDEO_DURATION} seconds maximum
        - Style: {brand_voice} and engaging
        - Quality: High-definition, professional
        - Aspect ratio: {VIDEO_ASPECT_RATIO}
        - No text overlays or captions needed
        
        Content guidance:
        - Focus on visual storytelling
        - Showcase {company_name}'s brand personality
        - Appeal to target audience: {business_context.get('target_audience', 'general audience')}
        - Align with campaign objective: {campaign_guidance.get('objective', 'brand awareness') if campaign_guidance else 'brand awareness'}
        
        Visual elements to include:
        - Professional lighting and composition
        - Smooth camera movements
        - Relevant props and settings for {industry}
        - Brand colors and style if applicable
        
        Avoid:
        - Low-quality or blurry footage
        - Inappropriate or off-brand content
        - Excessive text or overlays
        - Jarring transitions or cuts
        """
        
        return enhanced_prompt.strip()
    
    async def get_video_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of video generation job."""
        return await self.generation_queue.get_job_status(job_id)
    
    async def get_completed_videos(self, post_ids: List[str]) -> Dict[str, Any]:
        """Get completed videos for specific posts."""
        completed_videos = {}
        
        for post_id in post_ids:
            # Find jobs for this post
            for job_id, job in self.generation_queue.completed_jobs.items():
                if job['metadata'].get('post_id') == post_id:
                    completed_videos[post_id] = {
                        'video_url': job['video_url'],
                        'duration': job['duration'],
                        'completed_at': job['completed_at'].isoformat(),
                        'job_id': job_id
                    }
                    break
        
        return completed_videos
    
    async def cleanup_old_videos(self, max_age_days: int = 30):
        """Clean up old videos from storage."""
        await self.storage_manager.cleanup_old_videos(max_age_days)

# Factory function
async def create_enhanced_video_generation_agent() -> EnhancedVideoGenerationAgent:
    """Create an enhanced video generation agent instance."""
    return EnhancedVideoGenerationAgent()

# Backward compatibility function
async def generate_videos_for_posts(
    posts: List[Dict[str, Any]], 
    business_context: Dict[str, Any],
    campaign_guidance: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate videos for posts with backward compatibility."""
    agent = await create_enhanced_video_generation_agent()
    return await agent.generate_videos_for_posts(posts, business_context, campaign_guidance)