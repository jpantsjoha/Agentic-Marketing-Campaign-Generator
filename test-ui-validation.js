import { chromium } from 'playwright';
import fs from 'fs';

async function validateUI() {
  console.log('🚀 Starting Video Venture Launch UI Validation');
  
  const browser = await chromium.launch({ headless: false, slowMo: 1000 });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  try {
    // Test 1: Load homepage
    console.log('\n📋 Test 1: Loading homepage...');
    await page.goto('http://localhost:8080');
    await page.waitForTimeout(2000);
    
    const title = await page.title();
    console.log(`✅ Page title: ${title}`);
    
    // Take screenshot of homepage
    await page.screenshot({ path: 'screenshots/homepage.png', fullPage: true });
    console.log('📸 Homepage screenshot saved');

    // Test 2: Navigate to campaign creation
    console.log('\n📋 Test 2: Testing campaign creation page...');
    try {
      // Look for navigation elements
      const newCampaignButton = page.locator('text=New Campaign').or(page.locator('[href*="campaign"]')).or(page.locator('text=Create')).first();
      
      if (await newCampaignButton.count() > 0) {
        await newCampaignButton.click();
        await page.waitForTimeout(2000);
        console.log('✅ Navigated to campaign creation');
      } else {
        // Try direct navigation
        await page.goto('http://localhost:8080/new-campaign');
        await page.waitForTimeout(2000);
        console.log('✅ Direct navigation to campaign creation');
      }
      
      await page.screenshot({ path: 'screenshots/campaign-creation.png', fullPage: true });
      console.log('📸 Campaign creation screenshot saved');
      
      // Test URL analysis functionality
      console.log('\n📋 Test 3: Testing URL analysis...');
      const urlInput = page.locator('input[type="url"]').or(page.locator('input[placeholder*="URL"]')).or(page.locator('input[placeholder*="website"]')).first();
      
      if (await urlInput.count() > 0) {
        await urlInput.fill('https://www.redbubble.com/people/illustraman/shop');
        
        const analyzeButton = page.locator('text=Analyze').or(page.locator('button:has-text("AI")')).first();
        if (await analyzeButton.count() > 0) {
          console.log('🔍 Clicking URL analysis button...');
          await analyzeButton.click();
          await page.waitForTimeout(5000); // Wait for analysis
          
          await page.screenshot({ path: 'screenshots/url-analysis-result.png', fullPage: true });
          console.log('📸 URL analysis result screenshot saved');
        } else {
          console.log('⚠️ Analyze button not found');
        }
      } else {
        console.log('⚠️ URL input field not found');
      }
      
    } catch (e) {
      console.log('⚠️ Campaign creation navigation failed:', e.message);
    }

    // Test 3: Navigate to ideation page
    console.log('\n📋 Test 4: Testing ideation page for visual content...');
    try {
      await page.goto('http://localhost:8080/ideation');
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: 'screenshots/ideation-page.png', fullPage: true });
      console.log('📸 Ideation page screenshot saved');
      
      // Look for image/video content
      const images = await page.locator('img').count();
      const videos = await page.locator('video').count();
      const imageReady = await page.locator('text=Image Ready').count();
      const videoComplete = await page.locator('text=Video generation complete').count();
      
      console.log(`📊 Visual content found: ${images} images, ${videos} videos`);
      console.log(`📊 Content status: ${imageReady} image ready, ${videoComplete} video complete`);
      
      // Check for broken images or missing content
      const brokenImages = await page.locator('img[src=""], img[src*="placeholder"]').count();
      console.log(`🔍 Potential broken images: ${brokenImages}`);
      
    } catch (e) {
      console.log('⚠️ Ideation page test failed:', e.message);
    }

    // Test 4: Navigate to scheduling page
    console.log('\n📋 Test 5: Testing scheduling page content preview...');
    try {
      await page.goto('http://localhost:8080/scheduling');
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: 'screenshots/scheduling-page.png', fullPage: true });
      console.log('📸 Scheduling page screenshot saved');
      
      // Look for posts in the scheduling section
      const schedulingPosts = await page.locator('[class*="post"], [class*="card"]').count();
      const schedulingImages = await page.locator('img').count();
      
      console.log(`📊 Scheduling content: ${schedulingPosts} posts, ${schedulingImages} images`);
      
      // Check for missing previews
      const missingPreviews = await page.locator('text=Image Ready, text=Video generation complete').count();
      console.log(`📊 Content status indicators: ${missingPreviews}`);
      
    } catch (e) {
      console.log('⚠️ Scheduling page test failed:', e.message);
    }

    // Test 5: Check browser console for errors
    console.log('\n📋 Test 6: Checking browser console...');
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('🔴 Console Error:', msg.text());
      } else if (msg.type() === 'warning') {
        console.log('🟡 Console Warning:', msg.text());
      }
    });

    // Test 6: Check network requests
    console.log('\n📋 Test 7: Monitoring network requests...');
    page.on('response', response => {
      if (response.status() >= 400) {
        console.log(`🔴 Failed Request: ${response.status()} ${response.url()}`);
      } else if (response.url().includes('/api/')) {
        console.log(`✅ API Request: ${response.status()} ${response.url()}`);
      }
    });

    // Give some time to capture network activity
    await page.waitForTimeout(3000);
    
    console.log('\n🎉 UI Validation Complete! Check screenshots/ directory for visual evidence.');
    console.log('\n📁 Screenshots generated:');
    console.log('  - homepage.png');
    console.log('  - campaign-creation.png');
    console.log('  - url-analysis-result.png');
    console.log('  - ideation-page.png');
    console.log('  - scheduling-page.png');

  } catch (error) {
    console.error('❌ Validation failed:', error);
  } finally {
    await browser.close();
  }
}

// Create screenshots directory
if (!fs.existsSync('screenshots')) {
  fs.mkdirSync('screenshots');
}

validateUI().catch(console.error);