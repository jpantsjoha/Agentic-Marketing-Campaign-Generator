#!/usr/bin/env python3
"""
Selenium MCP Test for Video Venture Launch Integration
Direct test using Selenium WebDriver with better error handling
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """Setup Chrome driver with options for better stability"""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def take_screenshot(driver, name, description=""):
    """Take screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"selenium_mcp_{timestamp}_{name}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot: {filename} - {description}")
    return filename

def test_homepage_and_navigation(driver, base_url="http://localhost:8096"):
    """Test homepage and basic navigation"""
    print("\n=== Testing Homepage and Navigation ===")
    
    try:
        # Navigate to homepage
        driver.get(base_url)
        wait = WebDriverWait(driver, 15)
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)  # Additional wait for React to render
        
        # Take homepage screenshot
        homepage_screenshot = take_screenshot(driver, "homepage", "Homepage loaded")
        
        # Check page title
        title = driver.title
        print(f"Page title: {title}")
        
        # Check if React app has rendered by looking for any content
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"Body text length: {len(body_text)} characters")
        
        if len(body_text) < 100:
            print("⚠️  Page appears to be blank or minimal content")
            # Try to wait a bit more and refresh
            time.sleep(5)
            driver.refresh()
            time.sleep(3)
            body_text = driver.find_element(By.TAG_NAME, "body").text
            take_screenshot(driver, "homepage_after_refresh", "Homepage after refresh")
        
        # Look for common navigation elements
        nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav, [role='navigation'], a")
        print(f"Found {len(nav_elements)} navigation elements")
        
        # Look for any links or buttons
        links = driver.find_elements(By.TAG_NAME, "a")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(links)} links and {len(buttons)} buttons")
        
        return {
            "success": len(body_text) > 100,
            "title": title,
            "content_length": len(body_text),
            "nav_elements": len(nav_elements),
            "interactive_elements": len(links) + len(buttons),
            "screenshot": homepage_screenshot
        }
        
    except Exception as e:
        error_screenshot = take_screenshot(driver, "homepage_error", "Homepage error")
        print(f"Error testing homepage: {e}")
        return {
            "success": False,
            "error": str(e),
            "screenshot": error_screenshot
        }

def test_settings_page(driver, base_url="http://localhost:8096"):
    """Test settings page functionality"""
    print("\n=== Testing Settings Page ===")
    
    try:
        # Navigate directly to settings
        settings_url = f"{base_url}/settings"
        driver.get(settings_url)
        time.sleep(5)  # Wait for page to load
        
        settings_screenshot = take_screenshot(driver, "settings_page", "Settings page loaded")
        
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Check page content
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        page_source = driver.page_source.lower()
        
        # Look for settings-related content
        settings_indicators = {
            "api_key": any(term in page_source for term in ["api", "key", "google"]),
            "settings": "settings" in page_source,
            "configuration": "configuration" in page_source,
            "tabs": any(term in page_source for term in ["tab", "usage", "model", "quota"])
        }
        
        print(f"Settings indicators: {settings_indicators}")
        
        # Look for input fields
        inputs = driver.find_elements(By.TAG_NAME, "input")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        selects = driver.find_elements(By.TAG_NAME, "select")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        
        print(f"Form elements: {len(inputs)} inputs, {len(textareas)} textareas, {len(selects)} selects, {len(buttons)} buttons")
        
        # Look for tab elements specifically
        tab_elements = driver.find_elements(By.CSS_SELECTOR, "[role='tab'], .tab, [data-tab], [aria-selected]")
        print(f"Found {len(tab_elements)} potential tab elements")
        
        return {
            "success": any(settings_indicators.values()),
            "url": current_url,
            "indicators": settings_indicators,
            "form_elements": len(inputs) + len(textareas) + len(selects),
            "buttons": len(buttons),
            "tabs": len(tab_elements),
            "screenshot": settings_screenshot
        }
        
    except Exception as e:
        error_screenshot = take_screenshot(driver, "settings_error", "Settings page error")
        print(f"Error testing settings: {e}")
        return {
            "success": False,
            "error": str(e),
            "screenshot": error_screenshot
        }

