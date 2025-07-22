// Debug homepage to see available buttons and content
import { chromium } from 'playwright';

async function debugHomepage() {
  const browser = await chromium.launch({ headless: false, slowMo: 1000 });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:8080/');
    await page.waitForTimeout(3000);
    
    // Get all buttons
    const buttons = await page.locator('button').all();
    console.log(`Found ${buttons.length} buttons:`);
    
    for (let i = 0; i < buttons.length; i++) {
      const text = await buttons[i].textContent();
      const isVisible = await buttons[i].isVisible();
      console.log(`  Button ${i + 1}: "${text}" (visible: ${isVisible})`);
    }
    
    // Get all links
    const links = await page.locator('a').all();
    console.log(`\nFound ${links.length} links:`);
    
    for (let i = 0; i < Math.min(10, links.length); i++) {
      const text = await links[i].textContent();
      const href = await links[i].getAttribute('href');
      const isVisible = await links[i].isVisible();
      console.log(`  Link ${i + 1}: "${text}" -> ${href} (visible: ${isVisible})`);
    }
    
    // Look for campaign-related text
    const campaignElements = await page.locator('text*=Campaign, text*=campaign, text*=Create, text*=New').all();
    console.log(`\nFound ${campaignElements.length} campaign-related elements:`);
    
    for (let i = 0; i < campaignElements.length; i++) {
      const text = await campaignElements[i].textContent();
      const isVisible = await campaignElements[i].isVisible();
      console.log(`  Element ${i + 1}: "${text}" (visible: ${isVisible})`);
    }
    
    await page.screenshot({ path: 'debug-homepage.png', fullPage: true });
    
  } finally {
    await browser.close();
  }
}

debugHomepage().catch(console.error);