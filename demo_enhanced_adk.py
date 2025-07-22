#!/usr/bin/env python3
"""
FILENAME: demo_enhanced_adk.py
DESCRIPTION/PURPOSE: Demo script for ADK v1.6+ enhanced capabilities
Author: JP + Claude Code + 2025-01-20

This script demonstrates the enhanced ADK v1.6+ features including:
- Zero fidelity loss campaign context
- A2A messaging between agents
- Persistent memory across sessions
- Event-driven coordination
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.agents.enhanced_marketing_orchestrator_v2 import (
    create_enhanced_marketing_orchestrator
)
from backend.models.campaign_context import (
    CampaignContext,
    GenerationEventType,
    SocialPlatform
)
from backend.messaging.a2a_messaging import (
    initialize_message_bus,
    get_message_bus
)

async def demo_context_fidelity():
    """Demonstrate zero fidelity loss in campaign context"""
    
    print("\n🎯 DEMO: Campaign Context Fidelity")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = await create_enhanced_marketing_orchestrator("./demo_sessions")
    
    # Create test campaign
    campaign_id = f"demo_fidelity_{int(time.time())}"
    business_input = {
        "campaign_name": "ADK v1.6+ Fidelity Demo",
        "description": "Demonstrating zero data loss in context handling",
        "business_url": "https://example-ai-startup.com",
        "target_platforms": [SocialPlatform.LINKEDIN, SocialPlatform.TWITTER],
        "campaign_objectives": ["Brand awareness", "Lead generation"]
    }
    
    print(f"📋 Creating campaign: {campaign_id}")
    
    # Generate campaign
    start_time = time.time()
    final_context = await orchestrator.generate_campaign(campaign_id, business_input)
    duration = time.time() - start_time
    
    print(f"⏱️  Campaign generation took: {duration:.2f} seconds")
    print(f"📊 Campaign completion: {final_context.get_completion_percentage():.1f}%")
    print(f"🔢 Context version: {final_context.version}")
    print(f"📝 Generation events: {len(final_context.generation_history)}")
    
    # Demonstrate context serialization/deserialization
    from backend.models.campaign_context import serialize_campaign_context, deserialize_campaign_context
    
    print("\n🔄 Testing context serialization fidelity...")
    serialized = serialize_campaign_context(final_context)
    restored_context = deserialize_campaign_context(serialized)
    
    # Verify fidelity
    fidelity_checks = [
        ("Campaign ID", final_context.campaign_id == restored_context.campaign_id),
        ("Version", final_context.version == restored_context.version),
        ("Business Analysis", final_context.business_analysis == restored_context.business_analysis),
        ("Content Strategy", final_context.content_strategy == restored_context.content_strategy),
        ("Generation History", len(final_context.generation_history) == len(restored_context.generation_history)),
        ("Completed Stages", final_context.completed_stages == restored_context.completed_stages)
    ]
    
    print("\n✅ Fidelity Check Results:")
    for check_name, passed in fidelity_checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check_name}: {status}")
    
    all_passed = all(passed for _, passed in fidelity_checks)
    print(f"\n🎯 Overall Fidelity: {'✅ 100% PRESERVED' if all_passed else '❌ DATA LOSS DETECTED'}")
    
    return campaign_id, final_context

async def demo_a2a_messaging():
    """Demonstrate A2A messaging between agents"""
    
    print("\n💬 DEMO: A2A Messaging System")
    print("=" * 50)
    
    # Get message bus
    message_bus = get_message_bus()
    
    # Show message bus stats
    stats = message_bus.get_agent_stats()
    print(f"📊 Registered agents: {stats['active_agents']}")
    print(f"📨 Total messages sent: {stats['total_messages']}")
    
    # Show recent messages
    recent_messages = message_bus.get_message_history(limit=5)
    
    print(f"\n📬 Recent A2A Messages ({len(recent_messages)} shown):")
    for i, message in enumerate(recent_messages[-5:], 1):
        print(f"  {i}. {message.sender} → {message.recipients}")
        print(f"     Type: {message.message_type.value}")
        print(f"     Time: {message.timestamp.strftime('%H:%M:%S')}")
        print(f"     Campaign: {message.campaign_id}")
        if message.delivered_to:
            print(f"     Delivered: {len(message.delivered_to)} recipients")
        print()

async def demo_persistent_memory():
    """Demonstrate persistent memory across sessions"""
    
    print("\n🧠 DEMO: Persistent Memory Service")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = await create_enhanced_marketing_orchestrator("./demo_sessions")
    
    # Show memory stats
    memory_stats = await orchestrator.get_memory_stats()
    
    print(f"📊 Memory Service Statistics:")
    print(f"   Total contexts: {memory_stats['memory_service']['total_contexts']}")
    print(f"   Cached contexts: {memory_stats['memory_service']['cached_contexts']}")
    print(f"   Storage backend: {memory_stats['memory_service']['storage_backend']}")
    print(f"   Base path: {memory_stats['memory_service']['base_path']}")
    
    # List existing campaigns
    campaigns = await orchestrator.list_campaigns()
    print(f"\n📋 Existing campaigns: {len(campaigns)}")
    
    for campaign_id in campaigns[-3:]:  # Show last 3
        status = await orchestrator.get_campaign_status(campaign_id)
        if status:
            print(f"   • {campaign_id}")
            print(f"     Completion: {status['completion_percentage']:.1f}%")
            print(f"     Last updated: {status['last_updated'][:19]}")
            print(f"     Version: {status['version']}")

async def demo_event_driven_coordination():
    """Demonstrate event-driven agent coordination"""
    
    print("\n⚡ DEMO: Event-Driven Coordination")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = await create_enhanced_marketing_orchestrator("./demo_sessions")
    
    # Create new campaign to show coordination
    campaign_id = f"demo_coordination_{int(time.time())}"
    business_input = {
        "campaign_name": "Event-Driven Demo",
        "description": "Demonstrating agent coordination",
        "business_url": "https://example-coordination.com"
    }
    
    print(f"🚀 Starting coordinated campaign: {campaign_id}")
    print("🔄 Watch for real-time agent coordination...")
    
    # Monitor progress
    start_time = time.time()
    
    # Start campaign generation
    campaign_task = asyncio.create_task(
        orchestrator.generate_campaign(campaign_id, business_input)
    )
    
    # Monitor progress in real-time
    while not campaign_task.done():
        await asyncio.sleep(0.5)
        
        # Get current status
        status = await orchestrator.get_campaign_status(campaign_id)
        if status:
            elapsed = time.time() - start_time
            print(f"⏱️  {elapsed:.1f}s - Progress: {status['completion_percentage']:.1f}% - "
                  f"Stages: {len(status['completed_stages'])}")
            
            # Show latest event
            if status['generation_history']:
                latest_event = status['generation_history'][-1]
                print(f"   Latest: {latest_event['agent_name']} - {latest_event['event_type']}")
    
    # Get final result
    final_context = await campaign_task
    final_time = time.time() - start_time
    
    print(f"\n✅ Coordination complete in {final_time:.2f} seconds")
    print(f"📊 Final completion: {final_context.get_completion_percentage():.1f}%")
    print(f"🎭 Agents involved: {len(set(event.agent_name for event in final_context.generation_history))}")

async def demo_performance_comparison():
    """Demonstrate performance improvements"""
    
    print("\n⚡ DEMO: Performance Comparison")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = await create_enhanced_marketing_orchestrator("./demo_sessions")
    
    print("🏁 Running performance test...")
    
    # Test concurrent campaign generation
    num_campaigns = 3
    campaign_tasks = []
    
    start_time = time.time()
    
    for i in range(num_campaigns):
        campaign_id = f"perf_test_{i}_{int(time.time())}"
        business_input = {
            "campaign_name": f"Performance Test Campaign {i+1}",
            "description": f"Testing concurrent generation {i+1}",
            "business_url": f"https://example-perf-{i}.com"
        }
        
        task = orchestrator.generate_campaign(campaign_id, business_input)
        campaign_tasks.append(task)
    
    print(f"⚡ Started {num_campaigns} concurrent campaigns...")
    
    # Wait for all to complete
    results = await asyncio.gather(*campaign_tasks)
    
    total_time = time.time() - start_time
    avg_time = total_time / num_campaigns
    
    print(f"✅ All campaigns completed!")
    print(f"⏱️  Total time: {total_time:.2f} seconds")
    print(f"📊 Average per campaign: {avg_time:.2f} seconds")
    print(f"🚀 Throughput: {num_campaigns / total_time:.2f} campaigns/second")
    
    # Show memory efficiency
    memory_stats = await orchestrator.get_memory_stats()
    print(f"🧠 Memory efficiency:")
    print(f"   Total contexts: {memory_stats['memory_service']['total_contexts']}")
    print(f"   Cache hit ratio: {memory_stats['memory_service']['cache_hit_ratio']:.2%}")

async def main():
    """Main demo function"""
    
    print("🚀 ADK v1.6+ Enhanced Capabilities Demo")
    print("=" * 60)
    print("Demonstrating advanced features:")
    print("• Zero fidelity loss campaign context")
    print("• A2A messaging between agents")
    print("• Persistent memory across sessions") 
    print("• Event-driven coordination")
    print("• Performance improvements")
    print("=" * 60)
    
    try:
        # Initialize message bus
        await initialize_message_bus()
        print("✅ Message bus initialized")
        
        # Run demos
        await demo_context_fidelity()
        await demo_a2a_messaging()
        await demo_persistent_memory()
        await demo_event_driven_coordination()
        await demo_performance_comparison()
        
        print("\n🎉 ADK v1.6+ Demo Complete!")
        print("=" * 60)
        print("✅ All enhanced features demonstrated successfully")
        print("📋 Check './demo_sessions' for persistent campaign data")
        print("🔍 Review logs for detailed A2A message flow")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())