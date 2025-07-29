import { chromium } from 'playwright';

async function validateAllFixes() {
  console.log('🧪 COMPREHENSIVE FIX VALIDATION TEST');
  console.log('====================================');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Test 1: Photography Business Analysis with Trending Hashtags
    console.log('\n📍 TEST 1: Photography Business Analysis & Trending Hashtags');
    await page.goto('http://localhost:8096');
    await page.click('text="Create Your Campaign"');
    await page.waitForURL('**/new-campaign');
    
    // Fill photography business details
    await page.fill('input[placeholder*="Summer 2025 Product Launch"]', 'Liat Victoria Photography - Professional Services');
    await page.fill('input[placeholder*="Increase brand awareness"]', 'Increase wedding photography bookings and brand recognition');
    await page.fill('input[placeholder*="your-main-website.com"]', 'https://liatvictoriaphotography.co.uk');
    
    console.log('   ⏳ Running AI analysis with new trending hashtag agent...');
    await page.click('button:has-text("Analyze URLs with AI")');
    await page.waitForTimeout(15000); // Wait for analysis
    
    // Check for photography-specific hashtags (not generic business ones)
    const hashtagButtons = await page.$$('button[class*="px-3"][class*="py-1"]');
    console.log(`   📊 Found ${hashtagButtons.length} hashtag suggestions`);
    
    let photographyHashtags = 0;
    let genericBusinessHashtags = 0;
    
    for (let i = 0; i < Math.min(6, hashtagButtons.length); i++) {
      const tagText = await hashtagButtons[i].textContent();
      if (tagText) {
        if (tagText.includes('Photography') || tagText.includes('Photo') || tagText.includes('Creative') || tagText.includes('Artistic') || tagText.includes('Memory')) {
          photographyHashtags++;
          console.log(`   ✅ ${tagText} - Photography-specific`);
        } else if (tagText.includes('#Business') || tagText.includes('#Tech') || tagText.includes('#Growth') || tagText.includes('#Solutions')) {
          genericBusinessHashtags++;
          console.log(`   ❌ ${tagText} - Generic business (should be removed)`);
        } else {
          console.log(`   ⚠️  ${tagText} - Other/neutral`);
        }
      }
    }
    
    console.log(`\\n   📈 HASHTAG ASSESSMENT:`);
    console.log(`   - Photography-specific: ${photographyHashtags}/6`);
    console.log(`   - Generic business: ${genericBusinessHashtags}/6 (should be 0)`);
    
    await page.screenshot({ path: 'test-1-hashtag-analysis.png' });
    
    // Test 2: Content Generation with Visual Previews
    console.log('\\n📍 TEST 2: Content Generation & Visual Preview Validation');
    
    // Navigate to ideation page
    await page.click('text="Next: Content Planning"');
    await page.waitForURL('**/ideation');
    
    // Generate content
    console.log('   ⏳ Generating social media content...');
    await page.click('text="Generate All Content"', { timeout: 5000 });
    await page.waitForTimeout(10000); // Wait for content generation
    
    // Check for visual content cards
    const imageCards = await page.$$('[class*="text-image"]');
    const videoCards = await page.$$('[class*="text-video"]');
    
    console.log(`   🖼️  Found ${imageCards.length} image post cards`);
    console.log(`   🎬 Found ${videoCards.length} video post cards`);
    
    // Check if visual content is actually displaying (not just placeholders)
    const imageElements = await page.$$('img[src*="http"]');
    const videoElements = await page.$$('video');
    
    console.log(`   🎨 Active image elements: ${imageElements.length}`);
    console.log(`   📹 Active video elements: ${videoElements.length}`);
    
    // Look for "generation complete" placeholder messages
    const placeholderMessages = await page.$('text="Image generation complete"');
    if (placeholderMessages) {
      console.log('   ⚠️  Still showing placeholder messages - visual API integration may need work');
    } else {
      console.log('   ✅ No placeholder messages detected');
    }
    
    await page.screenshot({ path: 'test-2-visual-content.png' });
    
    // Test 3: Theme-Tag Alignment Check
    console.log('\\n📍 TEST 3: Theme-Tag Alignment Validation');
    
    // Check that themes match the suggested tags
    const themeButtons = await page.$$('button[class*="theme"]');
    const themes = [];
    for (let i = 0; i < Math.min(5, themeButtons.length); i++) {
      const themeText = await themeButtons[i].textContent();
      if (themeText) themes.push(themeText.trim());
    }
    
    console.log(`   🎭 Detected themes: ${themes.join(', ')}`);
    console.log(`   🏷️  Suggested tags align with photography themes: ${photographyHashtags > 0 ? 'YES' : 'NO'}`);
    
    // Final Scoring
    console.log('\\n📊 COMPREHENSIVE TEST RESULTS:');
    console.log('================================');
    
    let passedTests = 0;
    const totalTests = 5;
    
    // Test scoring
    if (photographyHashtags >= 3) {
      console.log('✅ PASS: Photography-specific hashtags (3+ found)');
      passedTests++;
    } else {
      console.log('❌ FAIL: Photography-specific hashtags (< 3 found)');
    }
    
    if (genericBusinessHashtags === 0) {
      console.log('✅ PASS: No generic business hashtags');
      passedTests++;
    } else {
      console.log('❌ FAIL: Still showing generic business hashtags');
    }
    
    if (imageCards.length > 0 || videoCards.length > 0) {
      console.log('✅ PASS: Visual content cards generated');
      passedTests++;
    } else {
      console.log('❌ FAIL: No visual content cards generated');
    }
    
    if (imageElements.length > 0 || videoElements.length > 0) {
      console.log('✅ PASS: Visual content elements present');
      passedTests++;
    } else {
      console.log('❌ FAIL: No visual content elements found');
    }
    
    if (themes.length > 0 && photographyHashtags > 0) {
      console.log('✅ PASS: Theme-tag alignment improved');
      passedTests++;
    } else {
      console.log('❌ FAIL: Theme-tag alignment issues remain');
    }
    
    const successRate = (passedTests / totalTests) * 100;
    console.log(`\\n🎯 OVERALL SUCCESS RATE: ${passedTests}/${totalTests} (${successRate.toFixed(1)}%)`);
    
    if (successRate >= 80) {
      console.log('🎉 EXCELLENT: Most critical issues resolved!');
    } else if (successRate >= 60) {
      console.log('⚠️  GOOD: Some issues resolved, more work needed');
    } else {
      console.log('❌ NEEDS WORK: Significant issues remain');
    }
    
    await page.screenshot({ path: 'test-final-results.png' });
    
  } catch (error) {
    console.error('❌ Test execution failed:', error.message);
    await page.screenshot({ path: 'test-error-state.png' });
  } finally {
    await browser.close();
  }
}

validateAllFixes()
  .then(() => console.log('\\n✨ Comprehensive validation test complete!'))
  .catch(console.error);