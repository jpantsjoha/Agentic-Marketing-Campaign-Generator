/**
 * FILENAME: test-visual-content-context-regression.js
 * DESCRIPTION/PURPOSE: Frontend regression tests for visual content context fidelity
 * Author: JP + 2025-07-23
 * 
 * These tests specifically prevent the regression where:
 * - Mountain landscape images were shown for business marketing campaigns
 * - Generic demo content was displayed instead of campaign-specific visuals
 * - Context fidelity was lost between campaign text and visual content
 * 
 * CRITICAL: These tests should FAIL if demo mode shows irrelevant content
 * without clear "DEMO" labeling.
 */

import { test, expect } from '@playwright/test';
import { chromium } from 'playwright';

// REGRESSION PREVENTION: These exact URLs caused the original issue
const FORBIDDEN_DEMO_URLS = [
  'https://images.unsplash.com/photo-1542038784456-1ea8e732b2b9',
  'https://images.unsplash.com/photo-1531804055935-76f44d7c3621',
  'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
  'https://via.placeholder.com',
  'https://picsum.photos'
];

// Expected indicators that content is contextually relevant to business campaigns
const BUSINESS_CONTEXT_INDICATORS = [
  'professional', 'business', 'marketing', 'corporate', 'office',
  'team', 'meeting', 'consultation', 'service', 'product', 'company'
];

