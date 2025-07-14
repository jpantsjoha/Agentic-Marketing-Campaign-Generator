#!/usr/bin/env python3
"""
Simple test script to verify the marketing workflow execution.
Author: JP + 2025-06-15
"""

import asyncio
from agents.marketing_orchestrator import execute_campaign_workflow

async def test_workflow():
    """Test the marketing campaign workflow with mock data."""
    print("🧪 Testing marketing campaign workflow...")
    
    result = await execute_campaign_workflow(
        business_description='AI startup focused on marketing automation',
        objective='Launch new product campaign',
        target_audience='Small business owners',
        campaign_type='product',
        creativity_level=7
    )
    
    print('✅ Campaign workflow test passed')
    print(f'Campaign ID: {result["campaign_id"]}')
    print(f'Generated {len(result["social_posts"])} social media posts')
    print(f'Business Analysis: {result["business_analysis"]["company_name"]}')
    print(f'Processing Time: {result.get("processing_time", "N/A")}s')
    
    return result

if __name__ == "__main__":
    asyncio.run(test_workflow()) 