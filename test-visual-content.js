// Test visual content display in the ideation page
import { chromium } from 'playwright';

async function testVisualContent() {
  console.log('🎨 Testing Visual Content Display');
  
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Enable console logging
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('🔴 Console Error:', msg.text());
    } else if (msg.type() === 'log') {
      console.log('📝 Console Log:', msg.text());
    }
  });

  try {
    console.log('\n1. Navigating to ideation page...');
    await page.goto('http://localhost:8080/ideation');
    await page.waitForTimeout(3000);
    
    // Take a screenshot to see current state
    await page.screenshot({ path: 'visual-content-before.png', fullPage: true });

    // Look for image elements
    const imageCount = await page.locator('img').count();
    console.log(`🖼️ Found ${imageCount} image elements on page`);

    // Look for video elements
    const videoCount = await page.locator('video').count();
    console.log(`🎬 Found ${videoCount} video elements on page`);

    // Look for generation buttons
    const generateButtons = await page.locator('button:has-text("Generate")').count();
    console.log(`🎯 Found ${generateButtons} generate buttons`);

    // Check if demo campaign creation works
    const createCampaignButton = await page.locator('button:has-text("Create New Campaign")');
    if (await createCampaignButton.count() > 0) {
      console.log('✅ Found "Create New Campaign" button - clicking it...');
      await createCampaignButton.click();
      await page.waitForTimeout(2000);
      
      // Take screenshot of campaign creation page
      await page.screenshot({ path: 'campaign-creation.png', fullPage: true });
    }
    
  } catch (error) {
    console.error('❌ Visual content test failed:', error);
  } finally {
    await browser.close();
  }
}

testVisualContent().catch(console.error);