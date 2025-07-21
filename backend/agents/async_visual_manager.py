"""
FILENAME: async_visual_manager.py  
DESCRIPTION/PURPOSE: Async visual content generation manager with job tracking and progress monitoring
Author: JP + 2025-06-28

This module provides async visual content generation capabilities with:
- Background processing for images and videos
- Real-time progress tracking
- Job status management
- File system monitoring
- Progressive UI updates support
"""

import asyncio
import uuid
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json

from ..api.models import VisualGenerationJob, VisualJobStatus, VisualContentType, BatchVisualStatus

logger = logging.getLogger(__name__)

@dataclass
class JobProgress:
    """Progress tracking for visual generation jobs"""
    job_id: str
    current_step: str = "queued"
    progress: float = 0.0
    estimated_completion: Optional[datetime] = None
    last_update: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AsyncVisualManager:
    """
    Manages async visual content generation with progressive loading support.
    
    Features:
    - Background job processing
    - Real-time progress tracking
    - File system monitoring
    - Campaign-aware job management
    - Progressive UI update support
    """
    
    def __init__(self):
        self.jobs: Dict[str, VisualGenerationJob] = {}
        self.job_progress: Dict[str, JobProgress] = {}
        self.processing_queue = asyncio.Queue()
        self.active_workers = 0
        self.max_workers = 2  # Limit concurrent generation for resource management
        self.is_running = False
        self.campaign_jobs: Dict[str, List[str]] = {}  # campaign_id -> [job_ids]
        
        # Performance estimates (in seconds)
        self.generation_estimates = {
            VisualContentType.IMAGE: 45,  # Imagen API average
            VisualContentType.VIDEO: 120  # Veo API average
        }
        
        logger.info("✅ AsyncVisualManager initialized")
    
    async def start_workers(self):
        """Start background worker tasks for processing visual generation jobs"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info(f"🚀 Starting {self.max_workers} async visual generation workers")
        
        # Start worker tasks
        for i in range(self.max_workers):
            asyncio.create_task(self._worker(f"worker-{i+1}"))
            
        logger.info("✅ Async visual generation workers started")
    
    async def stop_workers(self):
        """Stop all background workers"""
        self.is_running = False
        logger.info("🛑 Stopping async visual generation workers")
    
    async def queue_visual_generation(
        self,
        campaign_id: str,
        posts: List[Dict[str, Any]],
        business_context: Dict[str, Any],
        campaign_objective: str
    ) -> List[VisualGenerationJob]:
        """
        Queue visual content generation jobs for multiple posts.
        Returns immediately with job information for tracking.
        """
        jobs = []
        
        for post in posts:
            post_id = post.get('id', f"post_{int(time.time())}")
            post_type = post.get('type', 'text_image')
            
            # Create jobs based on post type
            if post_type in ['text_image', 'text_video']:
                content_types = []
                if post_type == 'text_image':
                    content_types.append(VisualContentType.IMAGE)
                elif post_type == 'text_video':
                    content_types.extend([VisualContentType.IMAGE, VisualContentType.VIDEO])
                
                for content_type in content_types:
                    job = self._create_visual_job(
                        campaign_id=campaign_id,
                        post_id=post_id,
                        post_content=post,
                        content_type=content_type,
                        business_context=business_context,
                        campaign_objective=campaign_objective
                    )
                    
                    jobs.append(job)
                    await self.processing_queue.put(job.job_id)
                    
                    logger.info(f"📋 Queued {content_type.value} generation job: {job.job_id}")
        
        # Track jobs by campaign
        if campaign_id not in self.campaign_jobs:
            self.campaign_jobs[campaign_id] = []
        self.campaign_jobs[campaign_id].extend([job.job_id for job in jobs])
        
        logger.info(f"✅ Queued {len(jobs)} visual generation jobs for campaign {campaign_id}")
        return jobs
    
    def _create_visual_job(
        self,
        campaign_id: str,
        post_id: str,
        post_content: Dict[str, Any],
        content_type: VisualContentType,
        business_context: Dict[str, Any],
        campaign_objective: str
    ) -> VisualGenerationJob:
        """Create a new visual generation job"""
        job_id = f"{content_type.value}_{campaign_id}_{post_id}_{uuid.uuid4().hex[:8]}"
        
        # Create generation prompt based on content type
        if content_type == VisualContentType.IMAGE:
            prompt = self._create_image_prompt(post_content, business_context, campaign_objective)
        else:  # VIDEO
            prompt = self._create_video_prompt(post_content, business_context, campaign_objective)
        
        job = VisualGenerationJob(
            job_id=job_id,
            campaign_id=campaign_id,
            post_id=post_id,
            content_type=content_type,
            prompt=prompt,
            status=VisualJobStatus.QUEUED,
            estimated_completion_seconds=self.generation_estimates[content_type],
            metadata={
                'business_context': business_context,
                'campaign_objective': campaign_objective,
                'post_content': post_content
            }
        )
        
        self.jobs[job_id] = job
        self.job_progress[job_id] = JobProgress(job_id=job_id)
        
        return job
    
    def _create_image_prompt(self, post: Dict[str, Any], business_context: Dict[str, Any], objective: str) -> str:
        """Create business-contextual image generation prompt"""
        content = post.get('content', '')
        company_name = business_context.get('company_name', 'Company')
        business_description = business_context.get('business_description', '')
        
        # Detect business industry for contextual prompts
        industry = self._detect_business_industry(business_description)
        
        # Create industry-specific visual prompt
        if industry == 'Photography':
            prompt = f"Professional photography portfolio image showcasing {company_name}'s photography services and artistic style. "
            prompt += f"High-quality camera equipment, beautiful composition, behind-the-scenes photographer work, "
            prompt += f"elegant studio lighting or natural outdoor photography setting. "
            prompt += f"Context: {content[:150]} - Style: Professional, artistic, high-end photography aesthetic. "
            prompt += f"NO TEXT OVERLAYS or written words in the image."
        elif industry == 'Food':
            prompt = f"Appetizing food photography for {company_name} restaurant/catering business. "
            prompt += f"Beautiful plated dishes, fresh ingredients, elegant presentation, warm restaurant ambiance. "
            prompt += f"Context: {content[:150]} - Style: Food photography, mouth-watering, professional culinary presentation."
        elif industry == 'Fitness':
            prompt = f"Dynamic fitness and wellness imagery for {company_name}. "
            prompt += f"Athletic equipment, gym environment, healthy lifestyle, energetic workout scenes. "
            prompt += f"Context: {content[:150]} - Style: Motivational, energetic, health-focused."
        elif industry == 'Tech':
            prompt = f"Modern technology and innovation imagery for {company_name}. "
            prompt += f"Clean minimalist design, digital interfaces, professional tech environment. "
            prompt += f"Context: {content[:150]} - Style: Modern, sleek, innovative technology aesthetic."
        elif industry == 'Art':
            prompt = f"Creative artistic imagery showcasing {company_name}'s artistic work and studio. "
            prompt += f"Art supplies, creative workspace, artistic compositions, gallery-worthy presentation. "
            prompt += f"Context: {content[:150]} - Style: Creative, artistic, inspiring aesthetic."
        else:
            # Generic professional business prompt
            prompt = f"Professional business marketing image for {company_name}. "
            prompt += f"Clean, modern business environment appropriate for their industry. "
            prompt += f"Context: {content[:150]} - Style: Professional, trustworthy, business-focused."
        
        return prompt
    
    def _create_video_prompt(self, post: Dict[str, Any], business_context: Dict[str, Any], objective: str) -> str:
        """Create business-contextual video generation prompt"""
        content = post.get('content', '')
        company_name = business_context.get('company_name', 'Company')
        business_description = business_context.get('business_description', '')
        
        # Detect business industry for contextual prompts
        industry = self._detect_business_industry(business_description)
        
        # Create industry-specific video prompt
        if industry == 'Photography':
            prompt = f"Professional photography showcase video for {company_name}. "
            prompt += f"Behind-the-scenes photographer at work, capturing beautiful moments, professional camera equipment in action, "
            prompt += f"elegant photo shoot environment, artistic composition techniques, natural lighting or studio setup. "
            prompt += f"Context: {content[:150]} - Style: Cinematic, professional, showcasing photography expertise and artistic vision."
        elif industry == 'Food':
            prompt = f"Appetizing food preparation video for {company_name} restaurant/catering. "
            prompt += f"Chef preparing dishes, fresh ingredients, cooking process, beautiful food presentation. "
            prompt += f"Context: {content[:150]} - Style: Mouth-watering, professional culinary cinematography."
        elif industry == 'Fitness':
            prompt = f"Dynamic fitness and wellness video for {company_name}. "
            prompt += f"Energetic workout routines, gym environment, health and wellness activities, motivational fitness scenes. "
            prompt += f"Context: {content[:150]} - Style: High-energy, motivational, fitness-focused."
        elif industry == 'Tech':
            prompt = f"Modern technology showcase video for {company_name}. "
            prompt += f"Clean tech environment, innovative solutions in action, professional digital workspace, modern interfaces. "
            prompt += f"Context: {content[:150]} - Style: Sleek, modern, technology-focused cinematography."
        elif industry == 'Art':
            prompt = f"Creative artistic process video for {company_name}. "
            prompt += f"Artist at work, creative process, art creation, studio environment, artistic techniques. "
            prompt += f"Context: {content[:150]} - Style: Creative, inspiring, artistic cinematography."
        else:
            # Generic professional business prompt
            prompt = f"Professional business showcase video for {company_name}. "
            prompt += f"Modern business environment, professional services in action, clean corporate setting. "
            prompt += f"Context: {content[:150]} - Style: Professional, trustworthy, business-focused."
        
        return prompt
    
    def _detect_business_industry(self, business_description: str) -> str:
        """Detect business industry from description for contextual visual prompts"""
        description = business_description.lower()
        
        # Industry detection patterns
        industry_patterns = {
            'Photography': ['photography', 'photographer', 'photo', 'wedding', 'portrait', 'studio', 'headshot', 'commercial photography', 'event photography'],
            'Food': ['restaurant', 'catering', 'food', 'chef', 'cuisine', 'dining', 'bakery', 'cafe', 'culinary', 'kitchen'],
            'Fitness': ['fitness', 'gym', 'personal trainer', 'workout', 'exercise', 'wellness', 'health', 'yoga', 'pilates', 'crossfit'],
            'Tech': ['technology', 'software', 'developer', 'app', 'digital', 'IT', 'coding', 'programming', 'startup', 'saas'],
            'Art': ['artist', 'art', 'creative', 'design', 'gallery', 'artwork', 'painting', 'sculpture', 'illustration', 'graphic design'],
            'Fashion': ['fashion', 'clothing', 'apparel', 'boutique', 'style', 'designer', 'retail', 'accessories', 'jewelry'],
            'Consulting': ['consulting', 'consultant', 'advisory', 'business coach', 'strategy', 'professional services', 'coaching']
        }
        
        # Check for industry patterns
        for industry, patterns in industry_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in description)
            if matches >= 1:  # At least one match
                logger.info(f"🎯 Detected '{industry}' industry from business description")
                return industry
        
        logger.info("🔍 No specific industry detected, using generic business context")
        return 'Generic'
    
    async def _worker(self, worker_name: str):
        """Background worker for processing visual generation jobs"""
        logger.info(f"🔄 Worker {worker_name} started")
        
        while self.is_running:
            try:
                # Get next job from queue (with timeout to check if should stop)
                try:
                    job_id = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                if job_id not in self.jobs:
                    logger.warning(f"⚠️ Job {job_id} not found, skipping")
                    continue
                
                job = self.jobs[job_id]
                logger.info(f"🎨 Worker {worker_name} processing job: {job_id} ({job.content_type.value})")
                
                await self._process_visual_job(job, worker_name)
                
            except Exception as e:
                logger.error(f"❌ Worker {worker_name} error: {e}", exc_info=True)
                if 'job_id' in locals() and job_id in self.jobs:
                    await self._mark_job_failed(job_id, str(e))
        
        logger.info(f"🛑 Worker {worker_name} stopped")
    
    async def _process_visual_job(self, job: VisualGenerationJob, worker_name: str):
        """Process a single visual generation job with progress tracking"""
        job_id = job.job_id
        
        try:
            # Mark job as processing
            await self._update_job_status(job_id, VisualJobStatus.PROCESSING, 0.1)
            
            if job.content_type == VisualContentType.IMAGE:
                result = await self._generate_image_async(job, worker_name)
            else:  # VIDEO
                result = await self._generate_video_async(job, worker_name)
            
            if result.get('success'):
                await self._mark_job_completed(job_id, result)
                logger.info(f"✅ Job {job_id} completed successfully")
            else:
                await self._mark_job_failed(job_id, result.get('error', 'Unknown error'))
                logger.error(f"❌ Job {job_id} failed: {result.get('error')}")
                
        except Exception as e:
            await self._mark_job_failed(job_id, str(e))
            logger.error(f"❌ Job {job_id} processing failed: {e}", exc_info=True)
    
    async def _generate_image_async(self, job: VisualGenerationJob, worker_name: str) -> Dict[str, Any]:
        """Generate image with progress tracking"""
        try:
            # Import here to avoid circular imports
            from .visual_content_agent import ImageGenerationAgent
            
            await self._update_job_progress(job.job_id, 0.3, "Initializing image generation...")
            
            # Create image generation agent
            agent = ImageGenerationAgent()
            
            await self._update_job_progress(job.job_id, 0.5, "Generating image with Imagen API...")
            
            # Generate image using existing logic
            results = await agent.generate_images(
                [job.prompt], 
                job.metadata['business_context'], 
                job.campaign_id
            )
            
            await self._update_job_progress(job.job_id, 0.9, "Saving image file...")
            
            if results and len(results) > 0 and results[0].get('image_url'):
                result_url = results[0]['image_url']
                
                await self._update_job_progress(job.job_id, 1.0, "Image generation complete!")
                
                return {
                    'success': True,
                    'result_url': result_url,
                    'metadata': results[0].get('metadata', {})
                }
            else:
                return {
                    'success': False,
                    'error': 'Image generation failed - no result URL'
                }
                
        except Exception as e:
            logger.error(f"Image generation error for job {job.job_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_video_async(self, job: VisualGenerationJob, worker_name: str) -> Dict[str, Any]:
        """Generate video with progress tracking"""
        try:
            # Import here to avoid circular imports
            from .visual_content_agent import VideoGenerationAgent
            
            await self._update_job_progress(job.job_id, 0.2, "Initializing video generation...")
            
            # Create video generation agent
            agent = VideoGenerationAgent()
            
            await self._update_job_progress(job.job_id, 0.4, "Generating video with Veo API...")
            
            # Generate video using existing logic
            results = await agent.generate_videos(
                [job.prompt], 
                job.metadata['business_context'], 
                job.campaign_id
            )
            
            await self._update_job_progress(job.job_id, 0.8, "Processing video file...")
            
            if results and len(results) > 0 and results[0].get('video_url'):
                result_url = results[0]['video_url']
                
                await self._update_job_progress(job.job_id, 1.0, "Video generation complete!")
                
                return {
                    'success': True,
                    'result_url': result_url,
                    'metadata': results[0].get('metadata', {})
                }
            else:
                return {
                    'success': False,
                    'error': 'Video generation failed - no result URL'
                }
                
        except Exception as e:
            logger.error(f"Video generation error for job {job.job_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _update_job_status(self, job_id: str, status: VisualJobStatus, progress: float = None):
        """Update job status and optionally progress"""
        if job_id not in self.jobs:
            return
            
        job = self.jobs[job_id]
        job.status = status
        
        if progress is not None:
            job.progress = progress
            
        if status == VisualJobStatus.PROCESSING and not job.started_at:
            job.started_at = datetime.now()
        elif status in [VisualJobStatus.COMPLETED, VisualJobStatus.FAILED]:
            job.completed_at = datetime.now()
            
        logger.debug(f"📊 Job {job_id} status: {status.value} ({progress*100:.0f}%)")
    
    async def _update_job_progress(self, job_id: str, progress: float, step: str):
        """Update job progress with detailed step information"""
        if job_id in self.job_progress:
            self.job_progress[job_id].progress = progress
            self.job_progress[job_id].current_step = step
            self.job_progress[job_id].last_update = datetime.now()
            
        await self._update_job_status(job_id, VisualJobStatus.PROCESSING, progress)
        
        logger.debug(f"🔄 Job {job_id}: {step} ({progress*100:.0f}%)")
    
    async def _mark_job_completed(self, job_id: str, result: Dict[str, Any]):
        """Mark job as completed with result"""
        if job_id not in self.jobs:
            return
            
        job = self.jobs[job_id]
        job.status = VisualJobStatus.COMPLETED
        job.progress = 1.0
        job.result_url = result.get('result_url')
        job.completed_at = datetime.now()
        job.metadata.update(result.get('metadata', {}))
    
    async def _mark_job_failed(self, job_id: str, error_message: str):
        """Mark job as failed with error message"""
        if job_id not in self.jobs:
            return
            
        job = self.jobs[job_id]
        job.status = VisualJobStatus.FAILED
        job.error_message = error_message
        job.completed_at = datetime.now()
    
    def get_job_status(self, job_id: str) -> Optional[VisualGenerationJob]:
        """Get status of a specific job"""
        return self.jobs.get(job_id)
    
    def get_campaign_status(self, campaign_id: str) -> BatchVisualStatus:
        """Get status of all jobs for a campaign"""
        job_ids = self.campaign_jobs.get(campaign_id, [])
        jobs = [self.jobs[job_id] for job_id in job_ids if job_id in self.jobs]
        
        total_jobs = len(jobs)
        completed_jobs = len([j for j in jobs if j.status == VisualJobStatus.COMPLETED])
        failed_jobs = len([j for j in jobs if j.status == VisualJobStatus.FAILED])
        
        overall_progress = sum(j.progress for j in jobs) / max(total_jobs, 1)
        is_complete = completed_jobs + failed_jobs == total_jobs
        
        # Build posts with completed visuals
        posts_with_visuals = []
        completed_visuals = [j for j in jobs if j.status == VisualJobStatus.COMPLETED and j.result_url]
        
        # Group by post_id
        post_visuals = {}
        for job in completed_visuals:
            if job.post_id not in post_visuals:
                post_visuals[job.post_id] = {}
            if job.content_type == VisualContentType.IMAGE:
                post_visuals[job.post_id]['image_url'] = job.result_url
            else:
                post_visuals[job.post_id]['video_url'] = job.result_url
        
        for post_id, visuals in post_visuals.items():
            posts_with_visuals.append({
                'id': post_id,
                **visuals
            })
        
        # Estimate completion time for remaining jobs
        processing_jobs = [j for j in jobs if j.status == VisualJobStatus.PROCESSING]
        estimated_completion = None
        if processing_jobs:
            avg_remaining_time = sum(
                self.generation_estimates[j.content_type] * (1 - j.progress) 
                for j in processing_jobs
            ) / len(processing_jobs)
            estimated_completion = int(avg_remaining_time)
        
        return BatchVisualStatus(
            campaign_id=campaign_id,
            total_jobs=total_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            overall_progress=overall_progress,
            jobs=jobs,
            posts_with_visuals=posts_with_visuals,
            is_complete=is_complete,
            estimated_completion_seconds=estimated_completion
        )

# Global manager instance
visual_manager = AsyncVisualManager() 