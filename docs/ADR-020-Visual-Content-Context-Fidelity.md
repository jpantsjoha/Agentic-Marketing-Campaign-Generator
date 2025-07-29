# ADR-020: Visual Content Context Fidelity Requirements

**Status**: Accepted  
**Date**: 2025-07-23  
**Authors**: JP  
**Reviewers**: Development Team  
**Related**: ADR-016 (Visual Content Generation), ADR-019 (Agentic Visual Content)

## Problem Statement

A critical regression occurred where the ideation page displayed generic mountain landscape images and nature photography for business marketing campaigns, completely breaking the context fidelity between campaign content and visual assets. This happened because:

1. **Demo Mode Misuse**: The frontend showed hardcoded Unsplash stock photos as placeholders
2. **Context Disconnect**: No validation ensured visual content matched campaign context
3. **Developer Confusion**: Lack of clear architectural guidance led to assumptions that placeholder content was acceptable
4. **Test Coverage Gap**: Existing tests didn't catch context mismatches

**Business Impact**: This regression would have resulted in:
- Poor campaign performance due to irrelevant visuals
- User confusion about system capabilities
- Brand misrepresentation for clients
- Loss of competitive advantage

## Decision

We establish **Visual Content Context Fidelity** as a core architectural requirement with the following binding decisions:

### Core Principle
**All visual content MUST be contextually relevant to the specific business, campaign, and post content being generated.**

### Architectural Requirements

#### 1. Mandatory Context Validation
- **REQUIRED**: All visual generation MUST validate context relevance before delivery
- **REQUIRED**: Visual generation prompts MUST include comprehensive business context
- **REQUIRED**: Generated content MUST align with campaign objectives and business type

#### 2. Forbidden Content Policy
The following content is **STRICTLY PROHIBITED** in production campaigns:

```javascript
// FORBIDDEN: These exact URLs caused the regression
const FORBIDDEN_DEMO_URLS = [
  'https://images.unsplash.com/photo-1542038784456-1ea8e732b2b9',
  'https://images.unsplash.com/photo-1531804055935-76f44d7c3621', 
  'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
  'https://via.placeholder.com/*',
  'https://picsum.photos/*'
];

// FORBIDDEN: Content types that violate context fidelity
const FORBIDDEN_CONTENT_TYPES = [
  'generic_mountain_landscapes_for_business_campaigns',
  'nature_photography_for_corporate_content',
  'random_stock_photos_without_business_context',
  'placeholder_content_in_production_mode'
];
```

#### 3. Context Enhancement Pipeline
Visual generation MUST follow this enhancement pipeline:

```python
def enhance_visual_prompt(base_prompt: str, business_context: Dict) -> str:
    """
    REQUIRED: All visual prompts must be enhanced with business context
    """
    enhanced_prompt = base_prompt
    
    # REQUIRED: Company and industry context
    enhanced_prompt += f", {business_context['company_name']} {business_context['industry']}"
    
    # REQUIRED: Product-specific context (if available)
    if business_context.get('product_context', {}).get('has_specific_product'):
        product_name = business_context['product_context']['product_name']
        enhanced_prompt += f", featuring {product_name}"
    
    # REQUIRED: Professional context matching business type
    if 'restaurant' in business_context['industry'].lower():
        enhanced_prompt += ", restaurant setting, food service context"
    elif 'technology' in business_context['industry'].lower():
        enhanced_prompt += ", professional office, technology context"
    # ... additional industry mappings
    
    # PROHIBITED: Generic contexts that could mislead generation
    prohibited_contexts = ['mountain', 'landscape', 'nature', 'generic']
    for prohibited in prohibited_contexts:
        assert prohibited not in enhanced_prompt.lower(), f"Prohibited context '{prohibited}' in prompt"
    
    return enhanced_prompt
```

#### 4. Validation Requirements
All implementations MUST include:

