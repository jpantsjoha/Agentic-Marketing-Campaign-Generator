import { chromium } from 'playwright';

async function testHashtagFix() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('🏷️ Testing hashtag fix on photography business...');
    
    // Navigate to homepage
    await page.goto('http://localhost:8096');
    await page.waitForTimeout(2000);
    
    // Start campaign
    await page.click('text="Create Your Campaign"');
    await page.waitForURL('**/new-campaign');
    
    // Fill photography business details
    await page.fill('input[placeholder*="Summer 2025 Product Launch"]', 'Liat Victoria Photography Campaign');
    await page.fill('input[placeholder*="Increase brand awareness"]', 'Increase bookings for professional photography services');
    await page.fill('input[placeholder*="your-main-website.com"]', 'https://liatvictoriaphotography.co.uk');
    
    // Analyze URLs
    await page.click('button:has-text("Analyze URLs with AI")');
    await page.waitForTimeout(15000); // Wait for API analysis
    
    // Take screenshot and check tags
    await page.screenshot({ path: 'hashtag-fix-test.png' });
    
    // Look for suggested tags section
    const tagButtons = await page.$$('button[class*="px-3"][class*="py-1"]');
    console.log(`Found ${tagButtons.length} tag buttons`);
    
    if (tagButtons.length > 0) {
      console.log('\\n🏷️ DETECTED HASHTAGS:');
      for (let i = 0; i < Math.min(8, tagButtons.length); i++) {
        const tagText = await tagButtons[i].textContent();
        const isGeneric = ['#Business', '#Tech', '#Growth', '#Solutions', '#Digital', '#Success'].includes(tagText);
        const isPhotography = tagText.includes('Photography') || tagText.includes('Photo') || tagText.includes('Creative') || tagText.includes('Art');
        
        console.log(`   ${tagText} ${isGeneric ? '❌ GENERIC' : isPhotography ? '✅ PHOTOGRAPHY' : '⚠️  OTHER'}`);
      }
    } else {
      console.log('❌ No hashtag buttons found');
    }
    
  } catch (error) {
    console.error('Test failed:', error.message);
    await page.screenshot({ path: 'hashtag-fix-error.png' });
  } finally {
    await browser.close();
  }
}

testHashtagFix().catch(console.error);