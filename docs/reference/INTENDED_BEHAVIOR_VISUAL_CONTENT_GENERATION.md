# Intended Behavior: Visual Content Generation

**Document Version**: 1.0  
**Date**: 2025-07-23  
**Author**: JP  
**Purpose**: Define the exact intended behavior for image and video content generation to prevent regressions

## Executive Summary

This document specifies the intended behavior for visual content generation in the video-venture-launch marketing campaign system. **The primary requirement is that all visual content must be contextually relevant to the specific campaign and business being promoted.**

## Critical Requirements

### ✅ MUST DO (Required Behavior)

1. **Contextual Relevance**: All generated images and videos MUST be contextually relevant to:
   - The specific business being promoted
   - The campaign objective 
   - The post content/message
   - The target audience
   - The industry/business type

2. **Real AI Generation**: When a campaign is active (not demo mode):
   - MUST call real AI generation APIs (Imagen 3.0 for images, Veo 3.0 for videos)
   - MUST pass comprehensive business context to generation prompts
   - MUST enhance prompts with campaign guidance and visual style preferences

3. **Business-Specific Content**: Generated visuals MUST reflect:
   - Company name and branding when appropriate
   - Industry-specific imagery (e.g., restaurant imagery for restaurants, office imagery for consulting)
   - Product-specific imagery when promoting specific products
   - Professional context matching the business type

4. **Error Handling**: When generation fails:
   - MUST return error state or null URLs
   - MUST NOT fall back to irrelevant placeholder content
   - MAY show loading states or retry options
   - MUST clearly indicate to users that generation failed

### ❌ MUST NOT DO (Forbidden Behavior)

1. **Generic Placeholder Content**: MUST NOT show:
   - Random stock photos unrelated to the business
   - Nature/landscape images for business campaigns
   - Generic people in generic settings without business context
   - Any Unsplash URLs in production campaigns: `https://images.unsplash.com/*`
   - Any placeholder service URLs: `https://via.placeholder.com/*`, `https://picsum.photos/*`

2. **Demo Content in Production**: MUST NOT show demo content when:
   - A real campaign has been created
   - Business context is available
   - Generation APIs are functional

3. **Context Mismatches**: MUST NOT generate:
   - Mountain landscapes for technology consulting campaigns
   - Generic office workers for restaurant campaigns  
   - Outdoor nature scenes for software/SaaS campaigns
   - Any visuals that don't relate to the actual business

## Specific Use Cases

### Use Case 1: T-Shirt Business Campaign

**Input:**
- Company: "Creative Threads"
- Product: "Joker T-Shirt" 
- Campaign: "Promote new Joker-themed designs"
- Post: "Check out our awesome Joker-themed t-shirt designs!"

**Expected Visual Generation:**
- ✅ Young adults wearing the Joker t-shirt
- ✅ Close-up of the t-shirt design
- ✅ Urban/street setting showing lifestyle usage
- ✅ Pop culture aesthetic matching Joker theme

**Forbidden Outputs:**
- ❌ Mountain landscapes
- ❌ Generic business meetings
- ❌ Nature photography
- ❌ Unrelated stock photos

### Use Case 2: Restaurant Campaign

**Input:**
- Company: "Bella Vista Restaurant"
- Business: "Upscale Italian restaurant"
- Campaign: "Promote fine dining experience"
- Post: "Experience fine dining at its best"

**Expected Visual Generation:**
- ✅ Elegant restaurant interior
- ✅ Beautifully plated Italian dishes
- ✅ Satisfied customers dining
- ✅ Professional kitchen/chef imagery

**Forbidden Outputs:**
- ❌ Corporate office settings
- ❌ Technology/software imagery
- ❌ Outdoor landscapes
- ❌ Generic stock photos

### Use Case 3: Technology Consulting Campaign

**Input:**
- Company: "TechCorp Solutions"
- Business: "Technology consulting services"
- Campaign: "Generate leads for consulting services"
- Post: "Transform your business with our innovative solutions"

**Expected Visual Generation:**
- ✅ Professional consultants with clients
- ✅ Modern office environments
- ✅ Technology interfaces/screens
- ✅ Business transformation imagery

**Forbidden Outputs:**
- ❌ Restaurant/food imagery
- ❌ Nature/outdoor scenes
- ❌ Generic landscapes
- ❌ Unrelated stock photos