1. **Pre-Generation Validation**:
   ```python
   def validate_generation_context(business_context: Dict, post_content: str) -> bool:
       """Validate context before generation"""
       assert business_context.get('company_name'), "Company name required"
       assert business_context.get('industry'), "Industry context required"  
       assert len(post_content) > 0, "Post content required for context"
       return True
   ```

2. **Post-Generation Validation**:
   ```python
   def validate_generated_content(image_url: str, business_context: Dict) -> bool:
       """Validate generated content matches business context"""
       # Must not be forbidden demo URLs
       for forbidden_url in FORBIDDEN_DEMO_URLS:
           assert not image_url.startswith(forbidden_url), f"Forbidden demo URL: {image_url}"
       
       # Must be contextually appropriate (implementation-specific)
       return True
   ```

3. **Test Coverage Requirements**:
   - **REQUIRED**: Tests must verify no forbidden URLs in responses
   - **REQUIRED**: Tests must validate context relevance
   - **REQUIRED**: Tests must catch regressions when demo content appears in production

#### 5. Error Handling Standards
When visual generation fails, implementations MUST:

1. **Return Explicit Error States**:
   ```json
   {
     "image_url": null,
     "status": "error",
     "error": "Generation failed - check API configuration",
     "metadata": {
       "generation_method": "failed",
       "note": "No placeholder content provided to avoid misleading users"
     }
   }
   ```

2. **Never Fall Back to Irrelevant Placeholders**:
   ```python
   # PROHIBITED: Fallback to irrelevant content
   def bad_fallback(prompt: str) -> str:
       return "https://via.placeholder.com/400x300"  # NEVER DO THIS
   
   # REQUIRED: Explicit error handling
   def good_error_handling(prompt: str) -> Dict:
       return {
           "image_url": None,
           "status": "error", 
           "error": "Visual generation unavailable"
       }
   ```

#### 6. Demo Mode Requirements
When operating in demo mode, implementations MUST:

1. **Clear Demo Labeling**:
   ```html
   <!-- REQUIRED: Obvious demo indicators -->
   <div class="demo-content-warning">
     <strong>DEMO CONTENT</strong> - Not representative of your actual campaign
   </div>
   ```

2. **Contextual Demo Content** (when possible):
   - Use business-specific demo content when available
   - Generate demo content using real APIs with demo data
   - Avoid generic stock photos that don't represent system capabilities

## Implementation Guidelines

### Backend Implementation
```python
# agents/visual_content_agent.py
async def generate_visual_content_for_posts(
    social_posts: List[Dict], 
    business_context: Dict,
    campaign_objective: str
) -> Dict:
    """
    Generate contextually relevant visual content
    
    ARCHITECTURAL REQUIREMENT: This function MUST ensure context fidelity
    """
    # 1. REQUIRED: Validate input context
    validate_generation_context(business_context, social_posts)
    
    # 2. REQUIRED: Enhance prompts with business context  
    enhanced_prompts = []
    for post in social_posts:
        base_prompt = post.get('content', '')
        enhanced_prompt = enhance_visual_prompt(base_prompt, business_context)
        enhanced_prompts.append(enhanced_prompt)
    
    # 3. REQUIRED: Generate with real APIs (not placeholders)
    try:
        generated_content = await real_ai_generation(enhanced_prompts)
        
        # 4. REQUIRED: Validate generated content
        for content in generated_content:
            validate_generated_content(content['image_url'], business_context)
            
        return {
            "posts_with_visuals": generated_content,
            "generation_metadata": {
                "context_fidelity": "validated",
                "generation_method": "real_ai"
            }
        }
        
    except Exception as e:
        # 5. REQUIRED: Proper error handling
        return {
            "posts_with_visuals": [
                {"image_url": None, "status": "error", "error": str(e)}
                for _ in social_posts
            ],
            "generation_metadata": {
                "context_fidelity": "error",
                "error": str(e)
            }
        }
```

