"""
FILENAME: test_enhanced_adk_upgrade.py
DESCRIPTION/PURPOSE: Comprehensive tests for ADK v1.6+ upgrade implementation
Author: JP + Claude Code + 2025-01-20

This module tests the enhanced ADK v1.6+ implementation including:
- Campaign context fidelity preservation
- A2A messaging functionality
- Persistent memory service
- Event-driven agent coordination
"""

import pytest
import asyncio
import tempfile
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from ..models.campaign_context import (
    CampaignContext,
    BusinessAnalysis,
    ContentStrategy,
    GenerationEventType,
    SocialPlatform,
    create_campaign_context,
    serialize_campaign_context,
    deserialize_campaign_context
)
from ..services.enhanced_memory_service import (
    EnhancedMemoryService,
    PersistentSessionService,
    initialize_memory_service
)
from ..messaging.a2a_messaging import (
    MessageBus,
    A2AMessage,
    MessageType,
    BusinessAnalysisCompleteMessage,
    get_message_bus,
    initialize_message_bus
)
from ..agents.enhanced_marketing_orchestrator_v2 import (
    EnhancedMarketingOrchestrator,
    EnhancedBusinessAnalysisAgent,
    EnhancedContentGenerationAgent,
    create_enhanced_marketing_orchestrator
)

class TestCampaignContextFidelity:
    """Test context fidelity preservation"""
    
    def test_campaign_context_serialization(self):
        """Test that campaign context serialization preserves all data"""
        
        # Create comprehensive campaign context
        context = create_campaign_context(
            campaign_id="test_campaign_123",
            campaign_name="Test Campaign",
            campaign_description="Test campaign for fidelity testing"
        )
        
        # Add complex business analysis
        context.business_analysis = BusinessAnalysis(
            company_name="Test Company",
            business_description="AI-powered test platform",
            target_audience={
                "demographics": {
                    "age_range": "25-45",
                    "gender": "All genders",
                    "income_level": "Middle to high income",
                    "education": "College educated", 
                    "location": "Urban areas",
                    "occupation": "Software developers"
                },
                "psychographics": {
                    "interests": ["Technology", "AI", "Productivity"],
                    "values": ["Innovation", "Efficiency"],
                    "lifestyle": "Tech-savvy professionals",
                    "personality_traits": ["Detail-oriented", "Goal-driven"],
                    "buying_behavior": "Research-driven"
                },
                "pain_points": ["Complex workflows", "Time management"],
                "preferred_platforms": [SocialPlatform.LINKEDIN, SocialPlatform.TWITTER],
                "engagement_patterns": {
                    "peak_activity_times": ["9:00 AM", "1:00 PM"],
                    "preferred_content_types": ["IMAGE", "VIDEO"],
                    "engagement_frequency": "Daily",
                    "content_preferences": ["How-to guides", "Tech insights"]
                }
            },
            brand_guidelines={
                "brand_voice": "Professional yet approachable",
                "tone_attributes": ["Professional", "Innovative"],
                "color_palette": ["#2563eb", "#3b82f6"],
                "visual_style": "Clean and modern",
                "brand_values": ["Innovation", "Reliability"],
                "messaging_principles": ["Clear communication"]
            },
            competitive_analysis={
                "direct_competitors": ["Competitor A", "Competitor B"],
                "indirect_competitors": ["Alternative A"],
                "competitive_advantages": ["AI features", "User experience"],
                "market_positioning": "Premium AI platform",
                "differentiation_factors": ["Advanced AI", "Intuitive design"]
            },
            campaign_objectives=[
                {
                    "type": "BRAND_AWARENESS",
                    "description": "Increase brand recognition",
                    "target_metrics": {"reach": 100000},
                    "priority": 1
                }
            ],
            industry_context={
                "industry": "SaaS/AI",
                "market_size": "Growing rapidly",
                "growth_trends": ["AI adoption", "Remote work"],
                "regulatory_considerations": ["Data privacy"],
                "seasonal_factors": ["Q4 budget cycles"]
            },
            unique_value_proposition="AI-powered productivity platform",
            key_messages=["AI productivity", "Seamless collaboration"],
            confidence_score=0.95
        )
        
        # Add generation event
        context.add_generation_event(
            event_type=GenerationEventType.BUSINESS_ANALYSIS,
            agent_name="test_agent",
            duration=5.2,
            success=True,
            test_metadata="additional_data"
        )
        
        # Serialize and deserialize
        serialized = serialize_campaign_context(context)
        restored_context = deserialize_campaign_context(serialized)
        
        # Verify complete fidelity
        assert restored_context.campaign_id == context.campaign_id
        assert restored_context.campaign_name == context.campaign_name
        assert restored_context.version == context.version
        
        # Verify business analysis preservation
        assert restored_context.business_analysis is not None
        assert restored_context.business_analysis.company_name == "Test Company"
        assert restored_context.business_analysis.confidence_score == 0.95
        
        # Verify complex nested data preservation
        assert len(restored_context.business_analysis.target_audience.preferred_platforms) == 2
        assert SocialPlatform.LINKEDIN in restored_context.business_analysis.target_audience.preferred_platforms
        
        # Verify generation events preservation
        assert len(restored_context.generation_history) == 1
        event = restored_context.generation_history[0]
        assert event.event_type == GenerationEventType.BUSINESS_ANALYSIS
        assert event.agent_name == "test_agent"
        assert event.duration_seconds == 5.2
        assert event.metadata["test_metadata"] == "additional_data"
        
        # Verify datetime preservation
        assert isinstance(restored_context.creation_timestamp, datetime)
        assert isinstance(event.timestamp, datetime)

