"""
Test Enhanced Agents from Phase 1 Implementation

This module tests the enhanced agents implemented in Phase 1:
- Enhanced Marketing Orchestrator with ADK v1.6.1
- Enhanced Video Generation Agent with Veo 2.0
- Enhanced Image Generation Agent with Imagen 3.0  
- Enhanced Social Media Agent with OAuth

Author: JP + 2025-07-14
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Test enhanced agent imports
from agents.enhanced_marketing_orchestrator import (
    EnhancedMarketingOrchestrator,
    create_enhanced_marketing_orchestrator,
    execute_campaign_workflow
)
from agents.enhanced_video_generation_agent import (
    EnhancedVideoGenerationAgent,
    create_enhanced_video_generation_agent
)
from agents.enhanced_image_generation_agent import (
    EnhancedImageGenerationAgent,
    create_enhanced_image_generation_agent
)
from agents.enhanced_social_media_agent import (
    EnhancedSocialMediaAgent,
    create_enhanced_social_media_agent
)


class TestEnhancedMarketingOrchestrator:
    """Test Enhanced Marketing Orchestrator with ADK v1.6.1 features."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test that the enhanced orchestrator initializes correctly."""
        orchestrator = EnhancedMarketingOrchestrator()
        
        assert orchestrator is not None
        assert orchestrator.campaign_id is not None
        assert orchestrator.memory_service is not None
        assert orchestrator.campaign_state == {}
        assert hasattr(orchestrator, 'business_analysis_agent')
        assert hasattr(orchestrator, 'content_generation_agent')
        assert hasattr(orchestrator, 'visual_content_agent')
        assert hasattr(orchestrator, 'social_media_agent')
    
    @pytest.mark.asyncio
    async def test_campaign_state_management(self):
        """Test campaign state management functionality."""
        orchestrator = EnhancedMarketingOrchestrator()
        
        # Test initial state
        state = orchestrator.get_campaign_state()
        assert state == {}
        
        # Test state restoration
        result = orchestrator.restore_campaign_state("test_campaign_id")
        assert result is False  # Should be False for empty state
        
        # Test with some state
        orchestrator.campaign_state["test"] = "data"
        state = orchestrator.get_campaign_state()
        assert state["test"] == "data"
    
    @pytest.mark.asyncio 
    async def test_factory_function(self):
        """Test the factory function creates orchestrator correctly."""
        orchestrator = await create_enhanced_marketing_orchestrator()
        
        assert isinstance(orchestrator, EnhancedMarketingOrchestrator)
        assert orchestrator.campaign_id is not None


class TestEnhancedVideoGenerationAgent:
    """Test Enhanced Video Generation Agent with Veo 2.0."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that the enhanced video agent initializes correctly."""
        agent = EnhancedVideoGenerationAgent()
        
        assert agent is not None
        assert hasattr(agent, 'storage_manager')
        assert hasattr(agent, 'generation_queue')
        assert agent.storage_manager is not None
        assert agent.generation_queue is not None
    
    @pytest.mark.asyncio
    async def test_video_generation_queue(self):
        """Test video generation queue functionality."""
        agent = EnhancedVideoGenerationAgent()
        
        # Test job status for non-existent job
        status = await agent.get_video_generation_status("nonexistent_job")
        assert status.get('status') == 'not_found'
    
    @pytest.mark.asyncio
    async def test_factory_function(self):
        """Test the factory function creates video agent correctly."""
        agent = await create_enhanced_video_generation_agent()
        
        assert isinstance(agent, EnhancedVideoGenerationAgent)


