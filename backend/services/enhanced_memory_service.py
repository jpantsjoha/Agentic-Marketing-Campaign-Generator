"""
FILENAME: enhanced_memory_service.py  
DESCRIPTION/PURPOSE: Enhanced memory service with persistent sessions for ADK v1.6+ upgrade
Author: JP + Claude Code + 2025-01-20

This module implements the enhanced memory service architecture with:
- Persistent session storage
- Campaign context management  
- Zero fidelity loss serialization
- Automatic versioning and recovery
"""

import logging
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import aiofiles
import pickle
from contextlib import asynccontextmanager

from google.adk.memory import BaseMemoryService
from google.adk.sessions import BaseSessionService

try:
    from ..models.campaign_context import (
        CampaignContext, 
        GenerationEvent,
        GenerationEventType,
        create_campaign_context,
        serialize_campaign_context,
        deserialize_campaign_context
    )
except ImportError:
    # Fallback for direct execution
    from models.campaign_context import (
        CampaignContext, 
        GenerationEvent,
        GenerationEventType,
        create_campaign_context,
        serialize_campaign_context,
        deserialize_campaign_context
    )

logger = logging.getLogger(__name__)

class PersistentSessionService(BaseSessionService):
    """Persistent session service with filesystem backend"""
    
    def __init__(self, storage_backend: str = "filesystem", 
                 base_path: str = "./campaign_sessions",
                 max_session_age_hours: int = 24 * 7):  # 1 week default
        self.storage_backend = storage_backend
        self.base_path = Path(base_path)
        self.max_session_age_hours = max_session_age_hours
        
        # Ensure storage directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for active sessions
        self._session_cache: Dict[str, CampaignContext] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        logger.info(f"✅ PersistentSessionService initialized with storage: {self.base_path}")
    
    def _get_session_file_path(self, session_id: str) -> Path:
        """Get file path for session storage"""
        return self.base_path / f"session_{session_id}.json"
    
    def _get_context_file_path(self, campaign_id: str) -> Path:
        """Get file path for campaign context storage"""
        return self.base_path / f"campaign_{campaign_id}.json"
    
    async def create_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new session"""
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "active": True
        }
        
        session_file = self._get_session_file_path(session_id)
        async with aiofiles.open(session_file, 'w') as f:
            await f.write(json.dumps(session_data, indent=2))
        
        logger.info(f"✅ Created session: {session_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        session_file = self._get_session_file_path(session_id)
        
        if not session_file.exists():
            return None
        
        try:
            async with aiofiles.open(session_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"❌ Error reading session {session_id}: {e}")
            return None
    
    async def update_session(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """Update session metadata"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
        
        session_data["metadata"].update(metadata)
        session_data["updated_at"] = datetime.now().isoformat()
        
        session_file = self._get_session_file_path(session_id)
        try:
            async with aiofiles.open(session_file, 'w') as f:
                await f.write(json.dumps(session_data, indent=2))
            return True
        except Exception as e:
            logger.error(f"❌ Error updating session {session_id}: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        session_file = self._get_session_file_path(session_id)
        
        try:
            if session_file.exists():
                session_file.unlink()
            
            # Remove from cache
            if session_id in self._session_cache:
                del self._session_cache[session_id]
                del self._cache_timestamps[session_id]
            
            logger.info(f"✅ Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting session {session_id}: {e}")
            return False
    
    async def list_sessions(self, active_only: bool = True) -> List[str]:
        """List all sessions"""
        sessions = []
        
        for session_file in self.base_path.glob("session_*.json"):
            session_id = session_file.stem.replace("session_", "")
            
            if active_only:
                session_data = await self.get_session(session_id)
                if session_data and session_data.get("active", False):
                    sessions.append(session_id)
            else:
                sessions.append(session_id)
        
        return sessions
    
    async def cleanup_old_sessions(self) -> int:
        """Clean up old sessions"""
        cutoff_time = datetime.now() - timedelta(hours=self.max_session_age_hours)
        cleaned_count = 0
        
        for session_file in self.base_path.glob("session_*.json"):
            try:
                session_id = session_file.stem.replace("session_", "")
                session_data = await self.get_session(session_id)
                
                if session_data:
                    created_at = datetime.fromisoformat(session_data["created_at"])
                    if created_at < cutoff_time:
                        await self.delete_session(session_id)
                        cleaned_count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error cleaning session {session_file}: {e}")
        
        logger.info(f"✅ Cleaned up {cleaned_count} old sessions")
        return cleaned_count

class EnhancedMemoryService(BaseMemoryService):
    """Enhanced memory service with campaign context management"""
    
    def __init__(self, session_service: PersistentSessionService, 
                 context_class=CampaignContext):
        self.session_service = session_service
        self.context_class = context_class
        
        # In-memory cache for active contexts
        self._context_cache: Dict[str, CampaignContext] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._max_cache_size = 100
        self._cache_ttl_minutes = 30
        
        logger.info("✅ EnhancedMemoryService initialized")
    
    def _evict_cache_if_needed(self):
        """Evict old entries from cache if needed"""
        if len(self._context_cache) <= self._max_cache_size:
            return
        
        # Remove oldest entries
        cutoff_time = datetime.now() - timedelta(minutes=self._cache_ttl_minutes)
        to_remove = []
        
        for campaign_id, timestamp in self._cache_timestamps.items():
            if timestamp < cutoff_time:
                to_remove.append(campaign_id)
        
        for campaign_id in to_remove:
            self._context_cache.pop(campaign_id, None)
            self._cache_timestamps.pop(campaign_id, None)
        
        # If still too large, remove oldest entries
        if len(self._context_cache) > self._max_cache_size:
            sorted_items = sorted(self._cache_timestamps.items(), key=lambda x: x[1])
            remove_count = len(self._context_cache) - self._max_cache_size
            
            for campaign_id, _ in sorted_items[:remove_count]:
                self._context_cache.pop(campaign_id, None)
                self._cache_timestamps.pop(campaign_id, None)
    
    async def save_campaign_context(self, context: CampaignContext) -> bool:
        """Save campaign context with automatic versioning"""
        try:
            # Update timestamps
            context.last_updated = datetime.now()
            
            # Save to filesystem
            context_file = self.session_service._get_context_file_path(context.campaign_id)
            serialized = serialize_campaign_context(context)
            
            async with aiofiles.open(context_file, 'w') as f:
                await f.write(serialized)
            
            # Update cache
            self._context_cache[context.campaign_id] = context
            self._cache_timestamps[context.campaign_id] = datetime.now()
            self._evict_cache_if_needed()
            
            logger.info(f"✅ Saved campaign context: {context.campaign_id} (v{context.version})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving campaign context {context.campaign_id}: {e}")
            return False
    
    async def get_campaign_context(self, campaign_id: str) -> Optional[CampaignContext]:
        """Get campaign context with caching"""
        
        # Check cache first
        if campaign_id in self._context_cache:
            cache_time = self._cache_timestamps[campaign_id]
            if datetime.now() - cache_time < timedelta(minutes=self._cache_ttl_minutes):
                logger.debug(f"📋 Retrieved campaign context from cache: {campaign_id}")
                return self._context_cache[campaign_id]
        
        # Load from filesystem
        context_file = self.session_service._get_context_file_path(campaign_id)
        
        if not context_file.exists():
            logger.warning(f"⚠️ Campaign context not found: {campaign_id}")
            return None
        
        try:
            async with aiofiles.open(context_file, 'r') as f:
                content = await f.read()
                context = deserialize_campaign_context(content)
            
            # Update cache
            self._context_cache[campaign_id] = context
            self._cache_timestamps[campaign_id] = datetime.now()
            self._evict_cache_if_needed()
            
            logger.info(f"✅ Loaded campaign context: {campaign_id} (v{context.version})")
            return context
            
        except Exception as e:
            logger.error(f"❌ Error loading campaign context {campaign_id}: {e}")
            return None
    
    async def create_campaign_context(self, campaign_id: str, campaign_name: Optional[str] = None,
                                    campaign_description: Optional[str] = None,
                                    session_id: Optional[str] = None) -> CampaignContext:
        """Create new campaign context"""
        
        context = create_campaign_context(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            campaign_description=campaign_description
        )
        
        if session_id:
            context.session_id = session_id
        
        # Save immediately
        await self.save_campaign_context(context)
        
        logger.info(f"✅ Created new campaign context: {campaign_id}")
        return context
    
    async def update_campaign_context(self, campaign_id: str, 
                                    updates: Dict[str, Any]) -> Optional[CampaignContext]:
        """Update campaign context with new data"""
        
        context = await self.get_campaign_context(campaign_id)
        if not context:
            logger.error(f"❌ Cannot update non-existent campaign: {campaign_id}")
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
            else:
                logger.warning(f"⚠️ Unknown context attribute: {key}")
        
        # Increment version
        context.version += 1
        context.last_updated = datetime.now()
        
        # Save updated context
        await self.save_campaign_context(context)
        
        logger.info(f"✅ Updated campaign context: {campaign_id} (v{context.version})")
        return context
    
    async def delete_campaign_context(self, campaign_id: str) -> bool:
        """Delete campaign context"""
        
        try:
            # Remove from filesystem
            context_file = self.session_service._get_context_file_path(campaign_id)
            if context_file.exists():
                context_file.unlink()
            
            # Remove from cache
            self._context_cache.pop(campaign_id, None)
            self._cache_timestamps.pop(campaign_id, None)
            
            logger.info(f"✅ Deleted campaign context: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting campaign context {campaign_id}: {e}")
            return False
    
    async def list_campaign_contexts(self) -> List[str]:
        """List all campaign context IDs"""
        
        campaign_ids = []
        
        for context_file in self.session_service.base_path.glob("campaign_*.json"):
            campaign_id = context_file.stem.replace("campaign_", "")
            campaign_ids.append(campaign_id)
        
        return sorted(campaign_ids)
    
    async def add_generation_event(self, campaign_id: str, event_type: GenerationEventType,
                                 agent_name: str, duration: Optional[float] = None,
                                 success: bool = True, error_message: Optional[str] = None,
                                 **metadata) -> Optional[GenerationEvent]:
        """Add generation event to campaign context"""
        
        context = await self.get_campaign_context(campaign_id)
        if not context:
            logger.error(f"❌ Cannot add event to non-existent campaign: {campaign_id}")
            return None
        
        event = context.add_generation_event(
            event_type=event_type,
            agent_name=agent_name,
            duration=duration,
            success=success,
            error_message=error_message,
            **metadata
        )
        
        # Save updated context
        await self.save_campaign_context(context)
        
        logger.info(f"✅ Added generation event: {campaign_id} - {event_type} by {agent_name}")
        return event
    
    @asynccontextmanager
    async def session(self, campaign_id: str):
        """Context manager for campaign context sessions"""
        
        context = await self.get_campaign_context(campaign_id)
        if not context:
            context = await self.create_campaign_context(campaign_id)
        
        try:
            yield CampaignContextSession(context, self)
        finally:
            # Auto-save on exit
            await self.save_campaign_context(context)
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory service statistics"""
        
        total_contexts = len(await self.list_campaign_contexts())
        cached_contexts = len(self._context_cache)
        
        return {
            "total_contexts": total_contexts,
            "cached_contexts": cached_contexts,
            "cache_hit_ratio": cached_contexts / max(total_contexts, 1),
            "storage_backend": self.session_service.storage_backend,
            "base_path": str(self.session_service.base_path),
            "max_cache_size": self._max_cache_size,
            "cache_ttl_minutes": self._cache_ttl_minutes
        }
    
    async def add_session_to_memory(self, session_id: str, context: Any) -> bool:
        """Add session to memory (required by BaseMemoryService)"""
        try:
            if isinstance(context, CampaignContext):
                context.session_id = session_id
                return await self.save_campaign_context(context)
            else:
                # Handle other context types if needed
                logger.warning(f"⚠️ Unsupported context type for session {session_id}: {type(context)}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to add session {session_id} to memory: {e}")
            return False
    
    async def search_memory(self, query: str, limit: int = 10) -> List[Any]:
        """Search memory for relevant contexts (required by BaseMemoryService)"""
        try:
            # Get all campaign contexts
            campaign_ids = await self.list_campaign_contexts()
            results = []
            
            # Simple text search through campaign contexts
            for campaign_id in campaign_ids[:limit]:
                context = await self.get_campaign_context(campaign_id)
                if context:
                    # Search in campaign name, description, and business analysis
                    searchable_text = ""
                    if context.campaign_name:
                        searchable_text += context.campaign_name.lower() + " "
                    if context.campaign_description:
                        searchable_text += context.campaign_description.lower() + " "
                    if context.business_analysis:
                        searchable_text += context.business_analysis.company_name.lower() + " "
                        searchable_text += context.business_analysis.business_description.lower() + " "
                    
                    if query.lower() in searchable_text:
                        results.append(context)
                        
                    if len(results) >= limit:
                        break
            
            logger.info(f"🔍 Memory search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Memory search failed: {e}")
            return []

class CampaignContextSession:
    """Session wrapper for campaign context operations"""
    
    def __init__(self, context: CampaignContext, memory_service: EnhancedMemoryService):
        self.context = context
        self.memory_service = memory_service
        self._initial_version = context.version
    
    async def get_context(self) -> CampaignContext:
        """Get the campaign context"""
        return self.context
    
    async def save_context(self, context: Optional[CampaignContext] = None) -> bool:
        """Save the campaign context"""
        if context:
            self.context = context
        return await self.memory_service.save_campaign_context(self.context)
    
    async def add_event(self, event_type: GenerationEventType, agent_name: str,
                       duration: Optional[float] = None, success: bool = True,
                       error_message: Optional[str] = None, **metadata) -> GenerationEvent:
        """Add generation event to context"""
        return self.context.add_generation_event(
            event_type=event_type,
            agent_name=agent_name,
            duration=duration,
            success=success,
            error_message=error_message,
            **metadata
        )
    
    def has_changes(self) -> bool:
        """Check if context has been modified"""
        return self.context.version > self._initial_version

# --- Factory Functions ---

def create_enhanced_memory_service(base_path: str = "./campaign_sessions") -> EnhancedMemoryService:
    """Factory function to create enhanced memory service"""
    
    session_service = PersistentSessionService(
        storage_backend="filesystem",
        base_path=base_path
    )
    
    return EnhancedMemoryService(session_service=session_service)

# --- Async initialization ---

async def initialize_memory_service(base_path: str = "./campaign_sessions") -> EnhancedMemoryService:
    """Initialize memory service with cleanup"""
    
    memory_service = create_enhanced_memory_service(base_path)
    
    # Clean up old sessions on startup
    await memory_service.session_service.cleanup_old_sessions()
    
    logger.info("✅ Enhanced memory service fully initialized")
    return memory_service

# Export main classes
__all__ = [
    "EnhancedMemoryService",
    "PersistentSessionService", 
    "CampaignContextSession",
    "create_enhanced_memory_service",
    "initialize_memory_service"
]