class TestEnhancedMemoryService:
    """Test enhanced memory service functionality"""
    
    @pytest.fixture
    async def temp_memory_service(self):
        """Create temporary memory service for testing"""
        temp_dir = tempfile.mkdtemp()
        try:
            memory_service = await initialize_memory_service(temp_dir)
            yield memory_service
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_campaign_context_persistence(self, temp_memory_service):
        """Test campaign context persistence across service restarts"""
        
        memory_service = temp_memory_service
        
        # Create and save campaign context
        campaign_id = "test_persistence_123"
        context = await memory_service.create_campaign_context(
            campaign_id=campaign_id,
            campaign_name="Persistence Test Campaign"
        )
        
        # Add some data
        context.add_generation_event(
            event_type=GenerationEventType.BUSINESS_ANALYSIS,
            agent_name="test_agent",
            duration=3.5
        )
        
        await memory_service.save_campaign_context(context)
        
        # Simulate service restart by creating new memory service
        base_path = memory_service.session_service.base_path
        new_memory_service = await initialize_memory_service(str(base_path))
        
        # Retrieve context from new service
        restored_context = await new_memory_service.get_campaign_context(campaign_id)
        
        assert restored_context is not None
        assert restored_context.campaign_id == campaign_id
        assert restored_context.campaign_name == "Persistence Test Campaign"
        assert len(restored_context.generation_history) == 1
        assert restored_context.version == 2  # Incremented by add_generation_event
    
    @pytest.mark.asyncio
    async def test_memory_service_caching(self, temp_memory_service):
        """Test memory service caching behavior"""
        
        memory_service = temp_memory_service
        
        # Create campaign context
        campaign_id = "test_caching_123"
        context = await memory_service.create_campaign_context(campaign_id)
        
        # First retrieval (from disk)
        context1 = await memory_service.get_campaign_context(campaign_id)
        
        # Second retrieval (from cache)
        context2 = await memory_service.get_campaign_context(campaign_id)
        
        # Should be same object reference (cached)
        assert context1 is context2
        
        # Verify cache statistics
        stats = await memory_service.get_memory_stats()
        assert stats["cached_contexts"] >= 1
        assert stats["total_contexts"] >= 1
    
    @pytest.mark.asyncio
    async def test_campaign_context_versioning(self, temp_memory_service):
        """Test campaign context versioning system"""
        
        memory_service = temp_memory_service
        
        # Create campaign context
        campaign_id = "test_versioning_123"
        context = await memory_service.create_campaign_context(campaign_id)
        initial_version = context.version
        
        # Update context multiple times
        for i in range(3):
            await memory_service.add_generation_event(
                campaign_id=campaign_id,
                event_type=GenerationEventType.BUSINESS_ANALYSIS,
                agent_name=f"agent_{i}",
                duration=float(i + 1)
            )
        
        # Retrieve final context
        final_context = await memory_service.get_campaign_context(campaign_id)
        
        # Verify version increments
        assert final_context.version == initial_version + 3
        assert len(final_context.generation_history) == 3
        
        # Verify events are ordered by timestamp
        timestamps = [event.timestamp for event in final_context.generation_history]
        assert timestamps == sorted(timestamps)