class TestEnhancedImageGenerationAgent:
    """Test Enhanced Image Generation Agent with Imagen 3.0."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that the enhanced image agent initializes correctly."""
        agent = EnhancedImageGenerationAgent()
        
        assert agent is not None
        assert hasattr(agent, 'circuit_breaker')
        assert hasattr(agent, 'cost_controller')
        assert hasattr(agent, 'cache_manager')
        assert agent.circuit_breaker is not None
        assert agent.cost_controller is not None
        assert agent.cache_manager is not None
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self):
        """Test circuit breaker pattern implementation."""
        agent = EnhancedImageGenerationAgent()
        
        # Test initial state
        assert agent.circuit_breaker.can_execute() is True
        assert agent.circuit_breaker.state == "CLOSED"
        
        # Test recording success
        agent.circuit_breaker.record_success()
        assert agent.circuit_breaker.failure_count == 0
        assert agent.circuit_breaker.state == "CLOSED"
        
        # Test recording failures
        for _ in range(3):
            agent.circuit_breaker.record_failure()
        
        assert agent.circuit_breaker.failure_count == 3
    
    @pytest.mark.asyncio
    async def test_cost_controller(self):
        """Test cost controller functionality."""
        agent = EnhancedImageGenerationAgent()
        
        # Test initial limits
        assert agent.cost_controller.can_generate_image() is True
        
        # Test daily stats
        stats = agent.cost_controller.get_daily_stats()
        assert 'date' in stats
        assert 'images_generated' in stats
        assert 'daily_limit' in stats
        assert 'estimated_cost' in stats
        assert 'remaining_quota' in stats
    
    @pytest.mark.asyncio
    async def test_generation_stats(self):
        """Test generation statistics."""
        agent = EnhancedImageGenerationAgent()
        
        stats = agent.get_generation_stats()
        assert 'cost_stats' in stats
        assert 'circuit_breaker_state' in stats
        assert 'circuit_breaker_failures' in stats
    
    @pytest.mark.asyncio
    async def test_factory_function(self):
        """Test the factory function creates image agent correctly."""
        agent = await create_enhanced_image_generation_agent()
        
        assert isinstance(agent, EnhancedImageGenerationAgent)


class TestEnhancedSocialMediaAgent:
    """Test Enhanced Social Media Agent with OAuth."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that the enhanced social media agent initializes correctly."""
        agent = EnhancedSocialMediaAgent()
        
        assert agent is not None
        assert hasattr(agent, 'token_manager')
        assert hasattr(agent, 'linkedin_publisher')
        assert hasattr(agent, 'twitter_publisher')
        assert agent.token_manager is not None
        assert agent.linkedin_publisher is not None
        assert agent.twitter_publisher is not None
    
    @pytest.mark.asyncio
    async def test_oauth_flow_initiation(self):
        """Test OAuth flow initiation for different platforms."""
        agent = EnhancedSocialMediaAgent()
        
        # Test unsupported platform
        result = agent.initiate_oauth_flow("unsupported", "test_user")
        assert result["success"] is False
        assert "Unsupported platform" in result["error"]
    
    @pytest.mark.asyncio
    async def test_connection_status(self):
        """Test connection status checking."""
        agent = EnhancedSocialMediaAgent()
        
        status = agent.get_connection_status("test_user")
        
        # Should return status for all platforms
        expected_platforms = ['linkedin', 'twitter', 'facebook', 'instagram']
        for platform in expected_platforms:
            assert platform in status
            assert 'connected' in status[platform]
            assert status[platform]['connected'] is False  # No tokens stored
    
    @pytest.mark.asyncio
    async def test_token_manager(self):
        """Test token manager functionality."""
        agent = EnhancedSocialMediaAgent()
        
        # Test getting non-existent token
        token = agent.token_manager.get_token("test_user", "linkedin")
        assert token is None
        
        # Test storing and retrieving token
        test_token_data = {
            "access_token": "test_token",
            "expires_at": "2025-12-31T23:59:59"
        }
        
        agent.token_manager.store_token("test_user", "linkedin", test_token_data)
        retrieved_token = agent.token_manager.get_token("test_user", "linkedin")
        
        assert retrieved_token is not None
        assert retrieved_token["access_token"] == "test_token"
    
    @pytest.mark.asyncio
    async def test_factory_function(self):
        """Test the factory function creates social media agent correctly."""
        agent = await create_enhanced_social_media_agent()
        
        assert isinstance(agent, EnhancedSocialMediaAgent)


