// Test visual content display in the scheduling page
import { chromium } from 'playwright';

async function testSchedulingVisual() {
  console.log('📅 Testing Scheduling Page Visual Content');
  
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
    console.log('\n1. Navigating to scheduling page...');
    await page.goto('http://localhost:8080/scheduling');
    await page.waitForTimeout(3000);
    
    // Take a screenshot to see current state
    await page.screenshot({ path: 'scheduling-visual-after.png', fullPage: true });

    // Look for image elements
    const imageCount = await page.locator('img').count();
    console.log(`🖼️ Found ${imageCount} image elements on scheduling page`);

    // Look for video elements
    const videoCount = await page.locator('video').count();
    console.log(`🎬 Found ${videoCount} video elements on scheduling page`);

    // Look for demo posts
    const demoPosts = await page.locator('text=Demo Posts to Schedule').count();
    console.log(`📋 Found "Demo Posts to Schedule" section: ${demoPosts > 0 ? 'YES' : 'NO'}`);

    // Look for specific visual content indicators
    const imageOverlays = await page.locator('text=Scheduled Image, text=Demo Image').count();
    console.log(`🏷️ Found ${imageOverlays} image overlay labels`);

    const videoOverlays = await page.locator('text=Scheduled Video, text=Demo Video').count();
    console.log(`🏷️ Found ${videoOverlays} video overlay labels`);
    
  } catch (error) {
    console.error('❌ Scheduling visual test failed:', error);
  } finally {
    await browser.close();
  }
}

testSchedulingVisual().catch(console.error);