#!/usr/bin/env python3
"""
Complete User Journey Test for Enhanced V2 API
Tests the full workflow and A2A messaging capabilities
"""

import requests
import json
import time
from datetime import datetime

def test_complete_user_journey():
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Complete Enhanced V2 API User Journey")
    print("=" * 60)
    
    # Step 1: Check system health
    print("1️⃣ Checking enhanced system health...")
    health_response = requests.get(f"{base_url}/api/v2/campaigns/health")
    print(f"   Health Status: {health_response.status_code}")
    
    if health_response.status_code == 200:
        health_data = health_response.json()
        print(f"   Version: {health_data['version']}")
        print(f"   Features: {', '.join(health_data['features'])}")
        print(f"   Registered Agents: {health_data['stats']['message_bus']['registered_agents']}")
    
    # Step 2: Get initial memory stats
    print("\n2️⃣ Getting initial memory statistics...")
    stats_response = requests.get(f"{base_url}/api/v2/campaigns/debug/memory-stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"   Active Agents: {stats['stats']['message_bus']['active_agents']}")
        print(f"   Total Contexts: {stats['stats']['memory_service']['total_contexts']}")
    
    # Step 3: Create enhanced campaign
    print("\n3️⃣ Creating enhanced campaign with A2A processing...")
    campaign_payload = {
        "campaign_name": "Full Journey Test Campaign",
        "campaign_description": "Complete user journey test for ADK v1.6+ features",
        "business_url": "https://techstartup.example.com",
        "target_platforms": ["linkedin", "twitter"],
        "campaign_objectives": ["increase_brand_awareness", "generate_leads"]
    }
    
    create_response = requests.post(
        f"{base_url}/api/v2/campaigns/create",
        json=campaign_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if create_response.status_code == 200:
        create_data = create_response.json()
        campaign_id = create_data["campaign_id"]
        print(f"   Campaign Created: {campaign_id}")
        print(f"   Initial Status: {create_data['status']}")
    else:
        print(f"   ❌ Campaign creation failed: {create_response.status_code}")
        return
    
    # Step 4: Monitor campaign progress
    print("\n4️⃣ Monitoring campaign progress...")
    for i in range(3):
        print(f"   Check #{i+1}...")
        status_response = requests.get(f"{base_url}/api/v2/campaigns/{campaign_id}/status")
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   Completion: {status_data['completion_percentage']:.1f}%")
            print(f"   Completed Stages: {len(status_data['completed_stages'])}")
            print(f"   Active Agents: {len(status_data['active_agents'])}")
        
        time.sleep(2)
    
    # Step 5: Check A2A message history
    print("\n5️⃣ Checking A2A message history...")
    messages_response = requests.get(f"{base_url}/api/v2/campaigns/{campaign_id}/messages")
    
    if messages_response.status_code == 200:
        messages_data = messages_response.json()
        print(f"   Total Messages: {messages_data['total_messages']}")
        
        if messages_data['total_messages'] > 0:
            print("   Recent A2A Messages:")
            for msg in messages_data['messages'][:3]:  # Show first 3 messages
                print(f"   - {msg['sender']} -> {', '.join(msg['recipients'])}")
                print(f"     Type: {msg['message_type']} at {msg['timestamp']}")
        else:
            print("   No A2A messages yet (generation may still be starting)")
    
    # Step 6: Get campaign context
    print("\n6️⃣ Retrieving campaign context (zero fidelity loss)...")
    context_response = requests.get(f"{base_url}/api/v2/campaigns/{campaign_id}/context")
    
    if context_response.status_code == 200:
        context_data = context_response.json()
        print(f"   Context Version: {context_data['metadata']['version']}")
        print(f"   Campaign Persistent: {context_data['context']['persistent']}")
        print(f"   Business Analysis Status: {'✅' if context_data['context']['business_analysis'] else '⏳'}")
        print(f"   Content Strategy Status: {'✅' if context_data['context']['content_strategy'] else '⏳'}")
    
    # Step 7: List all campaigns with memory stats
    print("\n7️⃣ Listing all campaigns with enhanced statistics...")
    list_response = requests.get(f"{base_url}/api/v2/campaigns/list")
    
    if list_response.status_code == 200:
        list_data = list_response.json()
        print(f"   Total Campaigns: {list_data['total_count']}")
        print(f"   Cache Hit Ratio: {list_data['memory_stats']['memory_service']['cache_hit_ratio']:.1%}")
        print(f"   Message Bus Active Agents: {list_data['memory_stats']['message_bus']['active_agents']}")
    
    # Final assessment
    print("\n" + "=" * 60)
    print("📊 USER JOURNEY ASSESSMENT")
    print("=" * 60)
    
    checks = [
        ("Enhanced Health Check", health_response.status_code == 200),
        ("Memory Statistics", stats_response.status_code == 200),
        ("Campaign Creation", create_response.status_code == 200),
        ("Campaign Status", status_response.status_code == 200),
        ("A2A Messages", messages_response.status_code == 200),
        ("Context Retrieval", context_response.status_code == 200),
        ("Campaign Listing", list_response.status_code == 200),
    ]
    
    passed = sum(1 for _, success in checks if success)
    total = len(checks)
    
    print(f"✅ Endpoint Tests: {passed}/{total} PASSED")
    
    # Validate ADK v1.6+ features
    adk_features = []
    if health_response.status_code == 200:
        health_data = health_response.json()
        if "A2A messaging" in health_data.get('features', []):
            adk_features.append("A2A Messaging")
        if "Persistent memory" in health_data.get('features', []):
            adk_features.append("Persistent Memory")
        if "Structured context" in health_data.get('features', []):
            adk_features.append("Structured Context")
        if "Event-driven coordination" in health_data.get('features', []):
            adk_features.append("Event-driven Coordination")
    
    print(f"🎯 ADK v1.6+ Features: {len(adk_features)}/4 VERIFIED")
    for feature in adk_features:
        print(f"   ✅ {feature}")
    
    # Agent registration validation
    if stats_response.status_code == 200:
        stats = stats_response.json()
        agent_count = stats['stats']['message_bus']['active_agents']
        print(f"🤖 Active Agents: {agent_count} REGISTERED")
        
        agent_details = stats['stats']['message_bus'].get('agent_details', {})
        for agent_name, details in agent_details.items():
            capabilities = details.get('metadata', {}).get('capabilities', [])
            print(f"   ✅ {agent_name}: {', '.join(capabilities)}")
    
    print(f"\n🎉 Enhanced V2 API User Journey: {'COMPLETE' if passed == total else 'PARTIAL'}")
    
    return {
        "endpoint_tests": f"{passed}/{total}",
        "adk_features": f"{len(adk_features)}/4",
        "campaign_id": campaign_id if 'campaign_id' in locals() else None,
        "success": passed == total and len(adk_features) == 4
    }

if __name__ == "__main__":
    result = test_complete_user_journey()
    print(f"\nFinal Result: {json.dumps(result, indent=2)}")