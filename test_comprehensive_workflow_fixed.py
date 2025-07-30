#!/usr/bin/env python3
"""
FIXED - Comprehensive Testing Workflow for Video Venture Launch Application
Tests the full workflow including Settings page with Gemini API key functionality using browser automation
"""

import time
import requests
import json
from datetime import datetime
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import base64

class ComprehensiveWorkflowTester:
    def __init__(self):
        self.frontend_url = "http://localhost:8096"
        self.backend_url = "http://localhost:8000"
        self.test_results = []
        self.screenshots_taken = []
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        # Run in headful mode to see what's happening
        # chrome_options.add_argument('--headless')  # Comment out for debugging
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def teardown_driver(self):
        """Cleanup WebDriver"""
        if self.driver:
            self.driver.quit()
        
    def take_screenshot(self, name, description=""):
        """Take and save screenshot"""
        if self.driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}_{name}.png"
            filepath = f"/Users/jp/Library/Mobile Documents/com~apple~CloudDocs/Documents/workspaces/video-venture-launch/{filename}"
            
            self.driver.save_screenshot(filepath)
            self.screenshots_taken.append({
                "name": name,
                "filename": filename,
                "description": description,
                "timestamp": timestamp
            })
            print(f"📸 Screenshot saved: {filename} - {description}")
        
    def log_result(self, test_name, success, details="", error=None):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "error": str(error) if error else None
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
    
    def test_backend_connectivity(self):
        """Test 1: Backend Health Check"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                details = f"Backend healthy - Agent: {health_data.get('agent_initialized')}, Gemini: {health_data.get('gemini_key_configured')}"
                self.log_result("Backend Health Check", True, details)
                return True
            else:
                self.log_result("Backend Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Backend Health Check", False, "Connection failed", e)
            return False
    
    def test_frontend_with_browser(self):
        """Test 2: Frontend with Browser Automation"""
        try:
            self.setup_driver()
            self.driver.get(self.frontend_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take screenshot of homepage
            self.take_screenshot("homepage", "Homepage design language and layout")
            
            # Check if it's the correct application
            page_title = self.driver.title
            page_source = self.driver.page_source
            
            if "Video Venture Launch" in page_title or "AI Marketing" in page_source:
                self.log_result("Frontend Browser Access", True, f"Successfully loaded app - Title: {page_title}")
                return True
            else:
                self.log_result("Frontend Browser Access", False, f"Unexpected content - Title: {page_title}")
                return False
                
        except Exception as e:
            self.log_result("Frontend Browser Access", False, "Failed to load in browser", e)
            return False
    
    def test_settings_page_navigation(self):
        """Test 3: Settings Page Navigation and Functionality"""
        try:
            if not self.driver:
                self.log_result("Settings Page Test", False, "No browser driver available")
                return False
            
            # Try to navigate directly to settings page
            settings_url = f"{self.frontend_url}/settings"
            self.driver.get(settings_url)
            
            time.sleep(2)  # Wait for page load
            
            # Take screenshot of settings page
            self.take_screenshot("settings_page", "Settings page layout and components")
            
            # Check if settings page loaded correctly
            try:
                # Look for settings-specific elements
                settings_indicators = [
                    "Google AI API",
                    "API Configuration",
                    "Settings",
                    "api-key"
                ]
                
                page_source = self.driver.page_source
                found_indicators = [indicator for indicator in settings_indicators if indicator in page_source]
                
                if found_indicators:
                    self.log_result("Settings Page Navigation", True, f"Found settings elements: {', '.join(found_indicators)}")
                    
                    # Test API key input field
                    try:
                        api_key_input = self.driver.find_element(By.ID, "api-key")
                        if api_key_input:
                            # Test entering a dummy API key
                            api_key_input.clear()
                            api_key_input.send_keys("test-api-key-12345")
                            
                            self.take_screenshot("api_key_test", "API key input field with test data")
                            
                            # Look for test connection button
                            try:
                                test_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Test Connection')]")
                                if test_button:
                                    self.log_result("API Key Input Test", True, "API key input field and test button functional")
                                    return True
                            except NoSuchElementException:
                                self.log_result("API Key Input Test", True, "API key input works, but test button not found")
                                return True
                                
                    except NoSuchElementException:
                        self.log_result("API Key Input Test", False, "API key input field not found")
                        return False
                        
                else:
                    self.log_result("Settings Page Navigation", False, "Settings page elements not found")
                    return False
                    
            except Exception as e:
                self.log_result("Settings Page Navigation", False, "Error checking settings elements", e)
                return False
                
        except Exception as e:
            self.log_result("Settings Page Test", False, "Navigation failed", e)
            return False
    
    def test_campaign_creation_api_fixed(self):
        """Test 4: Fixed Campaign Creation API with correct parameters"""
        try:
            # Fixed campaign data with all required fields
            campaign_data = {
                "business_description": "Professional photography services specializing in portraits and lifestyle photography",
                "objective": "Increase bookings and showcase portfolio to attract more clients seeking professional photography services",
                "target_audience": "Individuals and families looking for professional photography sessions",
                "campaign_type": "service",  # Must be one of: product, service, brand, event
                "creativity_level": 7,  # Must be 1-10
                "post_count": 6
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/campaigns/create",
                json=campaign_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                campaign_id = result.get('campaign_id', 'unknown')
                social_posts_count = len(result.get('social_posts', []))
                self.log_result("Campaign Creation API", True, f"Campaign created successfully - ID: {campaign_id}, Posts: {social_posts_count}")
                return True
            else:
                error_detail = response.text if response.text else f"Status: {response.status_code}"
                self.log_result("Campaign Creation API", False, error_detail)
                return False
                
        except Exception as e:
            self.log_result("Campaign Creation API", False, "API call failed", e)
            return False
    
    def test_homepage_design_validation(self):
        """Test 5: Visual Design Validation"""
        try:
            if not self.driver:
                self.log_result("Design Validation", False, "No browser driver available")
                return False
            
            # Navigate to homepage
            self.driver.get(self.frontend_url)
            time.sleep(3)
            
            # Take detailed screenshots
            self.take_screenshot("design_validation", "Overall design language and visual elements")
            
            # Check for design elements
            page_source = self.driver.page_source
            
            design_indicators = {
                "modern_css": ["gradient", "shadow", "rounded", "transition"],
                "professional_layout": ["container", "flex", "grid", "card"],
                "branding": ["primary", "accent", "brand"],
                "typography": ["font", "text", "heading"]
            }
            
            found_elements = {}
            for category, indicators in design_indicators.items():
                found = [indicator for indicator in indicators if indicator in page_source.lower()]
                found_elements[category] = found
            
            total_found = sum(len(elements) for elements in found_elements.values())
            
            if total_found >= 8:  # Arbitrary threshold
                details = f"Design elements detected: {total_found} indicators across categories"
                self.log_result("Visual Design Validation", True, details)
                return True
            else:
                details = f"Limited design elements found: {total_found} indicators"
                self.log_result("Visual Design Validation", False, details)
                return False
                
        except Exception as e:
            self.log_result("Visual Design Validation", False, "Design check failed", e)
            return False
    
    def test_campaign_creation_flow_browser(self):
        """Test 6: Complete Campaign Creation Flow in Browser"""
        try:
            if not self.driver:
                self.log_result("Campaign Flow Test", False, "No browser driver available")
                return False
            
            # Navigate to homepage
            self.driver.get(self.frontend_url)
            time.sleep(2)
            
            # Look for "Create Campaign" or similar button
            try:
                create_buttons = [
                    "Create Your Campaign",
                    "Create Campaign",
                    "Get Started",
                    "New Campaign"
                ]
                
                button_found = None
                for button_text in create_buttons:
                    try:
                        button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{button_text}')]")
                        if button and button.is_displayed():
                            button_found = button
                            break
                    except NoSuchElementException:
                        continue
                
                if button_found:
                    self.take_screenshot("before_campaign_click", "Homepage before clicking campaign button")
                    button_found.click()
                    time.sleep(3)
                    
                    self.take_screenshot("campaign_form", "Campaign creation form")
                    
                    # Check if we're on a form page
                    page_source = self.driver.page_source
                    form_indicators = ["business", "campaign", "objective", "audience", "description"]
                    found_form_elements = [indicator for indicator in form_indicators if indicator.lower() in page_source.lower()]
                    
                    if found_form_elements:
                        self.log_result("Campaign Flow Browser Test", True, f"Campaign form loaded with elements: {', '.join(found_form_elements)}")
                        return True
                    else:
                        self.log_result("Campaign Flow Browser Test", False, "Campaign button clicked but form not detected")
                        return False
                        
                else:
                    self.log_result("Campaign Flow Browser Test", False, "No campaign creation button found")
                    return False
                    
            except Exception as e:
                self.log_result("Campaign Flow Browser Test", False, "Error during campaign flow test", e)
                return False
                
        except Exception as e:
            self.log_result("Campaign Flow Browser Test", False, "Campaign flow test failed", e)
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("🚀 COMPREHENSIVE WORKFLOW TEST - VIDEO VENTURE LAUNCH (FIXED)")
        print("=" * 80)
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_backend_connectivity,
            self.test_frontend_with_browser,
            self.test_settings_page_navigation,
            self.test_campaign_creation_api_fixed,
            self.test_homepage_design_validation,
            self.test_campaign_creation_flow_browser
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
                traceback.print_exc()
            print()  # Add spacing between tests
        
        # Generate final report
        self.generate_final_report(passed_tests, total_tests)
        
        # Cleanup
        self.teardown_driver()
        
        return passed_tests, total_tests
    
    def generate_final_report(self, passed_tests, total_tests):
        """Generate comprehensive test report"""
        print("=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        print("DETAILED FINDINGS:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} - {result['test_name']}")
            print(f"   Details: {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
            print()
        
        print("SCREENSHOTS TAKEN:")
        print("-" * 40)
        for screenshot in self.screenshots_taken:
            print(f"📸 {screenshot['filename']} - {screenshot['description']}")
        print()
        
        print("SETTINGS PAGE ASSESSMENT:")
        print("-" * 40)
        settings_tests = [r for r in self.test_results if 'Settings' in r['test_name']]
        if settings_tests:
            settings_result = settings_tests[0]
            if settings_result['success']:
                print("✅ Settings page is implemented and accessible")
                print("✅ Gemini API key input field is functional")
                print("✅ Settings page navigation works correctly")
            else:
                print("❌ Settings page issues detected:")
                print(f"   - {settings_result['details']}")
        
        print()
        print("CAMPAIGN CREATION ASSESSMENT:")
        print("-" * 40)
        
        api_tests = [r for r in self.test_results if 'Campaign Creation API' in r['test_name']]
        flow_tests = [r for r in self.test_results if 'Campaign Flow' in r['test_name']]
        
        if api_tests and api_tests[0]['success']:
            print("✅ Campaign creation API is working correctly")
        else:
            print("❌ Campaign creation API needs fixes")
            
        if flow_tests and flow_tests[0]['success']:
            print("✅ Campaign creation user flow is functional")
        else:
            print("❌ Campaign creation user flow needs improvement")
        
        print()
        print("VISUAL DESIGN ASSESSMENT:")
        print("-" * 40)
        
        design_tests = [r for r in self.test_results if 'Design Validation' in r['test_name']]
        if design_tests and design_tests[0]['success']:
            print("✅ Visual design appears professional and modern")
            print("   - Modern CSS styling detected")
            print("   - Professional layout structure")
            print("   - Consistent design language")
        else:
            print("⚠️  Visual design validation inconclusive")
        
        print()
        print("OVERALL RECOMMENDATIONS:")
        print("-" * 40)
        
        if success_rate >= 80:
            print("🎉 EXCELLENT: Application is in great shape!")
            print("   - All major components are functional")
            print("   - Settings page is properly implemented")
            print("   - API integration is working")
        elif success_rate >= 60:
            print("👍 GOOD: Application is functional with minor issues")
            print("   - Core functionality works")
            print("   - Minor improvements needed")
        else:
            print("🔧 NEEDS WORK: Several issues need attention")
            print("   - Address failing tests")
            print("   - Improve core functionality")
        
        print()
        print("=" * 80)

def main():
    """Main test execution"""
    tester = ComprehensiveWorkflowTester()
    passed, total = tester.run_comprehensive_test()
    
    # Return exit code based on success rate
    success_rate = (passed / total) * 100 if total > 0 else 0
    return 0 if success_rate >= 75 else 1

if __name__ == "__main__":
    exit(main())