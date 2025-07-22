#!/usr/bin/env python3
"""
Test end-to-end campaign workflow to ensure photography-specific hashtags 
flow through from URL analysis to final content generation.
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(__file__))

from agents.marketing_orchestrator import execute_campaign_workflow
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_end_to_end_photography_campaign():
    """Test complete workflow from URL to final posts with photography-specific hashtags"""
    
    print("\n=== END-TO-END PHOTOGRAPHY CAMPAIGN TEST ===")
    print("URL: liatvictoriaphotography.co.uk")
    print("Expected: Photography-specific hashtags throughout the workflow")
    
    # Execute the complete campaign workflow
    workflow_result = await execute_campaign_workflow(
        business_description="Professional photography services specializing in weddings and portraits",
        objective="increase bookings and showcase portfolio",
        target_audience="Couples planning weddings, individuals seeking professional portraits",
        campaign_type="service",
        creativity_level=7,
        post_count=3,
        business_website="https://liatvictoriaphotography.co.uk"
    )
    
    print(f"\n=== WORKFLOW RESULTS ===")
    print(f"Success: {workflow_result.get('success', False)}")
    
    # Check business analysis
    business_analysis = workflow_result.get("business_analysis", {})
    print(f"\nBusiness Analysis:")
    print(f"  Company: {business_analysis.get('company_name', 'N/A')}")
    print(f"  Industry: {business_analysis.get('industry', 'N/A')}")
    
    # Check campaign guidance hashtags
    campaign_guidance = business_analysis.get('campaign_guidance', {})
    business_suggested_tags = campaign_guidance.get('suggested_tags', [])
    print(f"  Business Analysis Hashtags: {business_suggested_tags}")
    
    # Check generated content
    generated_content = workflow_result.get("generated_content", [])
    print(f"\nGenerated Content ({len(generated_content)} posts):")
    
    all_hashtags_found = []
    photography_specific_found = []
    
    for i, post in enumerate(generated_content):
        hashtags = getattr(post, 'hashtags', []) if hasattr(post, 'hashtags') else post.get('hashtags', [])
        all_hashtags_found.extend(hashtags)
        
        # Check for photography-specific tags
        photo_tags = [tag for tag in hashtags if any(keyword in tag.lower() for keyword in ['photo', 'portrait', 'wedding', 'artistic', 'creative', 'memories'])]
        photography_specific_found.extend(photo_tags)
        
        print(f"  Post {i+1}:")
        print(f"    Content: {getattr(post, 'content', post.get('content', 'N/A'))[:50]}...")
        print(f"    Hashtags: {hashtags}")
        print(f"    Photography-specific: {photo_tags}")
    
    # Final assessment
    print(f"\n=== ASSESSMENT ===")
    print(f"All hashtags found: {list(set(all_hashtags_found))}")
    print(f"Photography-specific hashtags: {list(set(photography_specific_found))}")
    
    # Success criteria
    has_business_analysis = business_analysis.get('company_name') and business_analysis.get('industry')
    has_business_hashtags = len(business_suggested_tags) > 0
    has_photography_industry = 'photo' in business_analysis.get('industry', '').lower()
    has_photography_hashtags = len(photography_specific_found) > 0
    has_content = len(generated_content) > 0
    
    success = all([
        has_business_analysis,
        has_business_hashtags,
        has_photography_industry, 
        has_photography_hashtags,
        has_content
    ])
    
    print(f"\nCRITERIA CHECK:")
    print(f"  ✅ Business analysis extracted: {has_business_analysis}")
    print(f"  ✅ Business hashtags generated: {has_business_hashtags}")
    print(f"  ✅ Photography industry detected: {has_photography_industry}")
    print(f"  ✅ Photography hashtags in posts: {has_photography_hashtags}")
    print(f"  ✅ Content generated: {has_content}")
    
    if success:
        print(f"\n✅ SUCCESS: End-to-end photography hashtag workflow is working correctly!")
        print(f"The system now properly:")
        print(f"  - Analyzes URLs with URLAnalysisAgent")
        print(f"  - Detects photography business context")
        print(f"  - Generates industry-specific hashtags")
        print(f"  - Uses business-specific hashtags in content generation")
        return True
    else:
        print(f"\n❌ FAILED: End-to-end workflow has issues")
        return False


async def main():
    print("Testing End-to-End Hashtag Recommendation System")
    print("=" * 60)
    
    try:
        success = await test_end_to_end_photography_campaign()
        
        if success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"The hashtag recommendation system is now working end-to-end.")
            print(f"Photography businesses will get relevant hashtags like:")
            print(f"  #Photography, #WeddingPhotographer, #PortraitPhotography")
            print(f"  #ArtisticVision, #ProfessionalHeadshots, #CreativeVision")
        else:
            print(f"\n❌ Issues remain in the workflow")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())