// Test API integration and check for network errors
import { chromium } from 'playwright';

async function testApiIntegration() {
  console.log('🔌 Testing API Integration');
  
  const browser = await chromium.launch({ headless: false, slowMo: 1000 });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Monitor ALL network requests and responses
  page.on('request', request => {
    if (request.url().includes('api') || request.url().includes('8000')) {
      console.log(`📤 Request: ${request.method()} ${request.url()}`);
    }
  });

  page.on('response', response => {
    if (response.url().includes('api') || response.url().includes('8000')) {
      console.log(`📥 Response: ${response.status()} ${response.url()}`);
    }
  });

  // Capture console logs (errors especially)
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('🔴 Console Error:', msg.text());
    } else if (msg.type() === 'log' && (msg.text().includes('API') || msg.text().includes('fetch') || msg.text().includes('error'))) {
      console.log('📝 API Log:', msg.text());
    }
  });

  try {
    console.log('\n1. Testing homepage first...');
    await page.goto('http://localhost:8080/');
    await page.waitForTimeout(2000);
    
    console.log('\n2. Testing new campaign creation...');
    await page.click('text=Create New Campaign');
    await page.waitForTimeout(2000);
    
    // Check if we're on the new campaign page
    const currentUrl = page.url();
    console.log(`📍 Current URL: ${currentUrl}`);
    
    if (currentUrl.includes('new-campaign')) {
      console.log('✅ Successfully navigated to new campaign page');
      
      // Fill in a basic campaign
      await page.fill('input[name="name"]', 'Test API Campaign');
      await page.fill('input[name="objective"]', 'Test API integration');
      await page.fill('input[name="businessUrl"]', 'https://example.com');
      await page.waitForTimeout(1000);
      
      // Submit the campaign
      console.log('\n3. Creating campaign and testing API...');
      await page.click('button:has-text("Create Campaign")');
      await page.waitForTimeout(3000);
      
      // Check if we're redirected to ideation
      const newUrl = page.url();
      console.log(`📍 After creation URL: ${newUrl}`);
      
      if (newUrl.includes('ideation')) {
        console.log('✅ Successfully created campaign and redirected to ideation');
        
        // Try to generate content to test API
        console.log('\n4. Testing content generation API...');
        const generateButtons = await page.locator('button:has-text("Generate")');
        const buttonCount = await generateButtons.count();
        
        if (buttonCount > 0) {
          console.log(`Found ${buttonCount} generate buttons`);
          
          // Click the first generate button
          await generateButtons.first().click();
          console.log('🎯 Clicked generate button - monitoring API calls...');
          
          // Wait longer to see API responses
          await page.waitForTimeout(10000);
        } else {
          console.log('❌ No generate buttons found');
        }
      } else {
        console.log('❌ Not redirected to ideation page after campaign creation');
      }
    } else {
      console.log('❌ Not on new campaign page');
    }
    
  } catch (error) {
    console.error('❌ API integration test failed:', error);
  }

  console.log('\n5. Taking final screenshot...');
  await page.screenshot({ path: 'api-integration-test.png', fullPage: true });

  console.log('\n6. Checking backend health directly...');
  try {
    const healthResponse = await page.goto('http://localhost:8000/health');
    console.log(`Backend health check: ${healthResponse ? healthResponse.status() : 'No response'}`);
  } catch (e) {
    console.log('❌ Backend health check failed:', e.message);
  }

  await browser.close();
}

testApiIntegration().catch(console.error);