class TestA2AMessaging:
    """Test A2A messaging system"""
    
    @pytest.fixture
    async def message_bus(self):
        """Create message bus for testing"""
        message_bus = await initialize_message_bus()
        yield message_bus
        # Cleanup
        message_bus._registered_agents.clear()
        message_bus._message_handlers.clear()
        message_bus._message_history.clear()
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, message_bus):
        """Test agent registration with message bus"""
        
        # Register agents
        await message_bus.register_agent("test_agent_1", {"type": "business_analysis"})
        await message_bus.register_agent("test_agent_2", {"type": "content_generation"})
        
        # Verify registration
        stats = message_bus.get_agent_stats()
        assert stats["registered_agents"] == 2
        assert stats["active_agents"] == 2
        
        # Test agent details
        assert "test_agent_1" in message_bus._registered_agents
        assert message_bus._registered_agents["test_agent_1"]["active"] is True
    
    @pytest.mark.asyncio
    async def test_message_delivery(self, message_bus):
        """Test message delivery between agents"""
        
        # Register agents
        await message_bus.register_agent("sender_agent")
        await message_bus.register_agent("receiver_agent")
        
        # Track received messages
        received_messages = []
        
        async def message_handler(message: A2AMessage):
            received_messages.append(message)
            return None
        
        # Register message handler
        message_bus.register_message_handler(
            "receiver_agent",
            MessageType.BUSINESS_ANALYSIS_COMPLETE,
            message_handler
        )
        
        # Create and send message
        message = A2AMessage(
            message_type=MessageType.BUSINESS_ANALYSIS_COMPLETE,
            sender="sender_agent",
            recipients=["receiver_agent"],
            campaign_id="test_campaign_123",
            payload={"test_data": "message_content"}
        )
        
        # Send message
        success = await message_bus.send_message(message)
        
        # Verify delivery
        assert success is True
        assert len(received_messages) == 1
        assert received_messages[0].message_id == message.message_id
        assert received_messages[0].payload["test_data"] == "message_content"
        
        # Verify message history
        history = message_bus.get_message_history(campaign_id="test_campaign_123")
        assert len(history) == 1
    
    @pytest.mark.asyncio
    async def test_business_analysis_complete_message(self, message_bus):
        """Test specialized business analysis complete message"""
        
        from ..models.campaign_context import BusinessAnalysis
        
        # Register agents
        await message_bus.register_agent("business_agent")
        await message_bus.register_agent("content_agent")
        
        # Create mock business analysis
        business_analysis = BusinessAnalysis(
            company_name="Test Company",
            business_description="Test description",
            target_audience={
                "demographics": {"age_range": "25-35"},
                "psychographics": {"interests": ["tech"]},
                "pain_points": ["complexity"],
                "preferred_platforms": [SocialPlatform.LINKEDIN],
                "engagement_patterns": {
                    "peak_activity_times": ["9:00 AM"],
                    "preferred_content_types": ["IMAGE"],
                    "engagement_frequency": "Daily",
                    "content_preferences": ["Tech news"]
                }
            },
            brand_guidelines={
                "brand_voice": "Professional",
                "tone_attributes": ["Expert"],
                "color_palette": ["#blue"],
                "brand_values": ["Innovation"],
                "messaging_principles": ["Clear"]
            },
            competitive_analysis={
                "direct_competitors": ["Competitor A"],
                "indirect_competitors": [],
                "competitive_advantages": ["AI"],
                "market_positioning": "Premium",
                "differentiation_factors": ["Features"]
            },
            campaign_objectives=[{
                "type": "BRAND_AWARENESS",
                "description": "Increase awareness",
                "target_metrics": {"reach": 1000},
                "priority": 1
            }],
            industry_context={
                "industry": "Tech",
                "growth_trends": ["AI adoption"],
                "regulatory_considerations": [],
                "seasonal_factors": []
            },
            unique_value_proposition="AI platform",
            key_messages=["Innovation"]
        )
        
        # Create and send specialized message
        message = BusinessAnalysisCompleteMessage(
            sender="business_agent",
            recipients=["content_agent"],
            campaign_id="test_campaign_123",
            business_analysis=business_analysis
        )
        
        # Send message
        success = await message_bus.send_message(message)
        
        # Verify specialized message
        assert success is True
        assert message.message_type == MessageType.BUSINESS_ANALYSIS_COMPLETE
        assert "business_analysis" in message.payload
        assert "next_steps" in message.payload
        assert message.payload["next_steps"] == ["content_strategy", "visual_planning"]

