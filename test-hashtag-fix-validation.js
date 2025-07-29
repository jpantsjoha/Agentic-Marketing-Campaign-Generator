import { chromium } from 'playwright';

async function testHashtagContextFix() {
  console.log('🏷️ Testing Hashtag Context Fix Validation\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--disable-blink-features=AutomationControlled', '--disable-web-security']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  
  const page = await context.newPage();
  
  try {
    // Clear browser cache to ensure fresh content
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    console.log('📍 Step 1: Creating fresh photography campaign...');
    await page.goto('http://localhost:8082', { waitUntil: 'networkidle' });
    await page.click('text="Create Your Campaign"');
    await page.waitForURL('**/new-campaign');
    
    // Fill photography-specific details
    await page.fill('input[placeholder*="Summer 2025 Product Launch"]', 'Photography Business Campaign Test');
    await page.fill('input[placeholder*="Increase brand awareness"]', 'Increase visitors for Liat Victoria photography services');
    await page.fill('input[placeholder*="your-main-website.com"]', 'https://liatvictoriaphotography.co.uk');
    
    console.log('📍 Step 2: Triggering URL analysis...');
    await page.click('button:has-text("Analyze URLs with AI")');
    await page.waitForTimeout(15000); // Wait for analysis
    
    console.log('📍 Step 3: Checking suggested tags...');
    await page.screenshot({ path: 'hashtag-test-01-analysis-complete.png' });
    
    // Check suggested tags
    const tagButtons = await page.$$('button[class*="px-3"][class*="py-1"]');
    console.log(`Found ${tagButtons.length} tag buttons`);
    
    const tags = [];
    for (let i = 0; i < Math.min(10, tagButtons.length); i++) {
      const tagText = await tagButtons[i].textContent();
      tags.push(tagText);
    }
    
    console.log('\n🏷️  HASHTAG VALIDATION RESULTS:');
    console.log('=====================================');
    
    const genericTags = ['#Business', '#Tech', '#Growth', '#Solutions', '#Digital', '#Success'];
    const photographyTags = ['#Photography', '#WeddingPhotographer', '#PortraitPhotography', '#ArtisticPhotography', '#StudioPhotography', '#ProfessionalHeadshots'];
    
    let hasGenericTags = false;
    let hasPhotographyTags = false;
    
    tags.forEach(tag => {
      if (genericTags.includes(tag)) {
        console.log(`   ${tag} ❌ GENERIC - Should not appear for photography business`);
        hasGenericTags = true;
      } else if (photographyTags.includes(tag) || tag.includes('Photography') || tag.includes('Photo')) {
        console.log(`   ${tag} ✅ PHOTOGRAPHY-SPECIFIC - Correct context`);
        hasPhotographyTags = true;
      } else {
        console.log(`   ${tag} ⚠️  OTHER - May be contextual`);
      }
    });
    
    console.log('\n📊 VALIDATION SUMMARY:');
    if (hasGenericTags) {
      console.log('❌ FAILED: Generic tags still present');
    } else {
      console.log('✅ SUCCESS: No generic tags found');
    }
    
    if (hasPhotographyTags) {
      console.log('✅ SUCCESS: Photography-specific tags detected');
    } else {
      console.log('❌ FAILED: No photography-specific tags found');
    }
    
    // Additional debugging - check React context state
    const contextState = await page.evaluate(() => {
      // Try to access React context state for debugging
      return {
        localStorage: { ...localStorage },
        sessionStorage: { ...sessionStorage },
        url: window.location.href
      };
    });
    
    console.log('\n🔍 DEBUG INFO:');
    console.log('Current URL:', contextState.url);
    console.log('LocalStorage keys:', Object.keys(contextState.localStorage));
    
    await page.screenshot({ path: 'hashtag-test-02-final-state.png' });
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'hashtag-test-error.png' });
  } finally {
    await browser.close();
  }
}

testHashtagContextFix()
  .then(() => console.log('\n✨ Hashtag fix validation complete!'))
  .catch(console.error);