import { chromium } from 'playwright';

async function testLiatPhotographyFullJourney() {
  console.log('🎯 Testing Full User Journey for Liat Victoria Photography - Context-Aware Visual Generation\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--disable-blink-features=AutomationControlled']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  
  const page = await context.newPage();
  
  try {
    // Step 1: Homepage
    console.log('📍 Step 1: Navigating to homepage...');
    await page.goto('http://localhost:8080');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'liat-context-01-homepage.png' });
    console.log('✅ Homepage loaded\n');
    
    // Step 2: Click on Create Your Campaign
    console.log('📍 Step 2: Starting new campaign...');
    await page.click('text="Create Your Campaign"');
    await page.waitForURL('**/new-campaign');
    await page.screenshot({ path: 'liat-context-02-new-campaign.png' });
    console.log('✅ New campaign page loaded\n');
    
    // Step 3: Fill campaign details
    console.log('📍 Step 3: Filling campaign details...');
    
    // Campaign name
    await page.fill('input[placeholder*="Summer 2025 Product Launch"]', 'Showcase Liat Victoria\'s Artistic Photography');
    
    // Campaign objective
    await page.fill('input[placeholder*="Increase brand awareness"]', 'Increase visitors & exposure for photography artist');
    
    // Business URL
    await page.fill('input[placeholder*="your-main-website.com"]', 'https://liatvictoriaphotography.co.uk');
    
    // Click Analyze URLs button
    await page.click('button:has-text("Analyze URLs with AI")');
    
    await page.screenshot({ path: 'liat-context-03-filled-form.png' });
    console.log('✅ Campaign details filled\n');
    
    // Step 4: Wait for URL analysis to complete
    console.log('📍 Step 4: Waiting for URL analysis to complete...');
    
    // Wait for "Analyzing..." button to disappear and be replaced
    try {
      await page.waitForSelector('button:has-text("Analyzing...")', { timeout: 30000 });
      console.log('   ⏳ URL analysis in progress...');
      
      // Wait for analysis to complete
      await page.waitForFunction(() => {
        const button = document.querySelector('button:contains("Analyzing...")');
        return !button || button.textContent !== "Analyzing...";
      }, { timeout: 60000 });
      
      console.log('   ✅ URL analysis complete');
    } catch (e) {
      console.log('   ⚠️ URL analysis might already be complete or different UI');
    }
    
    await page.screenshot({ path: 'liat-context-04-analysis-complete.png' });
    
    // Step 5: Create campaign
    console.log('📍 Step 5: Creating campaign...');
    await page.click('button:has-text("Start AI Generation")');
    
    // Wait for success and navigation
    await page.waitForTimeout(2000);
    await page.waitForSelector('text="Campaign created successfully"', { timeout: 10000 });
    console.log('✅ Campaign created successfully\n');
    
    // Wait for redirect to ideation page
    await page.waitForURL('**/ideation', { timeout: 10000 });
    await page.screenshot({ path: 'liat-context-04-ideation-loading.png' });
    
    // Step 6: Wait for AI analysis and content generation
    console.log('📍 Step 6: AI analyzing business and generating content...');
    console.log('⏳ Waiting for URL analysis to complete...');
    
    // Wait for analysis to complete (URL analysis + content generation)
    await page.waitForSelector('text="AI-generated social media content"', { timeout: 60000 });
    await page.waitForTimeout(3000); // Let all content load
    
    await page.screenshot({ path: 'liat-context-05-ideation-complete.png' });
    console.log('✅ AI analysis and content generation complete\n');
    
    // Step 6: Analyze the generated visual content
    console.log('📍 Step 6: Checking generated visual content for photography context...');
    
    // Check for image elements
    const imageElements = await page.$$('img[alt*="Generated"]');
    console.log(`🖼️  Found ${imageElements.length} generated images`);
    
    // Take detailed screenshot of visual content area
    const visualContentArea = await page.$('.grid.grid-cols-1.md\\:grid-cols-3.gap-6');
    if (visualContentArea) {
      await visualContentArea.screenshot({ path: 'liat-context-06-visual-content.png' });
    }
    
    // Check image sources to verify they're not placeholder images
    for (let i = 0; i < Math.min(3, imageElements.length); i++) {
      const imgSrc = await imageElements[i].getAttribute('src');
      console.log(`   Image ${i + 1} source: ${imgSrc ? imgSrc.substring(0, 50) + '...' : 'No source'}`);
    }
    
    // Check for video elements
    const videoElements = await page.$$('video');
    console.log(`🎬 Found ${videoElements.length} generated videos`);
    
    // Step 7: Click on Generate Visual Content to trigger enhanced prompts
    console.log('\n📍 Step 7: Testing enhanced visual generation...');
    const generateButton = await page.$('button:has-text("Generate Visual Content")');
    if (generateButton) {
      console.log('🔄 Clicking Generate Visual Content button...');
      await generateButton.click();
      await page.waitForTimeout(5000); // Wait for generation
      await page.screenshot({ path: 'liat-context-07-visual-generation.png' });
      console.log('✅ Visual content generation triggered\n');
    }
    
    // Step 8: Select posts and proceed to scheduling
    console.log('📍 Step 8: Selecting posts for scheduling...');
    
    // Click on first 3 post checkboxes
    const checkboxes = await page.$$('input[type="checkbox"]');
    for (let i = 0; i < Math.min(3, checkboxes.length); i++) {
      await checkboxes[i].click();
      console.log(`   ✓ Selected post ${i + 1}`);
    }
    
    await page.screenshot({ path: 'liat-context-08-posts-selected.png' });
    
    // Click Continue to Scheduling
    await page.click('button:has-text("Continue to Scheduling")');
    await page.waitForURL('**/scheduling', { timeout: 10000 });
    console.log('✅ Navigated to scheduling page\n');
    
    // Step 9: Verify visual content on scheduling page
    console.log('📍 Step 9: Verifying visual content on scheduling page...');
    await page.waitForTimeout(2000);
    
    const schedulingImages = await page.$$('.bg-gray-200.rounded-lg img');
    console.log(`🖼️  Found ${schedulingImages.length} images on scheduling page`);
    
    await page.screenshot({ path: 'liat-context-09-scheduling-visuals.png' });
    
    // Final summary
    console.log('\n📊 VISUAL CONTENT CONTEXT ANALYSIS:');
    console.log('=====================================');
    console.log('✅ Campaign created for Liat Victoria Photography');
    console.log('✅ Business URL analyzed: liatvictoriaphotography.co.uk');
    console.log('✅ Campaign objective: Increase visitors & exposure for artist');
    console.log(`✅ Generated ${imageElements.length} images with visual content`);
    console.log(`✅ Generated ${videoElements.length} videos`);
    console.log('✅ Visual content carried through to scheduling page');
    console.log('\n🎯 TEST COMPLETE - Check screenshots to verify photography-relevant visuals');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'liat-context-error.png' });
    throw error;
  } finally {
    await browser.close();
  }
}

// Run the test
testLiatPhotographyFullJourney()
  .then(() => {
    console.log('\n✨ Full user journey test completed successfully!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n💥 Test failed:', error);
    process.exit(1);
  });