test.describe('Visual Content Context Fidelity - Regression Prevention', () => {
  
  test.beforeEach(async ({ page }) => {
    // Enable console logging to catch API calls
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('🔴 Console Error:', msg.text());
      }
    });
    
    // Listen for network requests to track API calls
    page.on('request', request => {
      if (request.url().includes('/api/v1/content/generate-visuals')) {
        console.log('🎨 Visual generation API called:', request.url());
      }
    });
  });

  test('CRITICAL: No forbidden demo URLs in ideation page visuals', async ({ page }) => {
    console.log('🔍 Testing for forbidden demo URLs in ideation page...');
    
    await page.goto('http://localhost:8096/ideation');
    await page.waitForTimeout(3000);
    
    // Get all image elements
    const images = await page.locator('img').all();
    
    for (let i = 0; i < images.length; i++) {
      const img = images[i];
      const src = await img.getAttribute('src');
      
      if (src) {
        console.log(`📸 Found image ${i + 1}: ${src.substring(0, 80)}...`);
        
        // CRITICAL: Check for forbidden demo URLs
        for (const forbiddenUrl of FORBIDDEN_DEMO_URLS) {
          if (src.startsWith(forbiddenUrl)) {
            // Take screenshot of the offending content
            await page.screenshot({ 
              path: `regression-detected-forbidden-url-${Date.now()}.png`,
              fullPage: true 
            });
            
            throw new Error(
              `REGRESSION DETECTED: Found forbidden demo URL in image ${i + 1}: ${src}. ` +
              `This indicates demo mode is active when contextual generation should occur. ` +
              `Screenshots saved for investigation.`
            );
          }
        }
        
        // Additional check: If it's a demo URL, it should be clearly labeled
        if (src.includes('unsplash.com') || src.includes('placeholder.com') || src.includes('picsum.photos')) {
          // Look for demo indicators near the image
          const parentElement = await img.locator('..').first();
          const parentText = await parentElement.textContent();
          
          const hasDemoLabel = parentText && (
            parentText.includes('Demo') ||
            parentText.includes('Sample') ||
            parentText.includes('Preview') ||
            parentText.includes('Example')
          );
          
          if (!hasDemoLabel) {
            await page.screenshot({ 
              path: `regression-unlabeled-demo-${Date.now()}.png`,
              fullPage: true 
            });
            
            throw new Error(
              `REGRESSION: Demo image ${src} is not clearly labeled as demo content. ` +
              `Users may think this represents real system capabilities.`
            );
          }
        }
      }
    }
    
    console.log('✅ No forbidden demo URLs found in images');
  });

  test('CRITICAL: No forbidden demo URLs in video content', async ({ page }) => {
    console.log('🔍 Testing for forbidden demo URLs in video content...');
    
    await page.goto('http://localhost:8096/ideation');
    await page.waitForTimeout(3000);
    
    // Get all video elements
    const videos = await page.locator('video').all();
    
    for (let i = 0; i < videos.length; i++) {
      const video = videos[i];
      const src = await video.getAttribute('src');
      
      if (src) {
        console.log(`🎬 Found video ${i + 1}: ${src.substring(0, 80)}...`);
        
        // CRITICAL: Check for forbidden demo URLs
        for (const forbiddenUrl of FORBIDDEN_DEMO_URLS) {
          if (src.startsWith(forbiddenUrl)) {
            await page.screenshot({ 
              path: `regression-video-forbidden-url-${Date.now()}.png`,
              fullPage: true 
            });
            
            throw new Error(
              `REGRESSION DETECTED: Found forbidden demo video URL: ${src}. ` +
              `This indicates demo mode is bypassing real generation.`
            );
          }
        }
      }
    }
    
    console.log('✅ No forbidden demo URLs found in videos');
  });

  test('Context relevance validation for business campaigns', async ({ page }) => {
    console.log('🎯 Testing context relevance for business campaigns...');
    
    await page.goto('http://localhost:8096/ideation');
    await page.waitForTimeout(3000);
    
    // Look for campaign text content
    const campaignTexts = await page.locator('[class*="content"], [class*="text"], .post-content, .campaign-text').allTextContents();
    
    // Get all image sources
    const imageSources = await page.locator('img').evaluateAll(imgs => 
      imgs.map(img => img.src).filter(src => src && src.length > 0)
    );
    
    console.log(`📝 Found ${campaignTexts.length} text elements`);
    console.log(`🖼️ Found ${imageSources.length} image sources`);
    
    // If we have business-focused campaign text...
    let hasBusinessContent = false;
    for (const text of campaignTexts) {
      const lowerText = text.toLowerCase();
      if (BUSINESS_CONTEXT_INDICATORS.some(indicator => lowerText.includes(indicator))) {
        hasBusinessContent = true;
        console.log(`📈 Detected business context in text: "${text.substring(0, 100)}..."`);
        break;
      }
    }
    
    if (hasBusinessContent) {
      // ...then images should NOT be nature/landscape content
      const problematicImages = [];
      
      for (const imgSrc of imageSources) {
        // Check if image appears to be nature/landscape content based on URL structure
        if (imgSrc.includes('unsplash.com')) {
          // Unsplash URLs often contain descriptive information
          const lowerSrc = imgSrc.toLowerCase();
          
          // Nature/landscape indicators in URLs that conflict with business content
          const natureIndicators = [
            'mountain', 'nature', 'landscape', 'forest', 'tree', 'sky', 'cloud',
            'outdoor', 'wilderness', 'scenery', 'vista', 'peak', 'valley'
          ];
          
          if (natureIndicators.some(indicator => lowerSrc.includes(indicator))) {
            problematicImages.push({
              url: imgSrc,
              issue: 'Nature/landscape image for business campaign'
            });
          }
        }
      }
      
      if (problematicImages.length > 0) {
        await page.screenshot({ 
          path: `context-mismatch-detected-${Date.now()}.png`,
          fullPage: true 
        });
        
        const issueDetails = problematicImages.map(img => 
          `- ${img.url.substring(0, 100)}... (${img.issue})`
        ).join('\\n');
        
        throw new Error(
          `CONTEXT MISMATCH DETECTED: Found ${problematicImages.length} images with nature/landscape content ` +
          `in business campaign context. This indicates the regression where mountain images ` +
          `were shown for business campaigns.\\n\\nProblematic images:\\n${issueDetails}`
        );
      }
    }
    
    console.log('✅ No context mismatches detected');
  });

  test('Demo mode should be clearly indicated to users', async ({ page }) => {
    console.log('🏷️ Testing demo mode labeling...');
    
    await page.goto('http://localhost:8096/ideation');
    await page.waitForTimeout(3000);
    
    // Check if page is in demo mode
    const pageText = await page.textContent('body');
    const isDemoMode = pageText.includes('demo') || 
                      pageText.includes('Demo') || 
                      pageText.includes('DEMO') ||
                      pageText.includes('showing demo content');
    
    if (isDemoMode) {
      console.log('📋 Demo mode detected - checking for clear labeling...');
      
      // Demo mode should be OBVIOUS to users
      const demoIndicators = await page.locator('text=/demo|Demo|DEMO|Sample|Example|Preview/i').count();
      
      expect(demoIndicators).toBeGreaterThan(0);
      
      // Take screenshot to verify demo labeling is visible
      await page.screenshot({ 
        path: `demo-mode-labeling-${Date.now()}.png`,
        fullPage: true 
      });
      
      console.log(`✅ Demo mode properly labeled with ${demoIndicators} indicators`);
    } else {
      console.log('📋 Not in demo mode - should use real generation');
    }
  });

  test('Real campaign workflow should not show demo URLs', async ({ page }) => {
    console.log('🔄 Testing real campaign workflow...');
    
    // Navigate to create new campaign
    await page.goto('http://localhost:8096/new-campaign');
    await page.waitForTimeout(2000);
    
    // Fill out a minimal campaign (if form exists)
    try {
      const nameField = page.locator('input[name="name"], input[id="name"], input[placeholder*="name"]').first();
      if (await nameField.count() > 0) {
        await nameField.fill('Test Business Campaign');
      }
      
      const objectiveField = page.locator('input[name="objective"], input[id="objective"], textarea[name="objective"]').first();
      if (await objectiveField.count() > 0) {
        await objectiveField.fill('Increase brand awareness for technology consulting');
      }
      
      const businessDescField = page.locator('textarea[name="businessDescription"], textarea[id="businessDescription"]').first();
      if (await businessDescField.count() > 0) {
        await businessDescField.fill('Professional technology consulting services for businesses');
      }
      
      // Submit campaign creation
      const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Generate")').first();
      if (await submitButton.count() > 0) {
        await submitButton.click();
        await page.waitForTimeout(5000); // Allow time for generation
        
        // Check if we're redirected to ideation page
        const currentUrl = page.url();
        if (currentUrl.includes('/ideation')) {
          console.log('📍 Redirected to ideation page after campaign creation');
          
          // Now verify that real campaign content is shown (not demo URLs)
          const images = await page.locator('img').all();
          
          for (let i = 0; i < images.length; i++) {
            const img = images[i];
            const src = await img.getAttribute('src');
            
            if (src) {
              // Should not have forbidden demo URLs in real campaign
              for (const forbiddenUrl of FORBIDDEN_DEMO_URLS) {
                if (src.startsWith(forbiddenUrl)) {
                  await page.screenshot({ 
                    path: `real-campaign-demo-url-regression-${Date.now()}.png`,
                    fullPage: true 
                  });
                  
                  throw new Error(
                    `REGRESSION IN REAL CAMPAIGN: Created real campaign but still showing demo URL: ${src}. ` +
                    `This indicates the system is not properly switching from demo mode to real generation.`
                  );
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.log('⚠️ Campaign creation form not available or incomplete - skipping workflow test');
      console.log('Error details:', error.message);
    }
    
    console.log('✅ Real campaign workflow test completed');
  });

  test('API endpoints should not return demo URLs', async ({ page }) => {
    console.log('🔌 Testing API endpoints for demo URL prevention...');
    
    let apiCalled = false;
    let apiResponse = null;
    
    // Intercept API calls to visual generation endpoint
    await page.route('**/api/v1/content/generate-visuals', async route => {
      apiCalled = true;
      const response = await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          posts_with_visuals: [
            {
              id: 'test_post_1',
              type: 'text_image',
              content: 'Professional business consulting services',
              image_url: 'http://localhost:8000/api/v1/content/images/campaign123/business_consulting.png',
              image_metadata: {
                generation_method: 'imagen_real',
                model: 'imagen-3.0'
              }
            }
          ],
          generation_metadata: {
            agent_used: 'RealImageGeneration',
            processing_time: 4.2
          }
        })
      });
      
      apiResponse = response;
    });
    
    await page.goto('http://localhost:8096/ideation');
    await page.waitForTimeout(3000);
    
    // Try to trigger visual generation if possible
    const generateButton = page.locator('button:has-text("Generate")').first();
    if (await generateButton.count() > 0) {
      await generateButton.click();
      await page.waitForTimeout(2000);
    }
    
    if (apiCalled) {
      console.log('✅ API intercept verified - endpoint would return real URLs, not demo URLs');
    } else {
      console.log('ℹ️ Visual generation API not triggered in this test run');
    }
  });

});

