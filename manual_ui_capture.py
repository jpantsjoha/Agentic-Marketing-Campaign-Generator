#!/usr/bin/env python3
"""
Manual UI Capture for the new campaign form
"""

import time
import asyncio
from playwright.async_api import async_playwright

async def capture_campaign_form():
    """Capture screenshots of the campaign form process"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1440, 'height': 900},
            device_scale_factor=2
        )
        page = await context.new_page()
        
        screenshots = []
        
        try:
            print("🌐 Navigating to application...")
            await page.goto("http://localhost:8097")
            await page.wait_for_timeout(3000)
            
            # Click Create Your Campaign
            print("📝 Starting campaign creation...")
            await page.click('button:has-text("Create Your Campaign")')
            await page.wait_for_timeout(3000)
            
            # Fill out the form manually with proper selectors
            print("📝 Filling out campaign form...")
            
            # Campaign Name
            campaign_name_input = await page.query_selector('input[placeholder*="Summer"], input[placeholder*="Product Launch"]')
            if campaign_name_input:
                await campaign_name_input.fill("TechCorp Product Launch 2025")
            
            # Primary Objective  
            objective_input = await page.query_selector('input[placeholder*="brand awareness"], input[placeholder*="North America"]')
            if objective_input:
                await objective_input.fill("Increase brand awareness and generate leads for cloud solutions")
            
            # Business description
            business_textarea = await page.query_selector('textarea[placeholder*="company"], textarea[placeholder*="products"]')
            if business_textarea:
                await business_textarea.fill("TechCorp Solutions provides innovative cloud infrastructure services for startups and enterprises. We help businesses scale their operations efficiently with our cutting-edge cloud platform and AI-powered automation tools.")
            
            await page.wait_for_timeout(2000)
            
            # Screenshot after filling form
            print("📸 Taking filled form screenshot...")
            filled_form_path = "/Users/jp/Library/Mobile Documents/com~apple~CloudDocs/Documents/workspaces/video-venture-launch/ui-validation-new-form-filled.png"
            await page.screenshot(path=filled_form_path, full_page=True)
            screenshots.append(("New Form Filled", filled_form_path))
            
            # Try to start AI generation
            print("🚀 Starting AI generation...")
            start_button = await page.query_selector('button:has-text("Start AI Generation")')
            if start_button:
                await start_button.click()
                print("⏳ Waiting for AI generation...")
                await page.wait_for_timeout(10000)
                
                # Screenshot of generation process
                print("📸 Taking generation process screenshot...")
                generation_path = "/Users/jp/Library/Mobile Documents/com~apple~CloudDocs/Documents/workspaces/video-venture-launch/ui-validation-generation-process.png"
                await page.screenshot(path=generation_path, full_page=True)
                screenshots.append(("Generation Process", generation_path))
            
            print("✨ Manual interaction time - please continue with the form...")
            print("Press Enter to take a final screenshot when done...")
            
            # Wait for manual interaction
            await asyncio.sleep(30)  # Give time for manual testing
            
            # Final screenshot
            print("📸 Taking final state screenshot...")
            final_path = "/Users/jp/Library/Mobile Documents/com~apple~CloudDocs/Documents/workspaces/video-venture-launch/ui-validation-final-state.png"
            await page.screenshot(path=final_path, full_page=True)
            screenshots.append(("Final State", final_path))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            error_path = "/Users/jp/Library/Mobile Documents/com~apple~CloudDocs/Documents/workspaces/video-venture-launch/ui-validation-manual-error.png"
            await page.screenshot(path=error_path, full_page=True)
            screenshots.append(("Error State", error_path))
        
        finally:
            print("🔍 Browser will stay open for manual inspection...")
            await asyncio.sleep(10)  # Keep browser open for inspection
            await browser.close()
        
        return screenshots

async def main():
    print("🎬 Starting manual UI capture...")
    screenshot_results = await capture_campaign_form()
    
    print("\n📋 Screenshot Summary:")
    for name, path in screenshot_results:
        print(f"  • {name}: {path}")

if __name__ == "__main__":
    asyncio.run(main())