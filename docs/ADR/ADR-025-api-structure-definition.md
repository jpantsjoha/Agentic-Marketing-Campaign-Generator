# ADR-003: API Structure Definition and Standards

**Date:** 2025-01-16  
**Status:** ACCEPTED  
**Author:** JP  
**Context:** Google ADK Hackathon - AI Marketing Campaign Post Generator

## Context

As we approach the v1.0.0 release, we need consistent API structure definitions to:
- Prevent regression when extending capabilities
- Ensure consistent response formats across all endpoints
- Remove mock implementations in favor of proper error handling
- Maintain professional-grade API standards for hackathon submission

## Decision

### 1. Standard Response Structure

All API responses must follow this structure:

```typescript
// Success Response
{
  "data": T,           // Actual response data
  "metadata": {        // Processing metadata
    "processing_time": number,
    "generation_method": string,
    "agent_used": string,
    "timestamp": string
  },
  "status": "success"
}

// Error Response  
{
  "error": {
    "message": string,
    "code": string,
    "details": object | null
  },
  "status": "error",
  "timestamp": string
}
```

### 2. Content Generation API Structure

#### POST /api/v1/content/generate
```typescript
// Request
{
  "business_context": BusinessAnalysis,
  "campaign_objective": string,
  "creativity_level": number, // 1-10
  "post_count": number,       // 3-15
  "include_hashtags": boolean
}

// Response
{
  "posts": SocialMediaPost[],
  "hashtag_suggestions": string[],
  "generation_metadata": {
    "total_posts": number,
    "creativity_level": number,
    "generation_method": "gemini_batch" | "gemini_fallback" | "error_fallback",
    "generation_time": number,
    "cost_controlled": boolean
  },
  "processing_time": number
}
```

#### POST /api/v1/content/regenerate
```typescript
// Request
{
  "post_type": "text_url" | "text_image" | "text_video",
  "regenerate_count": number, // 1-10
  "business_context": object,
  "creativity_level": number,
  "current_posts": SocialMediaPost[]
}

// Response
{
  "new_posts": SocialMediaPost[],
  "regeneration_metadata": {
    "regenerated_count": number,
    "post_type": string,
    "generation_method": string,
    "creativity_level": number,
    "business_context_used": boolean,
    "cost_controlled": boolean
  },
  "processing_time": number
}
```

### 3. SocialMediaPost Structure

```typescript
{
  "id": string,
  "type": "text_url" | "text_image" | "text_video",
  "content": string,              // 40-120 chars for social media
  "url": string | null,
  "image_prompt": string | null,
  "image_url": string | null,
  "video_prompt": string | null,
  "video_url": string | null,
  "hashtags": string[],
  "platform_optimized": {
    "linkedin": {
      "content": string,
      "hashtags": string[]
    },
    "twitter": {
      "content": string,
      "hashtags": string[]
    },
    "instagram": {
      "content": string,
      "hashtags": string[]
    },
    "facebook": {
      "content": string,
      "hashtags": string[]
    }
  },
  "engagement_score": number,     // 0-10
  "selected": boolean,
  "call_to_action": string | null,
  "best_posting_time": string | null
}
```

### 4. Error Handling Strategy

**NO MORE MOCKS** - Replace with proper error handling:

```typescript
// Instead of mock data, return structured errors:
{
  "error": {
    "message": "Gemini API temporarily unavailable",
    "code": "GEMINI_API_ERROR",
    "details": {
      "fallback_available": false,
      "retry_after": 30,
      "support_contact": "Check API key configuration"
    }
  },
  "status": "error"
}
```

### 5. Business Context Flow

Ensure business context flows properly through the agent pipeline:

```typescript
BusinessAnalysis -> ContentGenerationAgent -> VisualContentAgent
```

Each agent must receive and use the business context:
- Company name, industry, description
- Target audience, campaign objectives
- Brand voice, competitive advantages
- Visual style preferences

### 6. Cost Control Structure

```typescript
"cost_control": {
  "text_url_limit": 10,
  "text_image_limit": 4,    // Imagen API costs
  "text_video_limit": 4,    // Veo API costs
  "requests_remaining": number,
  "daily_quota_used": number
}
```

## Implementation Requirements

### Phase 1: Remove All Mocks (IMMEDIATE)
- [ ] Replace mock content generation with proper Gemini integration
- [ ] Replace mock business analysis with real URL scraping + Gemini analysis
- [ ] Replace mock visual content with Imagen/Veo integration or proper error handling
- [ ] Add structured error responses for all failure scenarios
- [ ] Mocked Stubs should feature real-implemented functionality, or graceful exception handling advising of the functionality gap/placeholder, making it clear that functionality is omitted.

### Phase 2: Enforce Structure (IMMEDIATE)
- [ ] Update all API endpoints to match defined structure
- [ ] Fix all failing tests to match new structure
- [ ] Add API response validation middleware
- [ ] Update frontend to handle new error structure

### Phase 3: Business Context Flow (IMMEDIATE)
- [ ] Fix business context extraction from URLs
- [ ] Ensure context flows to visual content agent
- [ ] Add context validation and enrichment
- [ ] Test end-to-end context flow

## Testing Requirements

All tests must validate:
1. **Response Structure Compliance** - Exact field names and types
2. **Error Handling** - Proper error responses, no mock fallbacks
3. **Business Context Flow** - Context propagation through agent pipeline
4. **Cost Control** - Limits enforced correctly
5. **Performance** - Response times within acceptable ranges

## Success Criteria

- [ ] Zero mock responses in production code
- [ ] All API responses match defined structure
- [ ] Business context flows correctly to all agents
- [ ] Proper error handling for all failure scenarios
- [ ] All tests pass with real API structure validation
- [ ] Frontend handles all error cases gracefully

## Consequences

**Benefits:**
- Professional-grade API suitable for hackathon judging
- Consistent structure prevents regression
- Clear error handling improves user experience
- Real functionality demonstrates technical capability

**Risks:**
- More complex error handling implementation
- Potential for API failures without fallbacks
- Need for comprehensive testing of error scenarios

## Implementation Notes

This ADR must be implemented BEFORE v1.0.0 release to ensure:
- Professional presentation for hackathon judges
- Accurate representation of system capabilities
- Robust error handling for demo scenarios
- Consistent API structure for future development 