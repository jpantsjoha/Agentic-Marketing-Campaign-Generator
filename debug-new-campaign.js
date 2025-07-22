// Debug new-campaign page to see form structure
import { chromium } from 'playwright';

async function debugNewCampaign() {
  const browser = await chromium.launch({ headless: false, slowMo: 1000 });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/new-campaign');
    await page.waitForTimeout(3000);
    
    // Get all input fields
    const inputs = await page.locator('input').all();
    console.log(`Found ${inputs.length} input fields:`);
    
    for (let i = 0; i < inputs.length; i++) {
      const name = await inputs[i].getAttribute('name');
      const type = await inputs[i].getAttribute('type');
      const placeholder = await inputs[i].getAttribute('placeholder');
      const isVisible = await inputs[i].isVisible();
      console.log(`  Input ${i + 1}: name="${name}", type="${type}", placeholder="${placeholder}" (visible: ${isVisible})`);
    }
    
    // Get all textareas
    const textareas = await page.locator('textarea').all();
    console.log(`\nFound ${textareas.length} textarea fields:`);
    
    for (let i = 0; i < textareas.length; i++) {
      const name = await textareas[i].getAttribute('name');
      const placeholder = await textareas[i].getAttribute('placeholder');
      const isVisible = await textareas[i].isVisible();
      console.log(`  Textarea ${i + 1}: name="${name}", placeholder="${placeholder}" (visible: ${isVisible})`);
    }
    
    // Get all select fields
    const selects = await page.locator('select').all();
    console.log(`\nFound ${selects.length} select fields:`);
    
    for (let i = 0; i < selects.length; i++) {
      const name = await selects[i].getAttribute('name');
      const isVisible = await selects[i].isVisible();
      console.log(`  Select ${i + 1}: name="${name}" (visible: ${isVisible})`);
    }
    
    // Get all labels to understand the form structure
    const labels = await page.locator('label').all();
    console.log(`\nFound ${labels.length} labels:`);
    
    for (let i = 0; i < Math.min(10, labels.length); i++) {
      const text = await labels[i].textContent();
      const isVisible = await labels[i].isVisible();
      console.log(`  Label ${i + 1}: "${text}" (visible: ${isVisible})`);
    }
    
    await page.screenshot({ path: 'debug-new-campaign.png', fullPage: true });
    
  } finally {
    await browser.close();
  }
}

debugNewCampaign().catch(console.error);