class TestEnhancedOrchestrator:
    """Test enhanced marketing orchestrator"""
    
    @pytest.fixture
    async def temp_orchestrator(self):
        """Create temporary orchestrator for testing"""
        temp_dir = tempfile.mkdtemp()
        try:
            orchestrator = await create_enhanced_marketing_orchestrator(temp_dir)
            yield orchestrator
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, temp_orchestrator):
        """Test orchestrator initialization"""
        
        orchestrator = temp_orchestrator
        
        # Verify components initialized
        assert orchestrator.memory_service is not None
        assert orchestrator.business_agent is not None
        assert orchestrator.content_agent is not None
        assert orchestrator.message_bus is not None
        
        # Verify agent registration
        stats = orchestrator.message_bus.get_agent_stats()
        assert stats["registered_agents"] >= 3  # orchestrator + business + content agents
    
    @pytest.mark.asyncio
    async def test_campaign_generation_workflow(self, temp_orchestrator):
        """Test complete campaign generation workflow"""
        
        orchestrator = temp_orchestrator
        
        # Create campaign input
        campaign_id = "test_workflow_123"
        business_input = {
            "campaign_name": "Test Workflow Campaign",
            "description": "Testing complete workflow",
            "business_url": "https://example.com",
            "business_description": "AI productivity platform"
        }
        
        # Generate campaign
        final_context = await orchestrator.generate_campaign(campaign_id, business_input)
        
        # Verify campaign completion
        assert final_context is not None
        assert final_context.campaign_id == campaign_id
        assert final_context.business_analysis is not None
        assert final_context.content_strategy is not None
        
        # Verify generation events
        assert len(final_context.generation_history) >= 2  # business + content events
        
        # Verify completion stages
        assert GenerationEventType.BUSINESS_ANALYSIS in final_context.completed_stages
        assert GenerationEventType.CONTENT_STRATEGY in final_context.completed_stages
        
        # Verify campaign persistence
        retrieved_context = await orchestrator.memory_service.get_campaign_context(campaign_id)
        assert retrieved_context.campaign_id == final_context.campaign_id
        assert retrieved_context.version == final_context.version
    
    @pytest.mark.asyncio
    async def test_campaign_status_tracking(self, temp_orchestrator):
        """Test campaign status and progress tracking"""
        
        orchestrator = temp_orchestrator
        
        # Create campaign
        campaign_id = "test_status_123"
        business_input = {"campaign_name": "Status Test Campaign"}
        
        # Start campaign generation (run in background to test status)
        campaign_task = asyncio.create_task(
            orchestrator.generate_campaign(campaign_id, business_input)
        )
        
        # Wait a bit for generation to start
        await asyncio.sleep(0.1)
        
        # Check status during generation
        status = await orchestrator.get_campaign_status(campaign_id)
        
        if status:  # Campaign might complete quickly in tests
            assert status["campaign_id"] == campaign_id
            assert "completion_percentage" in status
            assert "completed_stages" in status
            assert "generation_history" in status
        
        # Wait for completion
        final_context = await campaign_task
        
        # Check final status
        final_status = await orchestrator.get_campaign_status(campaign_id)
        assert final_status is not None
        assert final_status["completion_percentage"] > 0
    
    @pytest.mark.asyncio
    async def test_memory_and_message_stats(self, temp_orchestrator):
        """Test memory and message statistics"""
        
        orchestrator = temp_orchestrator
        
        # Create a few campaigns
        for i in range(3):
            campaign_id = f"test_stats_{i}"
            business_input = {"campaign_name": f"Stats Test Campaign {i}"}
            await orchestrator.generate_campaign(campaign_id, business_input)
        
        # Get comprehensive stats
        stats = await orchestrator.get_memory_stats()
        
        # Verify memory stats
        assert "memory_service" in stats
        assert "message_bus" in stats
        assert "active_campaigns" in stats
        
        memory_stats = stats["memory_service"]
        assert memory_stats["total_contexts"] >= 3
        
        message_stats = stats["message_bus"]
        assert message_stats["total_messages"] >= 6  # 2 messages per campaign minimum