## Technical Implementation Requirements

### Backend API Behavior

1. **Visual Generation Endpoint** (`/api/v1/content/generate-visuals`):
   ```json
   // REQUIRED: Must accept comprehensive business context
   {
     "social_posts": [...],
     "business_context": {
       "company_name": "string",
       "industry": "string", 
       "business_description": "string",
       "product_context": {...},
       "campaign_guidance": {...}
     }
   }
   
   // REQUIRED: Must return contextually relevant URLs or error states
   {
     "posts_with_visuals": [
       {
         "id": "post_1",
         "image_url": "http://localhost:8000/api/v1/content/images/campaign123/business_relevant_image.png",
         // OR null if generation failed
         "image_url": null,
         "image_metadata": {
           "generation_method": "imagen_real|error",
           "status": "success|failed"
         }
       }
     ]
   }
   ```

2. **Prompt Enhancement**: Backend MUST enhance image/video prompts with:
   - Company name and business type
   - Industry-specific context
   - Product-specific details when available
   - Campaign guidance and visual style preferences
   - Target audience considerations

### Frontend Behavior

1. **Ideation Page**:
   - MUST call real generation APIs when campaign context is available
   - MUST display loading states during generation
   - MUST handle generation failures gracefully
   - MAY show demo content ONLY when clearly labeled as "Demo" or "Preview"

2. **Demo Mode** (when no active campaign):
   - MUST clearly label all content as "Demo", "Sample", or "Preview"
   - MAY use placeholder content but with obvious demo indicators
   - SHOULD still demonstrate the system's real capabilities when possible

3. **Error States**:
   - MUST show clear error messages when generation fails
   - MUST provide retry options or alternative actions
   - MUST NOT silently fall back to irrelevant placeholder content

## Quality Assurance Criteria

### Acceptance Criteria for Visual Content

A generated image or video is acceptable if:

1. **Relevance Score ≥ 80%**: Content clearly relates to the business/campaign
2. **Professional Quality**: Appropriate for marketing/promotional use
3. **Context Alignment**: Matches the post text and campaign objective
4. **Brand Appropriateness**: Suitable for the company's brand and industry

### Rejection Criteria for Visual Content

A generated image or video MUST be rejected if:

1. **Irrelevant Content**: Nature/landscape photos for business campaigns
2. **Context Mismatch**: Restaurant imagery for tech companies (unless relevant)
3. **Demo URLs**: Any hardcoded placeholder URLs in production responses
4. **Generic Stock**: Generic business stock photos without specific context

## Monitoring and Validation

### Automated Tests MUST Verify:

1. **No Forbidden URLs**: Tests must fail if demo URLs appear in production
2. **Context Relevance**: Generated prompts include business-specific context
3. **API Integration**: Real generation APIs are called with proper parameters
4. **Error Handling**: Failures return appropriate error states

### Manual QA MUST Verify:

1. **Visual Inspection**: Generated images/videos match campaign context
2. **User Experience**: Demo mode is clearly labeled and doesn't mislead users
3. **Business Alignment**: Content represents the actual business appropriately

## Error Scenarios and Responses

### Scenario 1: API Key Missing
**Behavior**: Return error state, do not show demo URLs
**User Experience**: Clear message about configuration needed

### Scenario 2: Generation API Timeout
**Behavior**: Return null URLs with retry option
**User Experience**: Loading state followed by retry button

### Scenario 3: Content Policy Violation
**Behavior**: Return error with explanation
**User Experience**: Suggestion to modify post content

### Scenario 4: No Business Context Available
**Behavior**: Request additional context or use minimal safe defaults
**User Experience**: Prompt for more business information

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-07-23 | JP | Initial specification following regression analysis |

## Related Documents

- [ADR-020: Visual Content Context Fidelity Requirements](./ADR-020-Visual-Content-Context-Fidelity.md)
- [Test Plan: Visual Content Regression Prevention](../tests/test_visual_content_context_fidelity.py)
- [User Journey: Campaign Creation to Visual Generation](./USER_JOURNEY_VISUAL_CONTENT.md)

---

**⚠️ CRITICAL NOTE**: Any deviation from this intended behavior, especially showing irrelevant placeholder content for real campaigns, constitutes a regression that must be immediately addressed. The system's value proposition depends on contextually relevant visual content generation.