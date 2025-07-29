#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import requests

def diagnostic_test():
    """Quick diagnostic test to identify image pipeline issues"""
    
    print("🔍 Starting diagnostic image test...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless for speed
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        print("✅ Browser initialized (headless)")
        
        # Step 1: Get to ideation page quickly
        print("\n🎯 Getting to ideation page...")
        driver.get("http://localhost:8080")
        time.sleep(2)
        
        # Click Create Campaign
        create_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Your Campaign')]"))
        )
        create_btn.click()
        time.sleep(2)
        
        # Fill form quickly
        url_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='https://your-main-website.com']"))
        )
        url_input.send_keys("https://www.liatvictoriaphotography.co.uk/")
        
        name_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Summer 2025 Product Launch']")
        name_input.send_keys("Diagnostic Test")
        
        objective_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Increase brand awareness in North America']")
        objective_input.send_keys("Brand awareness")
        
        # Start analysis
        analyze_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Analyze URLs with AI')]")
        analyze_btn.click()
        print("✅ Analysis started")
        
        # Wait for analysis completion
        time.sleep(8)
        
        # Try to start generation
        try:
            start_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start AI Generation')]"))
            )
            start_btn.click()
            print("✅ Generation started")
        except:
            print("⚠️ Could not find Start AI Generation button")
        
        # Wait a bit for generation to begin
        time.sleep(5)
        
        # Step 2: Analyze current state
        print("\n📊 Analyzing current state...")
        
        # Check URL
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Check for visual content elements
        images = driver.find_elements(By.TAG_NAME, "img")
        print(f"Images on page: {len(images)}")
        
        # Check for visual content containers or placeholders
        visual_containers = driver.find_elements(By.XPATH, "//*[contains(@class, 'visual') or contains(@class, 'image') or contains(@class, 'content')]")
        print(f"Visual containers: {len(visual_containers)}")
        
        # Check page text for clues
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if "AI-generated content themes will appear here" in page_text:
            print("✅ Found content placeholder text")
        if "Loading" in page_text or "Generating" in page_text:
            print("🔄 Found loading indicators")
        
        # Step 3: Check API calls
        print("\n🔌 Checking API calls...")
        
        logs = driver.get_log('performance')
        api_calls = []
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.requestWillBeSent':
                    url = message['message']['params']['request']['url']
                    if '/api/' in url:
                        api_calls.append(url)
            except:
                continue
        
        print(f"Total API calls: {len(api_calls)}")
        
        # Categorize API calls
        analysis_calls = [c for c in api_calls if 'analysis' in c]
        content_calls = [c for c in api_calls if 'content' in c]
        visual_calls = [c for c in api_calls if 'visual' in c]
        campaign_calls = [c for c in api_calls if 'campaign' in c]
        
        print(f"  - Analysis calls: {len(analysis_calls)}")
        print(f"  - Content calls: {len(content_calls)}")
        print(f"  - Visual calls: {len(visual_calls)}")
        print(f"  - Campaign calls: {len(campaign_calls)}")
        
        if visual_calls:
            print("🎯 Visual API calls found:")
            for call in visual_calls:
                print(f"  - {call}")
        else:
            print("❌ No visual API calls detected!")
        
        # Step 4: Direct API testing
        print("\n🧪 Testing direct API calls...")
        
        try:
            # Test if backend is responding
            health = requests.get("http://localhost:8000/health", timeout=3)
            print(f"✅ Backend health: {health.status_code}")
            
            # Test visual content endpoint directly
            test_campaign_id = "test_diagnostic"
            visual_url = f"http://localhost:8000/api/v1/content/visual/{test_campaign_id}"
            visual_response = requests.get(visual_url, timeout=5)
            print(f"📸 Visual endpoint test: {visual_response.status_code}")
            
            if visual_response.status_code == 200:
                print("✅ Visual endpoint is working")
            elif visual_response.status_code == 404:
                print("⚠️ Visual endpoint returns 404 (campaign not found)")
            else:
                print(f"❌ Visual endpoint error: {visual_response.status_code}")
                
        except Exception as e:
            print(f"❌ Direct API test failed: {e}")
        
        # Step 5: Check frontend implementation
        print("\n🔍 Checking frontend implementation...")
        
        # Look for JavaScript errors
        browser_logs = driver.get_log('browser')
        js_errors = [log for log in browser_logs if log['level'] == 'SEVERE']
        
        if js_errors:
            print(f"❌ JavaScript errors found ({len(js_errors)}):")
            for error in js_errors[-3:]:
                print(f"  - {error['message'][:80]}...")
        else:
            print("✅ No severe JavaScript errors")
        
        # Take final screenshot
        driver.save_screenshot("diagnostic_final_state.png")
        print("📸 Screenshot saved: diagnostic_final_state.png")
        
        # Step 6: Generate diagnosis
        print("\n" + "="*50)
        print("🩺 DIAGNOSTIC RESULTS")
        print("="*50)
        
        diagnosis = []
        
        if len(visual_calls) == 0:
            diagnosis.append("❌ CRITICAL: No visual content API calls detected")
            diagnosis.append("   → Frontend is not requesting visual content")
            diagnosis.append("   → Check IdeationPage.tsx visual content integration")
        
        if len(images) == 0:
            diagnosis.append("❌ CRITICAL: No images rendered on page")
            diagnosis.append("   → Visual content is not being displayed")
        
        if len(js_errors) > 0:
            diagnosis.append(f"❌ WARNING: {len(js_errors)} JavaScript errors detected")
            diagnosis.append("   → May be preventing visual content loading")
        
        if "AI-generated content themes will appear here" in page_text:
            diagnosis.append("⚠️ INFO: Placeholder text still visible")
            diagnosis.append("   → Content generation may not have started/completed")
        
        if len(visual_calls) > 0 and len(images) == 0:
            diagnosis.append("❌ CRITICAL: API called but no images displayed")
            diagnosis.append("   → Backend may return invalid URLs or frontend rendering issue")
        
        for item in diagnosis:
            print(item)
        
        if not diagnosis:
            print("✅ No obvious issues detected - may need deeper investigation")
        
        return {
            'api_calls': len(api_calls),
            'visual_calls': len(visual_calls),
            'images': len(images),
            'js_errors': len(js_errors),
            'diagnosis': diagnosis
        }
        
    except Exception as e:
        print(f"❌ Diagnostic test failed: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    result = diagnostic_test()
    if result:
        print(f"\n📋 Final result: {result}")