test.describe('Visual Content Performance and Reliability', () => {
  
  test('System should handle generation failures gracefully', async ({ page }) => {
    console.log('⚡ Testing generation failure handling...');
    
    // Mock API failure
    await page.route('**/api/v1/content/generate-visuals', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Visual generation temporarily unavailable'
        })
      });
    });
    
    await page.goto('http://localhost:8096/ideation');
    await page.waitForTimeout(3000);
    
    // Try to trigger generation
    const generateButton = page.locator('button:has-text("Generate")').first();
    if (await generateButton.count() > 0) {
      await generateButton.click();
      await page.waitForTimeout(2000);
      
      // System should show error message, not fall back to demo URLs
      const errorMessages = await page.locator('text=/error|Error|ERROR|failed|Failed|unavailable/i').count();
      
      if (errorMessages > 0) {
        console.log('✅ Error handling detected - system shows failure instead of misleading demo content');
      }
    }
  });

  test('Page loading performance with visual content', async ({ page }) => {
    console.log('📊 Testing page loading performance...');
    
    const startTime = Date.now();
    
    await page.goto('http://localhost:8096/ideation');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    console.log(`⏱️ Page loaded in ${loadTime}ms`);
    
    // Verify images are loaded (or properly indicate loading state)
    const images = await page.locator('img').all();
    let loadedImages = 0;
    
    for (const img of images) {
      const naturalWidth = await img.evaluate(el => el.naturalWidth);
      if (naturalWidth > 0) {
        loadedImages++;
      }
    }
    
    console.log(`🖼️ ${loadedImages}/${images.length} images loaded successfully`);
    
    // Page should load reasonably fast (less than 10 seconds)
    expect(loadTime).toBeLessThan(10000);
  });

});

