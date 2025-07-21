// Comprehensive UI Test Suite
import { chromium } from 'playwright';

async function runComprehensiveUITests() {
  console.log('🧪 COMPREHENSIVE UI TEST SUITE');
  console.log('================================\n');
  
  let passedTests = 0;
  let failedTests = 0;
  const testResults = [];
  
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Helper function to run a test
  async function runTest(testName, testFn) {
    console.log(`\n🔍 Testing: ${testName}`);
    try {
      await testFn();
      console.log(`✅ PASSED: ${testName}`);
      passedTests++;
      testResults.push({ test: testName, status: 'PASSED' });
    } catch (error) {
      console.log(`❌ FAILED: ${testName} - ${error.message}`);
      failedTests++;
      testResults.push({ test: testName, status: 'FAILED', error: error.message });
    }
  }

  // Test 1: Homepage loads correctly
  await runTest('Homepage loads correctly', async () => {
    await page.goto('http://localhost:8080/');
    await page.waitForLoadState('networkidle');
    const title = await page.locator('h1').first().textContent();
    if (!title.includes('AI Marketing Campaign')) throw new Error('Homepage title incorrect');
  });

  // Test 2: Backend API is healthy
  await runTest('Backend API health check', async () => {
    const response = await page.goto('http://localhost:8000/health');
    const data = await response.json();
    if (data.status !== 'healthy') throw new Error('Backend not healthy');
    if (!data.agent_initialized) throw new Error('Agent not initialized');
    if (!data.gemini_key_configured) throw new Error('Gemini key not configured');
  });

  // Test 3: Direct navigation to Ideation page
  await runTest('Direct navigation to /ideation', async () => {
    await page.goto('http://localhost:8080/ideation');
    await page.waitForLoadState('networkidle');
    const url = page.url();
    if (!url.includes('/ideation')) throw new Error('Redirected away from ideation page');
    const title = await page.locator('h2').first().textContent();
    if (!title.includes('Demo Ideation Page')) throw new Error('Not showing demo ideation page');
  });

  // Test 4: Visual content on Ideation page
  await runTest('Visual content on Ideation page', async () => {
    await page.goto('http://localhost:8080/ideation');
    await page.waitForTimeout(2000);
    const imageCount = await page.locator('img').count();
    const videoCount = await page.locator('video').count();
    if (imageCount < 2) throw new Error(`Expected 2+ images, found ${imageCount}`);
    if (videoCount < 1) throw new Error(`Expected 1+ videos, found ${videoCount}`);
  });

  // Test 5: Direct navigation to Scheduling page
  await runTest('Direct navigation to /scheduling', async () => {
    await page.goto('http://localhost:8080/scheduling');
    await page.waitForLoadState('networkidle');
    const url = page.url();
    if (!url.includes('/scheduling')) throw new Error('Redirected away from scheduling page');
    const title = await page.locator('h2').first().textContent();
    if (!title.includes('Demo Scheduling Page')) throw new Error('Not showing demo scheduling page');
  });

  // Test 6: Visual content on Scheduling page
  await runTest('Visual content on Scheduling page', async () => {
    await page.goto('http://localhost:8080/scheduling');
    await page.waitForTimeout(2000);
    const imageCount = await page.locator('img').count();
    const videoCount = await page.locator('video').count();
    if (imageCount < 1) throw new Error(`Expected 1+ images, found ${imageCount}`);
    if (videoCount < 1) throw new Error(`Expected 1+ videos, found ${videoCount}`);
  });

  // Test 7: Navigation between pages
  await runTest('Navigation between pages', async () => {
    await page.goto('http://localhost:8080/ideation');
    await page.click('button:has-text("Create New Campaign")');
    await page.waitForTimeout(1000);
    const url = page.url();
    if (!url.includes('/new-campaign')) throw new Error('Create campaign navigation failed');
  });

  // Test 8: Image loading validation
  await runTest('Images load successfully', async () => {
    await page.goto('http://localhost:8080/ideation');
    await page.waitForTimeout(3000);
    
    // Check if images actually loaded
    const images = await page.locator('img').all();
    for (const img of images) {
      const naturalWidth = await img.evaluate(el => el.naturalWidth);
      if (naturalWidth === 0) throw new Error('Image failed to load');
    }
  });

  // Test 9: Video elements present
  await runTest('Video elements functional', async () => {
    await page.goto('http://localhost:8080/ideation');
    await page.waitForTimeout(2000);
    
    const videos = await page.locator('video').all();
    if (videos.length === 0) throw new Error('No video elements found');
    
    // Check video has controls
    for (const video of videos) {
      const hasControls = await video.evaluate(el => el.hasAttribute('controls'));
      if (!hasControls) throw new Error('Video missing controls');
    }
  });

  // Test 10: API endpoints accessible
  await runTest('API endpoints accessible', async () => {
    // Test docs endpoint
    const docsResponse = await fetch('http://localhost:8000/docs');
    if (docsResponse.status !== 200) throw new Error('API docs not accessible');
    
    // Test campaigns endpoint  
    const campaignsResponse = await fetch('http://localhost:8000/api/v1/campaigns');
    if (campaignsResponse.status !== 200) throw new Error('Campaigns endpoint not accessible');
  });

  // Print test summary
  console.log('\n================================');
  console.log('📊 TEST SUMMARY');
  console.log('================================');
  console.log(`✅ Passed: ${passedTests}`);
  console.log(`❌ Failed: ${failedTests}`);
  console.log(`📈 Success Rate: ${((passedTests / (passedTests + failedTests)) * 100).toFixed(1)}%`);
  
  // Print detailed results
  console.log('\n📋 DETAILED RESULTS:');
  testResults.forEach(result => {
    const icon = result.status === 'PASSED' ? '✅' : '❌';
    console.log(`${icon} ${result.test}${result.error ? ` - ${result.error}` : ''}`);
  });

  await browser.close();
  
  // Return success/failure
  return failedTests === 0;
}

// Run the tests
runComprehensiveUITests()
  .then(success => {
    if (success) {
      console.log('\n🎉 ALL TESTS PASSED! Ready for commit.');
      process.exit(0);
    } else {
      console.log('\n⚠️  Some tests failed. Please review before committing.');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('\n❌ Test suite error:', error);
    process.exit(1);
  });