### Frontend Implementation
```typescript
// src/pages/IdeationPage.tsx
const IdeationPage = () => {
  const [visualContent, setVisualContent] = useState([]);
  const [isDemo, setIsDemo] = useState(false);
  
  useEffect(() => {
    if (currentCampaign) {
      // REQUIRED: Call real generation for active campaigns
      generateRealVisualContent(currentCampaign);
      setIsDemo(false);
    } else {
      // REQUIRED: Clear demo labeling when no campaign
      setIsDemo(true);
    }
  }, [currentCampaign]);
  
  const generateRealVisualContent = async (campaign) => {
    try {
      const response = await fetch('/api/v1/content/generate-visuals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          social_posts: campaign.posts,
          business_context: campaign.business_context,
          campaign_objective: campaign.objective
        })
      });
      
      const result = await response.json();
      
      // REQUIRED: Validate no forbidden URLs in response
      validateNoDemoUrls(result.posts_with_visuals);
      
      setVisualContent(result.posts_with_visuals);
      
    } catch (error) {
      // REQUIRED: Handle errors without misleading content
      setVisualContent([]);
      showError('Visual generation failed. Please try again.');
    }
  };
  
  const validateNoDemoUrls = (posts) => {
    const forbiddenUrls = [
      'https://images.unsplash.com/photo-1542038784456-1ea8e732b2b9',
      'https://images.unsplash.com/photo-1531804055935-76f44d7c3621',
      // ... other forbidden URLs
    ];
    
    for (const post of posts) {
      const imageUrl = post.image_url;
      if (imageUrl) {
        for (const forbidden of forbiddenUrls) {
          if (imageUrl.startsWith(forbidden)) {
            throw new Error(`Forbidden demo URL detected: ${imageUrl}`);
          }
        }
      }
    }
  };
  
  return (
    <div>
      {isDemo && (
        <div className="demo-warning">
          <strong>DEMO MODE</strong> - Create a campaign to see real visual generation
        </div>
      )}
      
      {/* Render visual content with context validation */}
      {visualContent.map(post => (
        <VisualPost 
          key={post.id} 
          post={post} 
          isDemoMode={isDemo}
        />
      ))}
    </div>
  );
};
```

### Test Implementation
```python
# tests/test_visual_content_context_fidelity.py
class TestContextFidelityRequirements:
    
    @pytest.mark.asyncio
    async def test_no_forbidden_demo_urls_in_production(self):
        """ARCHITECTURAL REQUIREMENT: No demo URLs in production responses"""
        
        business_posts = [
            {
                "id": "business_post", 
                "type": "text_image",
                "content": "Transform your business with our solutions"
            }
        ]
        
        business_context = {
            "company_name": "TechCorp",
            "industry": "Technology Consulting"
        }
        
        result = await generate_visual_content_for_posts(
            social_posts=business_posts,
            business_context=business_context,
            campaign_objective="generate leads"
        )
        
        # ARCHITECTURAL REQUIREMENT: Validate no forbidden URLs
        FORBIDDEN_URLS = [
            'https://images.unsplash.com/photo-1542038784456-1ea8e732b2b9',
            'https://images.unsplash.com/photo-1531804055935-76f44d7c3621',
            'https://via.placeholder.com',
            'https://picsum.photos'
        ]
        
        for post in result['posts_with_visuals']:
            image_url = post.get('image_url', '')
            if image_url:
                for forbidden_url in FORBIDDEN_URLS:
                    assert not image_url.startswith(forbidden_url), (
                        f"ARCHITECTURAL VIOLATION: Forbidden demo URL found: {image_url}"
                    )
    
    def test_context_enhancement_pipeline(self):
        """ARCHITECTURAL REQUIREMENT: Context must enhance all prompts"""
        
        base_prompt = "Professional business image"
        business_context = {
            "company_name": "RestaurantCorp",
            "industry": "Food & Beverage",
            "product_context": {
                "has_specific_product": True,
                "product_name": "Italian Cuisine"
            }
        }
        
        enhanced_prompt = enhance_visual_prompt(base_prompt, business_context)
        
        # ARCHITECTURAL REQUIREMENT: Must contain business context
        assert "RestaurantCorp" in enhanced_prompt
        assert "Food & Beverage" in enhanced_prompt or "restaurant" in enhanced_prompt.lower()
        assert "Italian Cuisine" in enhanced_prompt
        
        # ARCHITECTURAL REQUIREMENT: Must not contain prohibited contexts
        prohibited_contexts = ['mountain', 'landscape', 'nature']
        for prohibited in prohibited_contexts:
            assert prohibited not in enhanced_prompt.lower(), (
                f"Prohibited context '{prohibited}' found in enhanced prompt"
            )
```