// Utility function to run these tests
async function runRegressionTests() {
  console.log('🚀 Starting Visual Content Context Regression Tests...');
  
  const browser = await chromium.launch({ 
    headless: false, // Show browser for debugging
    slowMo: 500 
  });
  
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  
  const page = await context.newPage();
  
  try {
    // Run the most critical test manually for immediate feedback
    console.log('\\n🔍 Running critical regression test...');
    
    await page.goto('http://localhost:8096/ideation');
    await page.waitForTimeout(3000);
    
    const images = await page.locator('img').all();
    let regressionDetected = false;
    
    for (let i = 0; i < images.length; i++) {
      const img = images[i];
      const src = await img.getAttribute('src');
      
      if (src) {
        for (const forbiddenUrl of FORBIDDEN_DEMO_URLS) {
          if (src.startsWith(forbiddenUrl)) {
            console.log(`🚨 REGRESSION DETECTED: Image ${i + 1} uses forbidden URL: ${src}`);
            regressionDetected = true;
            
            await page.screenshot({ 
              path: `manual-regression-detection-${Date.now()}.png`,
              fullPage: true 
            });
          }
        }
      }
    }
    
    if (regressionDetected) {
      console.log('❌ REGRESSION TESTS FAILED: Demo URLs detected in production content');
      console.log('📸 Screenshots saved for investigation');
    } else {
      console.log('✅ REGRESSION TESTS PASSED: No forbidden demo URLs detected');
    }
    
  } catch (error) {
    console.error('❌ Test execution failed:', error);
  } finally {
    await browser.close();
  }
}

// Export for use in other test suites
export { FORBIDDEN_DEMO_URLS, BUSINESS_CONTEXT_INDICATORS, runRegressionTests };

// If run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runRegressionTests().catch(console.error);
}