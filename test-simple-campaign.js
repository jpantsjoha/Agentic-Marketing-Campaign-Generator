import { chromium } from 'playwright';

async function testSimpleCampaign() {
  console.log('🧪 Simple Campaign Creation Test\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--disable-blink-features=AutomationControlled']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  
  const page = await context.newPage();
  
  try {
    // Navigate to homepage
    console.log('📍 Going to homepage...');
    await page.goto('http://localhost:8080');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'simple-01-homepage.png' });
    
    // Click Create Your Campaign
    console.log('📍 Clicking Create Your Campaign...');
    await page.click('text="Create Your Campaign"');
    await page.waitForURL('**/new-campaign');
    await page.screenshot({ path: 'simple-02-new-campaign.png' });
    
    // Fill form
    console.log('📍 Filling form...');
    await page.fill('input[placeholder*="Summer 2025 Product Launch"]', 'Test Photography Campaign');
    await page.fill('input[placeholder*="Increase brand awareness"]', 'Test objective for photography');
    await page.fill('input[placeholder*="your-main-website.com"]', 'https://liatvictoriaphotography.co.uk');
    
    await page.screenshot({ path: 'simple-03-filled.png' });
    
    // Click Analyze URLs
    console.log('📍 Clicking Analyze URLs...');
    await page.click('button:has-text("Analyze URLs with AI")');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'simple-04-analysis.png' });
    
    // Wait a bit more for analysis
    console.log('📍 Waiting for analysis completion...');
    await page.waitForTimeout(10000);
    await page.screenshot({ path: 'simple-05-post-analysis.png' });
    
    // Look for Start AI Generation button
    const startButton = await page.$('button:has-text("Start AI Generation")');
    if (startButton) {
      console.log('✅ Found Start AI Generation button');
      await startButton.click();
      console.log('📍 Clicked Start AI Generation');
      
      // Wait for some progress
      await page.waitForTimeout(5000);
      await page.screenshot({ path: 'simple-06-generation-started.png' });
      
      // Check current URL
      const currentUrl = page.url();
      console.log(`📍 Current URL: ${currentUrl}`);
      
    } else {
      console.log('❌ Start AI Generation button not found');
      
      // Look for other buttons
      const buttons = await page.$$('button');
      console.log(`Found ${buttons.length} buttons:`);
      for (let i = 0; i < buttons.length; i++) {
        const buttonText = await buttons[i].textContent();
        console.log(`   ${i + 1}. "${buttonText}"`);
      }
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'simple-error.png' });
  } finally {
    await browser.close();
  }
}

testSimpleCampaign()
  .then(() => console.log('✅ Simple test complete'))
  .catch(console.error);