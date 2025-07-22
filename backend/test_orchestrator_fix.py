#!/usr/bin/env python3
"""
Test script to verify marketing orchestrator URL analysis integration.
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(__file__))

from agents.marketing_orchestrator import _comprehensive_business_analysis
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_url_analysis_integration():
    """Test that the marketing orchestrator uses URLAnalysisAgent when URLs are provided"""
    
    print("\n=== TESTING URL ANALYSIS INTEGRATION ===")
    print("Testing with liatvictoriaphotography.co.uk")
    
    # Test with photography business URL
    business_analysis = await _comprehensive_business_analysis(
        business_description="Liat Victoria Photography offers professional photography services",
        target_audience="Couples, families, professionals seeking high-quality photography",
        objective="increase bookings and brand awareness",
        campaign_type="awareness",
        business_website="https://liatvictoriaphotography.co.uk",
        about_page_url=None,
        product_service_url=None
    )
    
    print(f"\nBusiness Analysis Result:")
    print(f"Company: {business_analysis.get('company_name', 'N/A')}")
    print(f"Industry: {business_analysis.get('industry', 'N/A')}")
    
    # Check for campaign guidance and suggested tags
    campaign_guidance = business_analysis.get('campaign_guidance', {})
    suggested_tags = campaign_guidance.get('suggested_tags', [])
    
    print(f"Campaign Guidance Keys: {list(campaign_guidance.keys())}")
    print(f"Suggested Tags: {suggested_tags}")
    
    # Check if we got photography-specific tags
    photography_specific_tags = [tag for tag in suggested_tags if any(keyword in tag.lower() for keyword in ['photo', 'portrait', 'wedding', 'artistic'])]
    
    if photography_specific_tags:
        print(f"✅ SUCCESS: Found photography-specific tags: {photography_specific_tags}")
        return True
    else:
        print(f"❌ FAILED: No photography-specific tags found. Got generic tags: {suggested_tags}")
        return False


async def test_fallback_behavior():
    """Test fallback to description analysis when no URLs provided"""
    
    print("\n=== TESTING FALLBACK BEHAVIOR ===")
    print("Testing without URLs (should use description analysis)")
    
    business_analysis = await _comprehensive_business_analysis(
        business_description="Photography business offering wedding and portrait services",
        target_audience="Couples and individuals",
        objective="increase bookings",
        campaign_type="service",
        # No URLs provided
    )
    
    print(f"Company: {business_analysis.get('company_name', 'N/A')}")
    print(f"Industry: {business_analysis.get('industry', 'N/A')}")
    
    # Should still work, but with less detailed analysis
    if business_analysis and business_analysis.get('company_name'):
        print("✅ SUCCESS: Fallback behavior working")
        return True
    else:
        print("❌ FAILED: Fallback behavior not working")
        return False


async def main():
    print("Testing Marketing Orchestrator URL Analysis Integration")
    print("=" * 60)
    
    # Test 1: URL analysis integration
    success1 = await test_url_analysis_integration()
    
    # Test 2: Fallback behavior
    success2 = await test_fallback_behavior()
    
    if success1 and success2:
        print("\n✅ ALL TESTS PASSED - Marketing orchestrator is now properly integrated with URLAnalysisAgent!")
    else:
        print("\n❌ SOME TESTS FAILED - Check the integration")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())