## Consequences

### Positive Consequences
1. **Context Fidelity Guarantee**: All visual content will be relevant to campaigns
2. **Regression Prevention**: Clear architectural boundaries prevent similar issues
3. **Developer Clarity**: Explicit requirements eliminate ambiguity
4. **Quality Assurance**: Automated validation ensures compliance
5. **User Trust**: Consistent, relevant visuals build user confidence

### Negative Consequences
1. **Implementation Complexity**: Additional validation logic required
2. **Development Overhead**: More comprehensive testing needed
3. **Performance Impact**: Context validation adds processing time
4. **Error Handling Complexity**: More sophisticated error states required

### Risk Mitigation
1. **Performance**: Context validation optimized with caching and async processing
2. **Complexity**: Standardized validation utilities reduce implementation burden
3. **Testing**: Automated test suites catch violations early in development

## Compliance and Enforcement

### Mandatory Compliance Points
1. **Code Review**: All visual generation code must pass context fidelity review
2. **Automated Tests**: CI/CD must run context fidelity tests on every commit
3. **Production Monitoring**: Runtime validation must alert on context violations
4. **Documentation**: All visual generation features must document context requirements

### Enforcement Mechanisms
1. **Git Hooks**: Pre-commit hooks validate test coverage for context fidelity
2. **CI/CD Gates**: Builds fail if context fidelity tests don't pass
3. **Code Analysis**: Static analysis tools flag violations of forbidden patterns
4. **Monitoring Alerts**: Production systems alert on demo URL appearances

## Future Considerations

### Planned Enhancements
1. **AI-Powered Context Validation**: Use vision models to validate generated content relevance
2. **Dynamic Context Enhancement**: Machine learning to improve prompt enhancement
3. **User Feedback Integration**: Allow users to rate visual relevance for continuous improvement
4. **Advanced Error Recovery**: Intelligent retry with alternative generation strategies

### Deprecation Path
- **Legacy Demo Content**: All existing hardcoded demo URLs must be removed by 2025-08-15
- **Fallback Mechanisms**: Irrelevant placeholder fallbacks deprecated in favor of explicit error states

## Related Decisions
- **ADR-016**: Visual Content Generation - Established basic generation requirements
- **ADR-019**: Agentic Visual Content Generation - Defined autonomous validation patterns
- **ADR-021**: Campaign Context Management - Defines business context structure (planned)

## Decision Rationale

This architectural decision directly addresses the critical regression where mountain landscape images appeared in business marketing campaigns. By establishing Context Fidelity as a core architectural requirement, we:

1. **Prevent Similar Regressions**: Clear architectural boundaries make violations obvious
2. **Ensure Business Value**: Visual content will always support campaign objectives  
3. **Maintain Competitive Advantage**: Contextually relevant visuals differentiate our platform
4. **Build User Trust**: Consistent, relevant content builds confidence in the system

**This decision is BINDING and must be followed by all developers working on visual content generation features.**

---

**Approved By**: Development Team  
**Implementation Deadline**: 2025-08-01  
**Review Date**: 2025-10-01  
**Status**: ACTIVE - Must be implemented immediately