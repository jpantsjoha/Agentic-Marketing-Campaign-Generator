// Final integration test to validate the complete fix
import { chromium } from 'playwright';

async function testFinalIntegration() {
  console.log('🎯 Final Integration Test');
  
  const browser = await chromium.launch({ headless: false, slowMo: 1000 });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Monitor API calls
  page.on('request', request => {
    if (request.url().includes('8000')) {
      console.log(`📤 API Request: ${request.method()} ${request.url()}`);
    }
  });

  page.on('response', response => {
    if (response.url().includes('8000')) {
      console.log(`📥 API Response: ${response.status()} ${response.url()}`);
    }
  });

  // Monitor console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('🔴 Frontend Error:', msg.text());
    }
  });

  try {
    console.log('\n1. Testing homepage...');
    await page.goto('http://localhost:8080/');
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'homepage-test.png', fullPage: true });
    
    // Check if homepage loaded properly
    const title = await page.locator('h1').first().textContent({ timeout: 5000 });
    console.log(`✅ Homepage title: "${title}"`);

    console.log('\n2. Testing ideation page directly...');
    await page.goto('http://localhost:8080/ideation');
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'ideation-final-test.png', fullPage: true });
    
    // Check for demo images and videos
    const imageCount = await page.locator('img').count();
    const videoCount = await page.locator('video').count();
    console.log(`🖼️ Images found: ${imageCount}`);
    console.log(`🎬 Videos found: ${videoCount}`);

    // Check if we have working demo content
    if (imageCount > 0 && videoCount > 0) {
      console.log('✅ Demo visual content is working!');
    } else {
      console.log('❌ Demo visual content missing');
    }

    console.log('\n3. Testing scheduling page...');
    await page.goto('http://localhost:8080/scheduling');
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'scheduling-final-test.png', fullPage: true });
    
    const schedImageCount = await page.locator('img').count();
    const schedVideoCount = await page.locator('video').count();
    console.log(`📅 Scheduling page - Images: ${schedImageCount}, Videos: ${schedVideoCount}`);

    console.log('\n4. Testing backend API directly...');
    const healthResponse = await fetch('http://localhost:8000/health');
    const healthData = await healthResponse.json();
    console.log('🔧 Backend health:', JSON.stringify(healthData, null, 2));
    
  } catch (error) {
    console.error('❌ Final integration test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testFinalIntegration().catch(console.error);