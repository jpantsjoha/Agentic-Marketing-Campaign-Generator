#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
import time
import json
import sys

def test_image_generation_flow():
    """Test the complete image generation and display flow"""
    
    print("🚀 Starting Selenium test for image generation flow...")
    
    # Set up Chrome options for better debugging
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Enable logging - modern way
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
    
    driver = None
    try:
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        print("✅ Browser initialized successfully")
        
        # Step 1: Navigate to application
        print("\n📱 Step 1: Navigating to http://localhost:8080...")
        driver.get("http://localhost:8080")
        time.sleep(3)
        
        # Take initial screenshot
        driver.save_screenshot("step1_homepage.png")
        print("✅ Homepage loaded, screenshot saved as step1_homepage.png")
        
        # Step 2: Create new campaign
        print("\n🎯 Step 2: Creating new campaign...")
        
        # Look for "Create Your Campaign" button
        try:
            new_campaign_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Your Campaign')]"))
            )
            new_campaign_btn.click()
            print("✅ Create Your Campaign button clicked")
        except Exception as e:
            print(f"❌ Could not find Create Your Campaign button: {e}")
            # Try alternative selectors
            try:
                new_campaign_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Create') and contains(text(), 'Campaign')]")
                new_campaign_btn.click()
                print("✅ Alternative Create Campaign button clicked")
            except:
                print("❌ No campaign creation button found")
                return
        
        time.sleep(2)
        driver.save_screenshot("step2_campaign_form.png")
        
        # Step 3: Fill in campaign details
        print("\n📝 Step 3: Filling campaign details...")
        
        # Website URL
        try:
            url_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='url' or @placeholder*='website' or @placeholder*='URL' or @name*='url' or @id*='url']"))
            )
            url_input.clear()
            url_input.send_keys("https://www.liatvictoriaphotography.co.uk/")
            print("✅ Website URL entered")
        except Exception as e:
            print(f"❌ Could not find URL input: {e}")
        
        # Campaign Name
        try:
            name_input = driver.find_element(By.XPATH, "//input[@placeholder*='name' or @name*='name' or @id*='name']")
            name_input.clear()
            name_input.send_keys("Liat Photography UI Test")
            print("✅ Campaign name entered")
        except Exception as e:
            print(f"❌ Could not find name input: {e}")
        
        # Description
        try:
            desc_input = driver.find_element(By.XPATH, "//textarea[@placeholder*='description' or @name*='description'] | //input[@placeholder*='description' or @name*='description']")
            desc_input.clear()
            desc_input.send_keys("Professional wedding and portrait photography")
            print("✅ Description entered")
        except Exception as e:
            print(f"❌ Could not find description input: {e}")
        
        # Target Platforms (checkboxes or select)
        try:
            # Look for Instagram checkbox/option
            instagram_elem = driver.find_element(By.XPATH, "//input[@value='instagram' or @value='Instagram'] | //label[contains(text(), 'Instagram')]//input")
            if not instagram_elem.is_selected():
                instagram_elem.click()
            print("✅ Instagram selected")
        except Exception as e:
            print(f"❌ Could not find Instagram option: {e}")
        
        try:
            # Look for Facebook checkbox/option
            facebook_elem = driver.find_element(By.XPATH, "//input[@value='facebook' or @value='Facebook'] | //label[contains(text(), 'Facebook')]//input")
            if not facebook_elem.is_selected():
                facebook_elem.click()
            print("✅ Facebook selected")
        except Exception as e:
            print(f"❌ Could not find Facebook option: {e}")
        
        # Objectives
        try:
            objective_elem = driver.find_element(By.XPATH, "//select[@name*='objective'] | //input[@value='brand awareness' or @value='Brand Awareness']")
            if objective_elem.tag_name == 'select':
                select = Select(objective_elem)
                select.select_by_visible_text("Brand Awareness")
            else:
                objective_elem.click()
            print("✅ Brand awareness objective selected")
        except Exception as e:
            print(f"❌ Could not find objective option: {e}")
        
        time.sleep(2)
        driver.save_screenshot("step3_form_filled.png")
        
        # Step 4: Submit and monitor network requests
        print("\n🚀 Step 4: Submitting form and monitoring network...")
        
        # Clear performance logs before submission
        driver.get_log('performance')
        
        # Submit form
        try:
            submit_btn = driver.find_element(By.XPATH, "//button[@type='submit'] | //button[contains(text(), 'Create') or contains(text(), 'Submit') or contains(text(), 'Generate')]")
            submit_btn.click()
            print("✅ Form submitted")
        except Exception as e:
            print(f"❌ Could not find submit button: {e}")
            return
        
        # Wait for navigation to ideation page
        print("⏳ Waiting for ideation page to load...")
        time.sleep(5)
        
        # Step 5: Monitor network requests
        print("\n🔍 Step 5: Analyzing network requests...")
        
        # Get performance logs
        logs = driver.get_log('performance')
        api_requests = []
        
        for log in logs:
            message = json.loads(log['message'])
            if message['message']['method'] == 'Network.requestWillBeSent':
                url = message['message']['params']['request']['url']
                if '/api/' in url:
                    api_requests.append(url)
                    
        print(f"📊 Found {len(api_requests)} API requests:")
        for req in api_requests:
            print(f"  - {req}")
        
        # Wait for content generation
        print("⏳ Waiting for content generation...")
        time.sleep(10)
        
        # Step 6: Take screenshot of ideation page
        print("\n📸 Step 6: Taking screenshot of ideation page...")
        driver.save_screenshot("step6_ideation_page.png")
        print("✅ Ideation page screenshot saved as step6_ideation_page.png")
        
        # Check for image elements
        try:
            images = driver.find_elements(By.TAG_NAME, "img")
            print(f"🖼️ Found {len(images)} image elements on page")
            
            for i, img in enumerate(images[:5]):  # Check first 5 images
                src = img.get_attribute('src')
                alt = img.get_attribute('alt')
                print(f"  Image {i+1}: src='{src}', alt='{alt}'")
        except Exception as e:
            print(f"❌ Error checking images: {e}")
        
        # Step 7: Check browser console
        print("\n🔍 Step 7: Checking browser console for errors...")
        
        browser_logs = driver.get_log('browser')
        errors = [log for log in browser_logs if log['level'] == 'SEVERE']
        
        if errors:
            print(f"❌ Found {len(errors)} console errors:")
            for error in errors:
                print(f"  - {error['message']}")
        else:
            print("✅ No severe console errors found")
        
        # Get fresh performance logs for recent requests
        recent_logs = driver.get_log('performance')
        image_requests = []
        
        for log in recent_logs:
            message = json.loads(log['message'])
            if message['message']['method'] == 'Network.requestWillBeSent':
                url = message['message']['params']['request']['url']
                if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    image_requests.append(url)
        
        print(f"🖼️ Found {len(image_requests)} image requests:")
        for req in image_requests:
            print(f"  - {req}")
        
        # Final comprehensive screenshot
        driver.save_screenshot("final_state.png")
        print("✅ Final screenshot saved as final_state.png")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🔚 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    test_image_generation_flow()