class TestEnhancedAgentsIntegration:
    """Test integration between enhanced agents."""
    
    @pytest.mark.asyncio
    async def test_all_agents_importable(self):
        """Test that all enhanced agents can be imported and created."""
        # Test all factory functions
        orchestrator = await create_enhanced_marketing_orchestrator()
        video_agent = await create_enhanced_video_generation_agent()
        image_agent = await create_enhanced_image_generation_agent()
        social_agent = await create_enhanced_social_media_agent()
        
        assert isinstance(orchestrator, EnhancedMarketingOrchestrator)
        assert isinstance(video_agent, EnhancedVideoGenerationAgent)
        assert isinstance(image_agent, EnhancedImageGenerationAgent)
        assert isinstance(social_agent, EnhancedSocialMediaAgent)
    
    @pytest.mark.asyncio
    async def test_orchestrator_has_enhanced_agents(self):
        """Test that orchestrator includes enhanced sub-agents."""
        orchestrator = EnhancedMarketingOrchestrator()
        
        # Check that sub-agents are properly initialized
        assert orchestrator.business_analysis_agent is not None
        assert orchestrator.content_generation_agent is not None
        assert orchestrator.visual_content_agent is not None
        assert orchestrator.social_media_agent is not None
        
        # Check agent names
        assert orchestrator.business_analysis_agent.name == "business_analysis_agent"
        assert orchestrator.content_generation_agent.name == "content_generation_agent"
        assert orchestrator.visual_content_agent.name == "visual_content_agent"
        assert orchestrator.social_media_agent.name == "social_media_agent"


# Integration test markers
@pytest.mark.integration
class TestPhase1Implementation:
    """Integration tests for Phase 1 implementation completeness."""
    
    @pytest.mark.asyncio
    async def test_phase1_components_complete(self):
        """Test that all Phase 1 components are implemented and functional."""
        
        # EPIC 14: ADK Framework Modernization
        orchestrator = await create_enhanced_marketing_orchestrator()
        assert orchestrator.memory_service is not None
        
        # EPIC 15: Video Generation
        video_agent = await create_enhanced_video_generation_agent()
        assert video_agent.generation_queue is not None
        assert video_agent.storage_manager is not None
        
        # EPIC 16: Social Media Publishing
        social_agent = await create_enhanced_social_media_agent()
        assert social_agent.token_manager is not None
        assert social_agent.linkedin_publisher is not None
        assert social_agent.twitter_publisher is not None
        
        # EPIC 17: Image Generation
        image_agent = await create_enhanced_image_generation_agent()
        assert image_agent.circuit_breaker is not None
        assert image_agent.cost_controller is not None
        assert image_agent.cache_manager is not None
    
    @pytest.mark.asyncio
    async def test_no_mock_implementations(self):
        """Test that Phase 1 agents have real implementations, not mocks."""
        
        # Test that enhanced agents are using real classes, not mocks
        orchestrator = await create_enhanced_marketing_orchestrator()
        assert not isinstance(orchestrator, Mock)
        assert not isinstance(orchestrator.memory_service, Mock)
        
        video_agent = await create_enhanced_video_generation_agent()
        assert not isinstance(video_agent, Mock)
        assert not isinstance(video_agent.storage_manager, Mock)
        
        image_agent = await create_enhanced_image_generation_agent()
        assert not isinstance(image_agent, Mock)
        assert not isinstance(image_agent.circuit_breaker, Mock)
        
        social_agent = await create_enhanced_social_media_agent()
        assert not isinstance(social_agent, Mock)
        assert not isinstance(social_agent.token_manager, Mock)