def test_new_campaign_page(driver, base_url="http://localhost:8096"):
    """Test new campaign page"""
    print("\n=== Testing New Campaign Page ===")
    
    try:
        campaign_url = f"{base_url}/new-campaign"
        driver.get(campaign_url)
        time.sleep(5)
        
        campaign_screenshot = take_screenshot(driver, "new_campaign", "New campaign page loaded")
        
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        # Look for campaign-related content
        campaign_indicators = {
            "form": "form" in page_source,
            "business": "business" in page_source,
            "campaign": "campaign" in page_source,
            "create": "create" in page_source
        }
        
        # Count form elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        selects = driver.find_elements(By.TAG_NAME, "select")
        
        print(f"Campaign indicators: {campaign_indicators}")
        print(f"Form elements: {len(inputs)} inputs, {len(textareas)} textareas, {len(selects)} selects")
        
        return {
            "success": any(campaign_indicators.values()),
            "url": current_url,
            "indicators": campaign_indicators,
            "form_elements": len(inputs) + len(textareas) + len(selects),
            "screenshot": campaign_screenshot
        }
        
    except Exception as e:
        error_screenshot = take_screenshot(driver, "campaign_error", "Campaign page error")
        print(f"Error testing campaign page: {e}")
        return {
            "success": False,
            "error": str(e),
            "screenshot": error_screenshot
        }

def test_ideation_page(driver, base_url="http://localhost:8096"):
    """Test ideation page"""
    print("\n=== Testing Ideation Page ===")
    
    try:
        ideation_url = f"{base_url}/ideation"
        driver.get(ideation_url)
        time.sleep(5)
        
        ideation_screenshot = take_screenshot(driver, "ideation", "Ideation page loaded")
        
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        # Look for ideation-related content
        ideation_indicators = {
            "ideation": "ideation" in page_source,
            "content": "content" in page_source,
            "generate": "generate" in page_source,
            "ideas": "ideas" in page_source
        }
        
        buttons = driver.find_elements(By.TAG_NAME, "button")
        images = driver.find_elements(By.TAG_NAME, "img")
        
        print(f"Ideation indicators: {ideation_indicators}")
        print(f"Interactive elements: {len(buttons)} buttons, {len(images)} images")
        
        return {
            "success": any(ideation_indicators.values()),
            "url": current_url,
            "indicators": ideation_indicators,
            "buttons": len(buttons),
            "images": len(images),
            "screenshot": ideation_screenshot
        }
        
    except Exception as e:
        error_screenshot = take_screenshot(driver, "ideation_error", "Ideation page error")
        print(f"Error testing ideation page: {e}")
        return {
            "success": False,
            "error": str(e),
            "screenshot": error_screenshot
        }

def run_comprehensive_test(base_url="http://localhost:8096"):
    """Run comprehensive integration test"""
    print("Starting Selenium MCP Comprehensive Integration Test")
    print("="*60)
    
    driver = setup_driver()
    results = {}
    
    try:
        # Run all tests
        results["homepage"] = test_homepage_and_navigation(driver, base_url)
        results["settings"] = test_settings_page(driver, base_url)
        results["campaign"] = test_new_campaign_page(driver, base_url)
        results["ideation"] = test_ideation_page(driver, base_url)
        
        # Generate report
        print("\n" + "="*60)
        print("SELENIUM MCP TEST RESULTS")
        print("="*60)
        
        total_tests = len(results)
        successful_tests = sum(1 for result in results.values() if result.get("success", False))
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Success Rate: {successful_tests/total_tests:.1%}")
        
        print("\nDetailed Results:")
        print("-" * 40)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"{status} {test_name.title()}")
            
            if "error" in result:
                print(f"   Error: {result['error']}")
            
            if "screenshot" in result:
                print(f"   Screenshot: {result['screenshot']}")
            
            # Print key metrics
            for key, value in result.items():
                if key not in ["success", "error", "screenshot"] and isinstance(value, (int, str, dict)):
                    if isinstance(value, dict):
                        print(f"   {key}: {value}")
                    else:
                        print(f"   {key}: {value}")
            print()
        
        # Save detailed report
        report_file = f"selenium_mcp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Detailed report saved to: {report_file}")
        
        # Final assessment
        if successful_tests >= total_tests * 0.75:
            print("\n🎉 INTEGRATION TEST: SUCCESSFUL")
            print("Most functionality is working correctly.")
        elif successful_tests >= total_tests * 0.5:
            print("\n⚠️  INTEGRATION TEST: PARTIAL SUCCESS")
            print("Some functionality is working but issues detected.")
        else:
            print("\n❌ INTEGRATION TEST: FAILED")
            print("Major issues detected that need attention.")
        
        return successful_tests >= total_tests * 0.5
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)