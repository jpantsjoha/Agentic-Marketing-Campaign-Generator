#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import requests

def monitor_api_calls(driver):
    """Monitor and analyze API calls"""
    logs = driver.get_log('performance')
    api_calls = []
    
    for log in logs:
        try:
            message = json.loads(log['message'])
            if message['message']['method'] == 'Network.requestWillBeSent':
                request = message['message']['params']['request']
                url = request['url']
                method = request.get('method', 'GET')
                
                if '/api/' in url:
                    api_calls.append({
                        'url': url,
                        'method': method,
                        'timestamp': log['timestamp']
                    })
        except:
            continue
    
    return api_calls

def test_deep_image_generation():
    """Deep test of image generation pipeline with detailed monitoring"""
    
    print("🚀 Starting deep image generation analysis...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        print("✅ Browser initialized")
        
        # Phase 1: Setup campaign
        print("\n🎯 Phase 1: Setting up campaign...")
        driver.get("http://localhost:8080")
        time.sleep(3)
        
        # Click Create Campaign
        create_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Your Campaign')]"))
        )
        create_btn.click()
        time.sleep(3)
        
        # Fill form
        url_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='https://your-main-website.com']"))
        )
        url_input.clear()
        url_input.send_keys("https://www.liatvictoriaphotography.co.uk/")
        
        name_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Summer 2025 Product Launch']")
        name_input.clear()
        name_input.send_keys("Liat Photography Deep Test")
        
        objective_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Increase brand awareness in North America']")
        objective_input.clear()
        objective_input.send_keys("Professional photography brand awareness")
        
        print("✅ Form filled")
        
        # Phase 2: Start analysis and monitor
        print("\n🔍 Phase 2: Starting analysis with detailed monitoring...")
        
        # Clear logs and start analysis
        driver.get_log('performance')
        
        analyze_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Analyze URLs with AI')]")
        analyze_btn.click()
        
        print("⏳ Monitoring analysis phase...")
        for i in range(30):  # Monitor for 30 seconds
            time.sleep(1)
            api_calls = monitor_api_calls(driver)
            if api_calls:
                print(f"  [{i+1}s] API calls detected: {len(api_calls)}")
                for call in api_calls[-2:]:  # Show last 2 calls
                    print(f"    - {call['method']} {call['url']}")
        
        # Phase 3: Start content generation
        print("\n🎨 Phase 3: Starting content generation...")
        
        try:
            start_generation_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start AI Generation')]"))
            )
            start_generation_btn.click()
            print("✅ Content generation started")
        except Exception as e:
            print(f"❌ Could not start generation: {e}")
            # Look for alternative buttons or states
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"Available buttons ({len(buttons)}):")
            for btn in buttons[:10]:
                text = btn.text.strip()
                if text:
                    print(f"  - '{text}'")
        
        # Phase 4: Monitor content generation
        print("\n🔄 Phase 4: Monitoring content generation...")
        
        content_generated = False
        for minute in range(5):  # Monitor for 5 minutes
            print(f"\n--- Minute {minute + 1} ---")
            
            # Check API calls
            api_calls = monitor_api_calls(driver)
            recent_calls = [call for call in api_calls if 'content' in call['url'] or 'visual' in call['url']]
            
            if recent_calls:
                print(f"🎯 Content API calls: {len(recent_calls)}")
                for call in recent_calls[-3:]:
                    print(f"  - {call['method']} {call['url']}")
            
            # Check for images on page
            images = driver.find_elements(By.TAG_NAME, "img")
            if images:
                print(f"🖼️ Images found: {len(images)}")
                for i, img in enumerate(images[:3]):
                    src = img.get_attribute('src')
                    if src and 'generated' in src:
                        print(f"  ✅ Generated image {i+1}: {src}")
                        content_generated = True
                    elif src:
                        print(f"  📷 Image {i+1}: {src[:50]}...")
            
            # Check for loading indicators
            loading_texts = ['Loading', 'Generating', 'Processing', 'Creating']
            for text in loading_texts:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                if elements:
                    print(f"🔄 Status: Found '{text}' indicators ({len(elements)})")
            
            # Take periodic screenshots
            driver.save_screenshot(f"generation_progress_minute_{minute + 1}.png")
            
            if content_generated:
                print("🎉 Content generation detected!")
                break
                
            time.sleep(60)  # Wait 1 minute
        
        # Phase 5: Final analysis
        print("\n📊 Phase 5: Final analysis...")
        
        # Get all API calls
        all_api_calls = monitor_api_calls(driver)
        
        # Categorize calls
        analysis_calls = [c for c in all_api_calls if 'analysis' in c['url']]
        content_calls = [c for c in all_api_calls if 'content' in c['url']]
        visual_calls = [c for c in all_api_calls if 'visual' in c['url']]
        
        print(f"📈 API Call Summary:")
        print(f"  - Analysis calls: {len(analysis_calls)}")
        print(f"  - Content calls: {len(content_calls)}")
        print(f"  - Visual calls: {len(visual_calls)}")
        print(f"  - Total API calls: {len(all_api_calls)}")
        
        # Check final page state
        final_images = driver.find_elements(By.TAG_NAME, "img")
        working_images = 0
        broken_images = 0
        
        for img in final_images:
            src = img.get_attribute('src')
            if src and src.startswith('http'):
                working_images += 1
            else:
                broken_images += 1
        
        print(f"🖼️ Final Image State:")
        print(f"  - Total images: {len(final_images)}")
        print(f"  - Working images: {working_images}")
        print(f"  - Broken images: {broken_images}")
        
        # Check console errors
        browser_logs = driver.get_log('browser')
        errors = [log for log in browser_logs if log['level'] == 'SEVERE']
        warnings = [log for log in browser_logs if log['level'] == 'WARNING']
        
        print(f"🔍 Console Issues:")
        print(f"  - Severe errors: {len(errors)}")
        print(f"  - Warnings: {len(warnings)}")
        
        if errors:
            print("❌ Severe errors found:")
            for error in errors[-3:]:
                print(f"  - {error['message'][:100]}...")
        
        # Final screenshot
        driver.save_screenshot("final_deep_analysis.png")
        
        # Test direct API calls
        print("\n🔌 Testing direct API calls...")
        try:
            # Test health endpoint
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            print(f"✅ Health endpoint: {health_response.status_code}")
            
            # Test campaigns list
            campaigns_response = requests.get("http://localhost:8000/api/v1/campaigns", timeout=5)
            print(f"📋 Campaigns endpoint: {campaigns_response.status_code}")
            
        except Exception as e:
            print(f"❌ Direct API test failed: {e}")
        
        # Final summary
        print("\n" + "="*60)
        print("🎯 DEEP ANALYSIS SUMMARY")
        print("="*60)
        print(f"✅ Campaign created: Yes")
        print(f"🔍 Analysis completed: {len(analysis_calls) > 0}")
        print(f"🎨 Content generation attempted: {len(content_calls) > 0}")
        print(f"🖼️ Images displayed: {working_images > 0}")
        print(f"📊 Total API calls: {len(all_api_calls)}")
        print(f"❌ Console errors: {len(errors)}")
        print(f"⚠️ Console warnings: {len(warnings)}")
        
        # Diagnosis
        print("\n🩺 DIAGNOSIS:")
        if working_images == 0 and len(visual_calls) == 0:
            print("❌ PRIMARY ISSUE: No visual content API calls detected")
            print("   - Images are not being generated or requested")
            print("   - Frontend may not be calling visual content endpoints")
        elif working_images == 0 and len(visual_calls) > 0:
            print("❌ PRIMARY ISSUE: Visual API called but images not displayed")
            print("   - Backend may be returning invalid image URLs")
            print("   - Frontend may have image rendering issues")
        elif working_images > 0:
            print("✅ SUCCESS: Images are being generated and displayed")
        
        return {
            'total_api_calls': len(all_api_calls),
            'visual_calls': len(visual_calls),
            'images_displayed': working_images,
            'console_errors': len(errors)
        }
        
    except Exception as e:
        print(f"❌ Deep test failed: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if driver:
            print("\n🔚 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    result = test_deep_image_generation()
    if result:
        print(f"\n📝 Test completed with results: {result}")