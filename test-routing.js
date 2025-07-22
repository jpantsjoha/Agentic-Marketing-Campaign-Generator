import { chromium } from 'playwright';

async function testRouting() {
  console.log('🧪 Testing Frontend Routing');
  
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

  // Monitor network failures
  page.on('response', response => {
    if (response.status() >= 400) {
      console.log(`🔴 Failed Request: ${response.status()} ${response.url()}`);
    }
  });

  try {
    // Test 1: Homepage
    console.log('\n1. Testing homepage...');
    await page.goto('http://localhost:8080/');
    await page.waitForTimeout(2000);
    
    const homeTitle = await page.locator('h1').first().textContent();
    console.log(`✅ Homepage title: "${homeTitle}"`);

    // Test 2: Direct navigation to ideation
    console.log('\n2. Testing direct navigation to /ideation...');
    await page.goto('http://localhost:8080/ideation');
    await page.waitForTimeout(3000);
    
    // Take screenshot first to see what's rendered
    await page.screenshot({ path: 'ideation-debug.png', fullPage: true });
    
    // Check if we're still on homepage or actually on ideation page
    try {
      const ideationTitle = await page.locator('h1, h2').first().textContent({ timeout: 5000 });
      console.log(`📋 Ideation page title: "${ideationTitle}"`);
    } catch (e) {
      console.log('❌ No h1/h2 title found');
    }
    
    // Look for demo content
    const demoElements = await page.locator('text=Demo, text=demo, text=Create New Campaign').count();
    console.log(`🔍 Demo elements found: ${demoElements}`);
    
    // Look for ideation-specific elements
    const ideationElements = await page.locator('text=Post Ideas, text=Marketing Post, text=Ideation').count();
    console.log(`🔍 Ideation-specific elements found: ${ideationElements}`);
    
    // Take screenshot
    await page.screenshot({ path: 'routing-test-ideation.png', fullPage: true });

    // Test 3: Direct navigation to scheduling
    console.log('\n3. Testing direct navigation to /scheduling...');
    await page.goto('http://localhost:8080/scheduling');
    await page.waitForTimeout(3000);
    
    // Take screenshot first to see what's rendered
    await page.screenshot({ path: 'scheduling-debug.png', fullPage: true });
    
    try {
      const schedulingTitle = await page.locator('h1, h2').first().textContent({ timeout: 5000 });
      console.log(`📅 Scheduling page title: "${schedulingTitle}"`);
    } catch (e) {
      console.log('❌ No h1/h2 title found');
    }
    
    // Look for demo content
    const schedulingDemoElements = await page.locator('text=Demo, text=demo, text=Create New Campaign').count();
    console.log(`🔍 Demo elements found: ${schedulingDemoElements}`);
    
    // Look for scheduling-specific elements
    const schedulingElements = await page.locator('text=Schedule, text=Posts to Schedule, text=Publishing').count();
    console.log(`🔍 Scheduling-specific elements found: ${schedulingElements}`);
    
    // Take screenshot
    await page.screenshot({ path: 'routing-test-scheduling.png', fullPage: true });

    // Test 4: Check URL in browser
    const currentUrl = page.url();
    console.log(`🌐 Current URL: ${currentUrl}`);

    // Test 5: Check React Router errors
    const reactErrors = await page.locator('text=Error, text=Not Found, text=404').count();
    console.log(`❌ Error elements found: ${reactErrors}`);

  } catch (error) {
    console.error('❌ Routing test failed:', error);
  } finally {
    await browser.close();
  }
}

testRouting().catch(console.error);