"""
FILENAME: a2a_messaging.py
DESCRIPTION/PURPOSE: Agent-to-Agent messaging infrastructure for ADK v1.6+ upgrade
Author: JP + Claude Code + 2025-01-20

This module implements the A2A (Agent-to-Agent) messaging system enabling:
- Direct agent communication
- Event-driven coordination
- Structured message protocols
- Message bus routing and delivery
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from collections import defaultdict

try:
    from ..models.campaign_context import (
        CampaignContext,
        BusinessAnalysis,
        ContentStrategy, 
        VisualGuidance,
        GenerationEventType
    )
except ImportError:
    # Fallback for direct execution
    from models.campaign_context import (
        CampaignContext,
        BusinessAnalysis,
        ContentStrategy, 
        VisualGuidance,
        GenerationEventType
    )

logger = logging.getLogger(__name__)

# --- Message Types and Enums ---

class MessageType(str, Enum):
    """A2A message types for campaign workflow"""
    
    # Business analysis messages
    BUSINESS_ANALYSIS_COMPLETE = "business_analysis_complete"
    BUSINESS_CONTEXT_UPDATE = "business_context_update"
    
    # Content strategy messages  
    CONTENT_STRATEGY_READY = "content_strategy_ready"
    CONTENT_GENERATION_COMPLETE = "content_generation_complete"
    
    # Visual content messages
    VISUAL_PLANNING_COMPLETE = "visual_planning_complete" 
    VISUAL_CONTENT_GENERATED = "visual_content_generated"
    
    # Social media messages
    SOCIAL_POSTS_READY = "social_posts_ready"
    SOCIAL_CONTENT_OPTIMIZED = "social_content_optimized"
    
    # Campaign coordination messages
    CAMPAIGN_STAGE_COMPLETE = "campaign_stage_complete"
    CAMPAIGN_FINALIZED = "campaign_finalized"
    CAMPAIGN_ERROR = "campaign_error"
    
    # Progress and status messages
    PROGRESS_UPDATE = "progress_update"
    STATUS_REQUEST = "status_request"
    STATUS_RESPONSE = "status_response"

class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class DeliveryMode(str, Enum):
    """Message delivery modes"""
    ASYNC = "async"          # Fire and forget
    SYNC = "sync"            # Wait for response
    BROADCAST = "broadcast"  # Send to multiple recipients

# --- Core Message Models ---

class A2AMessage(BaseModel):
    """Agent-to-Agent message with structured payload"""
    
    # Message identification
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")
    message_type: MessageType = Field(..., description="Type of message")
    
    # Routing information
    sender: str = Field(..., description="Sending agent name")
    recipients: List[str] = Field(..., description="Target agent names")
    
    # Campaign context
    campaign_id: str = Field(..., description="Campaign identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Message content
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Delivery options
    priority: MessagePriority = Field(MessagePriority.NORMAL, description="Message priority")
    delivery_mode: DeliveryMode = Field(DeliveryMode.ASYNC, description="Delivery mode")
    requires_response: bool = Field(False, description="Whether response is required")
    response_timeout_seconds: int = Field(30, description="Response timeout")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.now, description="Message creation time")
    expires_at: Optional[datetime] = Field(None, description="Message expiration time")
    
    # Delivery tracking
    delivered_to: List[str] = Field(default_factory=list, description="Successfully delivered recipients")
    failed_deliveries: List[str] = Field(default_factory=list, description="Failed delivery recipients")
    response_received: bool = Field(False, description="Whether response was received")
    
    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MessageResponse(BaseModel):
    """Response to an A2A message"""
    
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_message_id: str = Field(..., description="ID of original message")
    sender: str = Field(..., description="Responding agent name")
    recipient: str = Field(..., description="Original sender")
    
    # Response data
    success: bool = Field(True, description="Whether request was successful")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Response payload")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# --- Specialized Message Classes ---

class BusinessAnalysisCompleteMessage(A2AMessage):
    """Business analysis completion message"""
    message_type: MessageType = MessageType.BUSINESS_ANALYSIS_COMPLETE
    
    def __init__(self, sender: str, recipients: List[str], campaign_id: str,
                 business_analysis: BusinessAnalysis, **kwargs):
        super().__init__(
            sender=sender,
            recipients=recipients,
            campaign_id=campaign_id,
            payload={
                "business_analysis": business_analysis.model_dump(),
                "next_steps": ["content_strategy", "visual_planning"]
            },
            **kwargs
        )

class ContentStrategyReadyMessage(A2AMessage):
    """Content strategy ready message"""
    message_type: MessageType = MessageType.CONTENT_STRATEGY_READY
    
    def __init__(self, sender: str, recipients: List[str], campaign_id: str,
                 content_strategy: ContentStrategy, **kwargs):
        super().__init__(
            sender=sender,
            recipients=recipients,
            campaign_id=campaign_id,
            payload={
                "content_strategy": content_strategy.model_dump(),
                "social_posts_count": len(content_strategy.social_posts),
                "platforms": [post.platform for post in content_strategy.social_posts]
            },
            **kwargs
        )

class VisualContentGeneratedMessage(A2AMessage):
    """Visual content generation complete message"""
    message_type: MessageType = MessageType.VISUAL_CONTENT_GENERATED
    
    def __init__(self, sender: str, recipients: List[str], campaign_id: str,
                 generated_assets: Dict[str, Any], **kwargs):
        super().__init__(
            sender=sender,
            recipients=recipients,
            campaign_id=campaign_id,
            payload={
                "generated_assets": generated_assets,
                "asset_count": len(generated_assets.get("assets", [])),
                "generation_summary": generated_assets.get("summary", {})
            },
            **kwargs
        )

class ProgressUpdateMessage(A2AMessage):
    """Progress update message"""
    message_type: MessageType = MessageType.PROGRESS_UPDATE
    
    def __init__(self, sender: str, recipients: List[str], campaign_id: str,
                 stage: GenerationEventType, progress_percentage: float,
                 status_message: str, **kwargs):
        super().__init__(
            sender=sender,
            recipients=recipients,
            campaign_id=campaign_id,
            payload={
                "stage": stage.value,
                "progress_percentage": progress_percentage,
                "status_message": status_message,
                "estimated_completion": None  # Can be calculated
            },
            **kwargs
        )

# --- Message Bus and Routing ---

MessageHandler = Callable[[A2AMessage], Awaitable[Optional[MessageResponse]]]

class MessageBus:
    """Central message bus for A2A communication"""
    
    def __init__(self):
        # Agent registration
        self._registered_agents: Dict[str, Dict[str, Any]] = {}
        
        # Message handlers
        self._message_handlers: Dict[str, Dict[MessageType, MessageHandler]] = defaultdict(dict)
        
        # Message queues for each agent
        self._message_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        
        # Message delivery tracking
        self._pending_messages: Dict[str, A2AMessage] = {}
        self._message_responses: Dict[str, MessageResponse] = {}
        
        # Message history for debugging
        self._message_history: List[A2AMessage] = []
        self._max_history_size = 1000
        
        # Event bus for external listeners
        self._event_listeners: Dict[MessageType, List[Callable]] = defaultdict(list)
        
        logger.info("✅ A2A MessageBus initialized")
    
    async def register_agent(self, agent_name: str, agent_metadata: Optional[Dict[str, Any]] = None):
        """Register an agent with the message bus"""
        
        self._registered_agents[agent_name] = {
            "name": agent_name,
            "registered_at": datetime.now(),
            "metadata": agent_metadata or {},
            "active": True,
            "message_count": 0
        }
        
        # Create message queue for agent
        if agent_name not in self._message_queues:
            self._message_queues[agent_name] = asyncio.Queue()
        
        logger.info(f"✅ Registered agent: {agent_name}")
    
    async def unregister_agent(self, agent_name: str):
        """Unregister agent from message bus"""
        
        if agent_name in self._registered_agents:
            self._registered_agents[agent_name]["active"] = False
        
        # Clear message handlers
        if agent_name in self._message_handlers:
            del self._message_handlers[agent_name]
        
        logger.info(f"✅ Unregistered agent: {agent_name}")
    
    def register_message_handler(self, agent_name: str, message_type: MessageType, 
                                handler: MessageHandler):
        """Register message handler for specific message type"""
        
        self._message_handlers[agent_name][message_type] = handler
        logger.info(f"✅ Registered handler: {agent_name} -> {message_type}")
    
    def register_event_listener(self, message_type: MessageType, listener: Callable):
        """Register event listener for message type"""
        self._event_listeners[message_type].append(listener)
        logger.info(f"✅ Registered event listener for: {message_type}")
    
    async def send_message(self, message: A2AMessage) -> bool:
        """Send message to recipients"""
        
        # Validate recipients
        invalid_recipients = [r for r in message.recipients 
                            if r not in self._registered_agents or 
                            not self._registered_agents[r]["active"]]
        
        if invalid_recipients:
            logger.warning(f"⚠️ Invalid recipients: {invalid_recipients}")
            message.failed_deliveries.extend(invalid_recipients)
        
        valid_recipients = [r for r in message.recipients if r not in invalid_recipients]
        
        if not valid_recipients:
            logger.error(f"❌ No valid recipients for message {message.message_id}")
            return False
        
        # Add to message history
        self._message_history.append(message)
        if len(self._message_history) > self._max_history_size:
            self._message_history.pop(0)
        
        # Store pending message if response required
        if message.requires_response:
            self._pending_messages[message.message_id] = message
        
        # Deliver to recipients
        delivery_tasks = []
        for recipient in valid_recipients:
            task = asyncio.create_task(self._deliver_message(message, recipient))
            delivery_tasks.append(task)
        
        # Wait for deliveries based on mode
        if message.delivery_mode == DeliveryMode.SYNC:
            results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            logger.info(f"✅ Sync delivery: {success_count}/{len(delivery_tasks)} successful")
        else:
            # Async delivery - don't wait
            asyncio.gather(*delivery_tasks, return_exceptions=True)
        
        # Notify event listeners
        await self._notify_event_listeners(message)
        
        logger.info(f"✅ Sent message {message.message_type} from {message.sender} to {valid_recipients}")
        return True
    
    async def _deliver_message(self, message: A2AMessage, recipient: str) -> bool:
        """Deliver message to specific recipient"""
        
        try:
            # Check if recipient has handler for this message type
            if (recipient in self._message_handlers and 
                message.message_type in self._message_handlers[recipient]):
                
                handler = self._message_handlers[recipient][message.message_type]
                
                # Call handler
                response = await handler(message)
                
                # Handle response if provided
                if response and message.requires_response:
                    self._message_responses[message.message_id] = response
                    message.response_received = True
                
                message.delivered_to.append(recipient)
                
                # Update agent stats
                if recipient in self._registered_agents:
                    self._registered_agents[recipient]["message_count"] += 1
                
                return True
            else:
                # No handler - add to queue for polling
                await self._message_queues[recipient].put(message)
                message.delivered_to.append(recipient)
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to deliver message to {recipient}: {e}")
            message.failed_deliveries.append(recipient)
            return False
    
    async def _notify_event_listeners(self, message: A2AMessage):
        """Notify event listeners about message"""
        
        listeners = self._event_listeners.get(message.message_type, [])
        
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(message)
                else:
                    listener(message)
            except Exception as e:
                logger.error(f"❌ Event listener error: {e}")
    
    async def get_messages(self, agent_name: str, timeout: float = 1.0) -> List[A2AMessage]:
        """Get pending messages for agent"""
        
        messages = []
        queue = self._message_queues.get(agent_name)
        
        if not queue:
            return messages
        
        try:
            # Get all available messages
            while True:
                message = await asyncio.wait_for(queue.get(), timeout=timeout)
                messages.append(message)
                timeout = 0.1  # Short timeout for subsequent messages
        except asyncio.TimeoutError:
            pass  # No more messages
        
        return messages
    
    async def send_response(self, response: MessageResponse) -> bool:
        """Send response to original message sender"""
        
        original_message = self._pending_messages.get(response.original_message_id)
        if not original_message:
            logger.warning(f"⚠️ No pending message for response: {response.original_message_id}")
            return False
        
        # Store response
        self._message_responses[response.original_message_id] = response
        original_message.response_received = True
        
        # Remove from pending
        del self._pending_messages[response.original_message_id]
        
        logger.info(f"✅ Received response for message {response.original_message_id}")
        return True
    
    async def wait_for_response(self, message_id: str, timeout: float = 30.0) -> Optional[MessageResponse]:
        """Wait for response to a message"""
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            if message_id in self._message_responses:
                response = self._message_responses[message_id]
                del self._message_responses[message_id]  # Clean up
                return response
            
            await asyncio.sleep(0.1)
        
        logger.warning(f"⚠️ Timeout waiting for response to message: {message_id}")
        return None
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        
        active_agents = sum(1 for a in self._registered_agents.values() if a["active"])
        total_messages = len(self._message_history)
        pending_responses = len(self._pending_messages)
        
        return {
            "registered_agents": len(self._registered_agents),
            "active_agents": active_agents,
            "total_messages": total_messages,
            "pending_responses": pending_responses,
            "message_types": list(set(m.message_type for m in self._message_history)),
            "agent_details": self._registered_agents
        }
    
    def get_message_history(self, campaign_id: Optional[str] = None, 
                          message_type: Optional[MessageType] = None,
                          limit: int = 50) -> List[A2AMessage]:
        """Get message history with optional filtering"""
        
        messages = self._message_history
        
        if campaign_id:
            messages = [m for m in messages if m.campaign_id == campaign_id]
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        return messages[-limit:]

# --- Global Message Bus Instance ---

# Global message bus instance
_global_message_bus: Optional[MessageBus] = None

def get_message_bus() -> MessageBus:
    """Get global message bus instance"""
    global _global_message_bus
    if _global_message_bus is None:
        _global_message_bus = MessageBus()
    return _global_message_bus

async def initialize_message_bus() -> MessageBus:
    """Initialize global message bus"""
    message_bus = get_message_bus()
    logger.info("✅ Global message bus initialized")
    return message_bus

# --- Helper Functions ---

async def send_business_analysis_complete(sender: str, recipients: List[str], 
                                        campaign_id: str, business_analysis: BusinessAnalysis) -> bool:
    """Helper to send business analysis complete message"""
    
    message_bus = get_message_bus()
    message = BusinessAnalysisCompleteMessage(
        sender=sender,
        recipients=recipients,
        campaign_id=campaign_id,
        business_analysis=business_analysis
    )
    
    return await message_bus.send_message(message)

async def send_content_strategy_ready(sender: str, recipients: List[str],
                                    campaign_id: str, content_strategy: ContentStrategy) -> bool:
    """Helper to send content strategy ready message"""
    
    message_bus = get_message_bus()
    message = ContentStrategyReadyMessage(
        sender=sender,
        recipients=recipients,
        campaign_id=campaign_id,
        content_strategy=content_strategy
    )
    
    return await message_bus.send_message(message)

async def send_progress_update(sender: str, recipients: List[str], campaign_id: str,
                             stage: GenerationEventType, progress_percentage: float,
                             status_message: str) -> bool:
    """Helper to send progress update message"""
    
    message_bus = get_message_bus()
    message = ProgressUpdateMessage(
        sender=sender,
        recipients=recipients,
        campaign_id=campaign_id,
        stage=stage,
        progress_percentage=progress_percentage,
        status_message=status_message
    )
    
    return await message_bus.send_message(message)

# Export main classes and functions
__all__ = [
    "A2AMessage",
    "MessageResponse", 
    "MessageType",
    "MessagePriority",
    "DeliveryMode",
    "MessageBus",
    "BusinessAnalysisCompleteMessage",
    "ContentStrategyReadyMessage", 
    "VisualContentGeneratedMessage",
    "ProgressUpdateMessage",
    "get_message_bus",
    "initialize_message_bus",
    "send_business_analysis_complete",
    "send_content_strategy_ready",
    "send_progress_update"
]