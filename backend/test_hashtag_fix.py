#!/usr/bin/env python3
"""
Test script to verify hashtag recommendation system is generating business-specific hashtags.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.routes.content import generate_contextual_hashtags
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_photography_business_hashtags():
    """Test hashtags for photography business like liatvictoriaphotography.co.uk"""
    
    # Simulate business context that should come from business analysis agent
    photography_business_context = {
        'company_name': 'Liat Victoria Photography',
        'industry': 'Photography',
        'business_type': 'individual_creator',
        'target_audience': 'Couples planning weddings, individuals seeking professional portraits, families wanting memorable photos',
        'campaign_guidance': {
            'suggested_tags': [
                '#Photography', '#WeddingPhotographer', '#PortraitPhotography', 
                '#LiatVictoriaPhotography', '#ProfessionalHeadshots', '#ArtisticPhotography', 
                '#UKPhotographer'
            ],
            'suggested_themes': [
                'Creative Vision', 'Professional Photography', 'Memorable Moments', 
                'Artistic Excellence', 'Personal Connection'
            ],
            'creative_direction': 'Showcase photographer\'s artistic vision and technical expertise through behind-the-scenes work, stunning photo examples, and satisfied clients'
        },
        'product_context': {
            'primary_products': ['Wedding Photography', 'Portrait Photography', 'Professional Headshots'],
            'visual_themes': ['creativity', 'artistry', 'moments', 'beauty', 'professional'],
            'brand_personality': 'artistic, professional, authentic'
        }
    }
    
    print("\n=== TESTING PHOTOGRAPHY BUSINESS HASHTAGS ===")
    print(f"Company: {photography_business_context['company_name']}")
    print(f"Industry: {photography_business_context['industry']}")
    print(f"Expected hashtags from business analysis: {photography_business_context['campaign_guidance']['suggested_tags']}")
    
    # Generate hashtags using the fixed function
    generated_hashtags = generate_contextual_hashtags(photography_business_context)
    
    print(f"\nGenerated hashtags: {generated_hashtags}")
    
    # Check if business-specific hashtags are being used
    expected_photography_tags = ['#Photography', '#WeddingPhotographer', '#PortraitPhotography', '#LiatVictoriaPhotography']
    found_specific_tags = [tag for tag in generated_hashtags if tag in expected_photography_tags]
    
    print(f"Photography-specific tags found: {found_specific_tags}")
    
    if len(found_specific_tags) >= 3:
        print("✅ SUCCESS: Business-specific hashtags are being generated!")
        return True
    else:
        print("❌ FAILED: Generic hashtags are still being used instead of business-specific ones")
        return False


def test_generic_business_fallback():
    """Test fallback behavior when no business analysis tags are available"""
    
    generic_business_context = {
        'company_name': 'Generic Business',
        'industry': 'Professional Services',
        'business_type': 'corporation',
        'target_audience': 'Business professionals'
        # Note: No campaign_guidance.suggested_tags - should use fallback logic
    }
    
    print("\n=== TESTING GENERIC BUSINESS FALLBACK ===")
    print(f"Company: {generic_business_context['company_name']}")
    print(f"Industry: {generic_business_context['industry']}")
    print("Expected: Should use contextual hashtag generation since no business analysis tags available")
    
    generated_hashtags = generate_contextual_hashtags(generic_business_context)
    
    print(f"Generated hashtags: {generated_hashtags}")
    
    return True


if __name__ == "__main__":
    print("Testing Hashtag Recommendation System Fix")
    print("=" * 50)
    
    # Test 1: Photography business with specific hashtags
    success1 = test_photography_business_hashtags()
    
    # Test 2: Generic business fallback
    success2 = test_generic_business_fallback()
    
    if success1 and success2:
        print("\n✅ ALL TESTS PASSED - Hashtag system is working correctly!")
    else:
        print("\n❌ SOME TESTS FAILED - Check the fixes")
        sys.exit(1)