class TestIntegrationAPI:
    """Test integration with API endpoints"""
    
    @pytest.mark.asyncio
    async def test_api_campaign_creation_flow(self):
        """Test API campaign creation and status flow"""
        
        # This would test the actual API endpoints
        # For now, we'll test the core components they use
        
        from ..api.routes.enhanced_campaigns import CampaignRequest
        
        # Create request model
        request = CampaignRequest(
            campaign_name="API Test Campaign",
            business_url="https://example.com",
            target_platforms=[SocialPlatform.LINKEDIN, SocialPlatform.TWITTER],
            campaign_objectives=["Brand awareness", "Lead generation"]
        )
        
        # Verify request validation
        assert request.campaign_name == "API Test Campaign"
        assert len(request.target_platforms) == 2
        assert SocialPlatform.LINKEDIN in request.target_platforms

# Performance and stress tests
class TestPerformanceAndStress:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_campaign_generation(self):
        """Test concurrent campaign generation"""
        
        temp_dir = tempfile.mkdtemp()
        try:
            orchestrator = await create_enhanced_marketing_orchestrator(temp_dir)
            
            # Generate multiple campaigns concurrently
            tasks = []
            for i in range(5):
                campaign_id = f"concurrent_test_{i}"
                business_input = {"campaign_name": f"Concurrent Campaign {i}"}
                task = orchestrator.generate_campaign(campaign_id, business_input)
                tasks.append(task)
            
            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all succeeded
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    pytest.fail(f"Campaign {i} failed: {result}")
                else:
                    assert result.campaign_id == f"concurrent_test_{i}"
            
            # Verify all campaigns persisted
            campaigns = await orchestrator.list_campaigns()
            assert len(campaigns) >= 5
            
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_large_context_serialization_performance(self):
        """Test performance with large campaign contexts"""
        
        # Create large context with many events
        context = create_campaign_context("perf_test_123")
        
        # Add many generation events
        for i in range(100):
            context.add_generation_event(
                event_type=GenerationEventType.BUSINESS_ANALYSIS,
                agent_name=f"agent_{i}",
                duration=float(i),
                metadata={f"key_{j}": f"value_{j}" for j in range(10)}
            )
        
        # Time serialization
        import time
        start_time = time.time()
        serialized = serialize_campaign_context(context)
        serialize_time = time.time() - start_time
        
        # Time deserialization
        start_time = time.time()
        restored = deserialize_campaign_context(serialized)
        deserialize_time = time.time() - start_time
        
        # Verify performance (should be fast)
        assert serialize_time < 1.0  # Less than 1 second
        assert deserialize_time < 1.0  # Less than 1 second
        
        # Verify fidelity with large context
        assert len(restored.generation_history) == 100
        assert restored.version == 101  # Initial version + 100 events

if __name__ == "__main__":
    # Run specific test for debugging
    pytest.main([__file__ + "::TestCampaignContextFidelity::test_campaign_context_serialization", "-v"])