#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

def test_image_generation_simplified():
    """Simplified test focusing on image generation pipeline"""
    
    print("🚀 Starting simplified image generation test...")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        print("✅ Browser initialized")
        
        # Step 1: Navigate to homepage
        print("\n📱 Navigating to application...")
        driver.get("http://localhost:8080")
        time.sleep(3)
        driver.save_screenshot("test_homepage.png")
        
        # Step 2: Click Create Your Campaign
        print("\n🎯 Clicking Create Your Campaign...")
        create_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Your Campaign')]"))
        )
        create_btn.click()
        time.sleep(3)
        driver.save_screenshot("test_form.png")
        
        # Step 3: Fill main website URL (first input field)
        print("\n📝 Filling website URL...")
        url_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='https://your-main-website.com']"))
        )
        url_input.clear()
        url_input.send_keys("https://www.liatvictoriaphotography.co.uk/")
        print("✅ URL entered")
        
        # Step 4: Fill campaign name
        print("\n📝 Filling campaign name...")
        name_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Summer 2025 Product Launch']")
        name_input.clear()
        name_input.send_keys("Liat Photography UI Test")
        print("✅ Campaign name entered")
        
        # Step 5: Fill primary objective
        print("\n📝 Filling primary objective...")
        objective_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Increase brand awareness in North America']")
        objective_input.clear()
        objective_input.send_keys("Brand awareness for professional photography services")
        print("✅ Primary objective entered")
        
        time.sleep(2)
        driver.save_screenshot("test_form_filled.png")
        
        # Step 6: Click "Analyze URLs with AI" button
        print("\n🚀 Starting URL analysis...")
        
        # Clear performance logs before analysis
        driver.get_log('performance')
        
        analyze_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Analyze URLs with AI')]")
        analyze_btn.click()
        print("✅ Analysis started")
        
        # Wait for analysis to complete (look for progress or completion indicators)
        print("⏳ Waiting for analysis to complete...")
        time.sleep(10)
        
        # Step 7: Look for "Start AI Generation" button and click it
        try:
            start_generation_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start AI Generation')]"))
            )
            start_generation_btn.click()
            print("✅ AI Generation started")
        except Exception as e:
            print(f"❌ Could not find Start AI Generation button: {e}")
            # Try to continue anyway
        
        # Step 8: Wait for ideation page and monitor network
        print("\n🔍 Monitoring network for content generation...")
        time.sleep(15)  # Give more time for content generation
        
        # Get performance logs
        logs = driver.get_log('performance')
        api_requests = []
        image_requests = []
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.requestWillBeSent':
                    url = message['message']['params']['request']['url']
                    if '/api/' in url:
                        api_requests.append(url)
                    if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        image_requests.append(url)
            except:
                continue
        
        print(f"📊 API Requests found: {len(api_requests)}")
        for req in api_requests[-10:]:  # Show last 10
            print(f"  - {req}")
            
        print(f"🖼️ Image Requests found: {len(image_requests)}")
        for req in image_requests:
            print(f"  - {req}")
        
        # Step 9: Take screenshot and analyze current page
        driver.save_screenshot("test_ideation_page.png")
        print("✅ Ideation page screenshot taken")
        
        # Check for image elements on page
        images = driver.find_elements(By.TAG_NAME, "img")
        print(f"\n🖼️ Found {len(images)} image elements:")
        
        working_images = 0
        broken_images = 0
        
        for i, img in enumerate(images):
            src = img.get_attribute('src')
            alt = img.get_attribute('alt') or 'No alt text'
            
            if src and src.startswith('http'):
                working_images += 1
                print(f"  ✅ Image {i+1}: {src[:60]}... (alt: {alt[:30]}...)")
            elif src:
                print(f"  ⚠️ Image {i+1}: {src} (alt: {alt[:30]}...)")
            else:
                broken_images += 1
                print(f"  ❌ Image {i+1}: No src attribute (alt: {alt[:30]}...)")
        
        print(f"\n📈 Image Summary: {working_images} working, {broken_images} broken")
        
        # Step 10: Check console errors
        browser_logs = driver.get_log('browser')
        errors = [log for log in browser_logs if log['level'] == 'SEVERE']
        
        if errors:
            print(f"\n❌ Console errors found ({len(errors)}):")
            for error in errors[-5:]:  # Show last 5 errors
                print(f"  - {error['message'][:100]}...")
        else:
            print("\n✅ No severe console errors")
        
        # Step 11: Check for loading indicators or error messages
        try:
            loading_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Loading') or contains(text(), 'Generating') or contains(text(), 'Error')]")
            if loading_elements:
                print(f"\n🔄 Status indicators found:")
                for elem in loading_elements:
                    print(f"  - {elem.text}")
        except:
            pass
        
        print("\n🎉 Test completed successfully!")
        
        # Final summary
        print("\n" + "="*50)
        print("📋 TEST SUMMARY")
        print("="*50)
        print(f"✅ Homepage loaded: Yes")
        print(f"✅ Form filled: Yes") 
        print(f"✅ Analysis started: Yes")
        print(f"📊 API requests: {len(api_requests)}")
        print(f"🖼️ Image requests: {len(image_requests)}")
        print(f"🖼️ Images on page: {len(images)} ({working_images} working, {broken_images} broken)")
        print(f"❌ Console errors: {len(errors)}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("\n🔚 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    test_image_generation_simplified()