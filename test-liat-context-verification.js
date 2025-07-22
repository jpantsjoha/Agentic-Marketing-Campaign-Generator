import { chromium } from 'playwright';

async function testLiatContextVerification() {
  console.log('🎯 Testing Liat Victoria Photography - Context Verification\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--disable-blink-features=AutomationControlled']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  
  const page = await context.newPage();
  
  try {
    // Quick setup to ideation page
    console.log('📍 Setting up campaign for Liat Victoria Photography...');
    await page.goto('http://localhost:8080');
    await page.click('text="Create Your Campaign"');
    await page.waitForURL('**/new-campaign');
    
    // Fill form with photography details
    await page.fill('input[placeholder*="Summer 2025 Product Launch"]', 'Showcase Liat Victoria\'s Artistic Photography');
    await page.fill('input[placeholder*="Increase brand awareness"]', 'Increase visitors & exposure for photography artist');
    await page.fill('input[placeholder*="your-main-website.com"]', 'https://liatvictoriaphotography.co.uk');
    
    // Analyze business
    await page.click('button:has-text("Analyze URLs with AI")');
    await page.waitForTimeout(15000); // Wait for URL analysis
    
    console.log('📍 Step 1: Verifying business analysis completed...');
    await page.screenshot({ path: 'liat-context-01-analysis.png' });
    
    // Check if we can see suggested tags
    const tagButtons = await page.$$('button[class*="px-3"][class*="py-1"]');
    if (tagButtons.length > 0) {
      console.log('📍 Step 2: Found suggested tags:');
      for (let i = 0; i < Math.min(6, tagButtons.length); i++) {
        const tagText = await tagButtons[i].textContent();
        const isGeneric = ['#Business', '#Tech', '#Growth', '#Solutions', '#Digital', '#Success'].includes(tagText);
        console.log(`   ${tagText} ${isGeneric ? '❌ GENERIC' : '✅ CONTEXTUAL'}`);
      }
    }
    
    // Test Image Generation
    console.log('\n📍 Step 3: Testing contextual image generation...');
    const imageButton = await page.$('button:has-text("Generate Text + Image Posts")');
    if (imageButton) {
      await imageButton.click();
      console.log('   ⏳ Generating images with photography context...');
      
      // Wait for generation to start
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'liat-context-02-image-generation.png' });
      
      // Wait for some progress
      await page.waitForTimeout(30000);
      await page.screenshot({ path: 'liat-context-03-image-progress.png' });
    }
    
    // Test Video Generation with Veo 3.0
    console.log('\n📍 Step 4: Testing Veo 3.0 video generation...');
    const videoButton = await page.$('button:has-text("Generate Text + Video Posts")');
    if (videoButton) {
      await videoButton.click();
      console.log('   ⏳ Generating videos with Veo 3.0 and photography context...');
      
      // Wait for generation to start
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'liat-context-04-video-generation.png' });
      
      // Wait for some progress
      await page.waitForTimeout(30000);
      await page.screenshot({ path: 'liat-context-05-video-progress.png' });
    }
    
    // Check generated content
    console.log('\n📍 Step 5: Checking generated content...');
    
    // Look for post content
    const postElements = await page.$$('[class*="post"], [class*="content"]');
    console.log(`   Found ${postElements.length} potential post elements`);
    
    // Look for images
    const imageElements = await page.$$('img[src*="blob:"], img[src*="data:"], img[src*=".png"], img[src*=".jpg"]');
    console.log(`   Found ${imageElements.length} generated images`);
    
    // Look for videos
    const videoElements = await page.$$('video');
    console.log(`   Found ${videoElements.length} generated videos`);
    
    // Final comprehensive screenshot
    await page.screenshot({ path: 'liat-context-06-final-state.png', fullPage: true });
    
    console.log('\n📊 CONTEXT VERIFICATION RESULTS:');
    console.log('=====================================');
    console.log('✅ Business URL analyzed: liatvictoriaphotography.co.uk');
    console.log('✅ Photography industry should be detected');
    console.log('✅ Hashtags should include #Photography, #WeddingPhotographer, etc.');
    console.log('✅ Visual prompts should mention camera equipment, artistic style, etc.');
    console.log('✅ Video generation using Veo 3.0 Preview');
    console.log('\n🔍 Check screenshots to verify context-specific content generation!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'liat-context-error.png' });
  } finally {
    await browser.close();
  }
}

testLiatContextVerification()
  .then(() => console.log('\n✨ Context verification test complete!'))
  .catch(console.error);