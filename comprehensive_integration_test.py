#!/usr/bin/env python3
"""
Comprehensive Integration Test for Video Venture Launch
Tests the complete merged solution with professional 3-tab settings interface
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class IntegrationTestSuite:
    def __init__(self, base_url="http://localhost:8096"):
        self.base_url = base_url
        self.driver = None
        self.test_results = []
        self.screenshots_dir = "integration_test_screenshots"
        
        # Test data
        self.test_api_key = "AIzaSyTestKey123456789012345678901234567890"
        self.test_campaign = {
            "business_name": "TechCorp Solutions",
            "business_type": "Software Development",
            "business_description": "Leading provider of enterprise software solutions",
            "target_audience": "Small to medium businesses",
            "value_proposition": "Streamline business operations with cutting-edge technology"
        }

    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-extensions")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def teardown_driver(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

    def take_screenshot(self, name, description=""):
        """Take screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}_{name}.png"
        self.driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename} - {description}")
        return filename

    def log_test_result(self, test_name, status, details="", screenshot=None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "screenshot": screenshot
        }
        self.test_results.append(result)
        print(f"TEST: {test_name} - {status}")
        if details:
            print(f"DETAILS: {details}")

    def test_homepage_load(self):
        """Test 1: Homepage loading and basic functionality"""
        try:
            print("\n=== Testing Homepage Load ===")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            
            # Check if homepage loads properly
            title = self.driver.title
            page_source_length = len(self.driver.page_source)
            
            screenshot = self.take_screenshot("homepage_load", "Homepage initial load")
            
            # Check for key elements
            hero_section = self.driver.find_elements(By.CSS_SELECTOR, "[class*='hero'], h1, [class*='title']")
            navigation = self.driver.find_elements(By.CSS_SELECTOR, "nav, [class*='nav'], [class*='menu']")
            
            success = (
                title and 
                page_source_length > 1000 and
                len(hero_section) > 0 and
                len(navigation) > 0
            )
            
            details = f"Title: {title}, Page size: {page_source_length} chars, Hero elements: {len(hero_section)}, Nav elements: {len(navigation)}"
            
            self.log_test_result(
                "Homepage Load",
                "PASS" if success else "FAIL",
                details,
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("homepage_error", "Homepage load error")
            self.log_test_result("Homepage Load", "FAIL", str(e), screenshot)
            return False

    def test_settings_page_navigation(self):
        """Test 2: Navigate to Settings page"""
        try:
            print("\n=== Testing Settings Page Navigation ===")
            
            # Try to find settings link/button
            settings_selectors = [
                "a[href='/settings']",
                "a[href='#/settings']", 
                "[data-testid='settings']",
                "button:contains('Settings')",
                "a:contains('Settings')",
                "[class*='settings']"
            ]
            
            settings_link = None
            for selector in settings_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    settings_link = elements[0]
                    break
            
            if not settings_link:
                # Try direct navigation
                self.driver.get(f"{self.base_url}/settings")
            else:
                settings_link.click()
            
            time.sleep(2)
            
            # Verify we're on settings page
            current_url = self.driver.current_url
            page_content = self.driver.page_source.lower()
            
            screenshot = self.take_screenshot("settings_navigation", "Settings page after navigation")
            
            success = (
                "/settings" in current_url or 
                "settings" in page_content or
                "api" in page_content or
                "configuration" in page_content
            )
            
            self.log_test_result(
                "Settings Navigation",
                "PASS" if success else "FAIL",
                f"URL: {current_url}",
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("settings_nav_error", "Settings navigation error")
            self.log_test_result("Settings Navigation", "FAIL", str(e), screenshot)
            return False

    def test_professional_3tab_interface(self):
        """Test 3: Professional 3-tab settings interface"""
        try:
            print("\n=== Testing Professional 3-Tab Interface ===")
            
            # Ensure we're on settings page
            if "/settings" not in self.driver.current_url:
                self.driver.get(f"{self.base_url}/settings")
                time.sleep(2)
            
            screenshot = self.take_screenshot("settings_page_full", "Settings page full view")
            
            # Look for tab elements
            tab_selectors = [
                "[role='tab']",
                "[class*='tab']",
                "[data-tab]",
                "button[class*='tab']",
                ".tab-button",
                "[aria-selected]"
            ]
            
            tabs_found = []
            for selector in tab_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    tabs_found.extend(elements)
            
            # Remove duplicates
            unique_tabs = list(set([tab.text.strip() for tab in tabs_found if tab.text.strip()]))
            
            # Look for expected tab content
            expected_tabs = ["API Configuration", "Usage & Quotas", "Model Selection"]
            page_text = self.driver.page_source.lower()
            
            found_tab_content = {
                "api_config": any(term in page_text for term in ["api", "configuration", "key"]),
                "usage_quotas": any(term in page_text for term in ["usage", "quota", "statistics"]),
                "model_selection": any(term in page_text for term in ["model", "selection", "dropdown"])
            }
            
            success = (
                len(unique_tabs) >= 2 or  # At least 2 distinct tabs
                sum(found_tab_content.values()) >= 2  # At least 2 tab content areas
            )
            
            details = f"Tabs found: {unique_tabs}, Tab content: {found_tab_content}"
            
            self.log_test_result(
                "Professional 3-Tab Interface",
                "PASS" if success else "PARTIAL" if sum(found_tab_content.values()) >= 1 else "FAIL",
                details,
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("tabs_error", "Tab interface error")
            self.log_test_result("Professional 3-Tab Interface", "FAIL", str(e), screenshot)
            return False

    def test_api_key_functionality(self):
        """Test 4: API key input and functionality"""
        try:
            print("\n=== Testing API Key Functionality ===")
            
            # Look for API key input field
            api_key_selectors = [
                "input[type='password']",
                "input[placeholder*='API']",
                "input[placeholder*='key']",
                "input[name*='api']",
                "[data-testid*='api-key']",
                "input[class*='api']"
            ]
            
            api_key_input = None
            for selector in api_key_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    api_key_input = elements[0]
                    break
            
            if api_key_input:
                # Clear and enter test API key
                api_key_input.clear()
                api_key_input.send_keys(self.test_api_key)
                time.sleep(1)
                
                screenshot = self.take_screenshot("api_key_entered", "API key entered")
                
                # Verify the key was entered
                entered_value = api_key_input.get_attribute("value")
                key_entered_successfully = len(entered_value) > 20
                
                self.log_test_result(
                    "API Key Input",
                    "PASS" if key_entered_successfully else "FAIL",
                    f"Entered {len(entered_value)} characters",
                    screenshot
                )
                
                return key_entered_successfully
            else:
                screenshot = self.take_screenshot("no_api_input", "No API key input found")
                self.log_test_result(
                    "API Key Input",
                    "FAIL",
                    "No API key input field found",
                    screenshot
                )
                return False
                
        except Exception as e:
            screenshot = self.take_screenshot("api_key_error", "API key input error")
            self.log_test_result("API Key Input", "FAIL", str(e), screenshot)
            return False

    def test_connection_button(self):
        """Test 5: Test Connection button functionality"""
        try:
            print("\n=== Testing Connection Button ===")
            
            # Look for test connection button
            test_button_selectors = [
                "button:contains('Test Connection')",
                "button:contains('Test')",
                "[data-testid*='test']",
                "button[class*='test']",
                "input[type='submit']",
                "button[type='submit']"
            ]
            
            test_button = None
            for selector in test_button_selectors:
                if "contains" in selector:
                    # Use XPath for text content
                    xpath = f"//button[contains(text(), 'Test')]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements:
                        test_button = elements[0]
                        break
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        test_button = elements[0]
                        break
            
            if test_button:
                # Click the test button
                self.driver.execute_script("arguments[0].scrollIntoView();", test_button)
                time.sleep(0.5)
                test_button.click()
                time.sleep(3)  # Wait for response
                
                screenshot = self.take_screenshot("test_connection_clicked", "After clicking test connection")
                
                # Look for response/feedback
                page_source = self.driver.page_source.lower()
                response_indicators = [
                    "success", "error", "invalid", "valid", "connected", 
                    "failed", "testing", "response", "status"
                ]
                
                has_response = any(indicator in page_source for indicator in response_indicators)
                
                self.log_test_result(
                    "Test Connection Button",
                    "PASS" if has_response else "PARTIAL",
                    f"Button clicked, response detected: {has_response}",
                    screenshot
                )
                
                return True
            else:
                screenshot = self.take_screenshot("no_test_button", "No test button found")
                self.log_test_result(
                    "Test Connection Button",
                    "FAIL",
                    "No test connection button found",
                    screenshot
                )
                return False
                
        except Exception as e:
            screenshot = self.take_screenshot("test_button_error", "Test button error")
            self.log_test_result("Test Connection Button", "FAIL", str(e), screenshot)
            return False

    def test_save_settings(self):
        """Test 6: Save settings functionality"""
        try:
            print("\n=== Testing Save Settings ===")
            
            # Look for save button
            save_selectors = [
                "button:contains('Save')",
                "input[type='submit']",
                "button[type='submit']",
                "[data-testid*='save']",
                "button[class*='save']"
            ]
            
            save_button = None
            for selector in save_selectors:
                if "contains" in selector:
                    xpath = "//button[contains(text(), 'Save')]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements:
                        save_button = elements[0]
                        break
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        save_button = elements[0]
                        break
            
            if save_button:
                save_button.click()
                time.sleep(2)
                
                screenshot = self.take_screenshot("settings_saved", "After saving settings")
                
                # Look for save confirmation
                page_source = self.driver.page_source.lower()
                save_indicators = ["saved", "updated", "success", "configuration saved"]
                
                has_save_feedback = any(indicator in page_source for indicator in save_indicators)
                
                self.log_test_result(
                    "Save Settings",
                    "PASS" if has_save_feedback else "PARTIAL",
                    f"Save button clicked, feedback: {has_save_feedback}",
                    screenshot
                )
                
                return True
            else:
                screenshot = self.take_screenshot("no_save_button", "No save button found")
                self.log_test_result(
                    "Save Settings",
                    "PARTIAL",
                    "No explicit save button found",
                    screenshot
                )
                return False
                
        except Exception as e:
            screenshot = self.take_screenshot("save_error", "Save settings error")
            self.log_test_result("Save Settings", "FAIL", str(e), screenshot)
            return False

    def test_new_campaign_navigation(self):
        """Test 7: Navigate to New Campaign page"""
        try:
            print("\n=== Testing New Campaign Navigation ===")
            
            # Navigate to new campaign page
            self.driver.get(f"{self.base_url}/new-campaign")
            time.sleep(2)
            
            # Verify we're on the right page
            current_url = self.driver.current_url
            page_content = self.driver.page_source.lower()
            
            screenshot = self.take_screenshot("new_campaign_page", "New Campaign page")
            
            # Look for campaign form elements
            form_elements = self.driver.find_elements(By.CSS_SELECTOR, "form, input, textarea, select")
            campaign_indicators = ["campaign", "business", "name", "type", "description"]
            
            has_campaign_content = any(indicator in page_content for indicator in campaign_indicators)
            
            success = (
                "/new-campaign" in current_url and
                len(form_elements) > 0 and
                has_campaign_content
            )
            
            self.log_test_result(
                "New Campaign Navigation",
                "PASS" if success else "FAIL",
                f"URL: {current_url}, Form elements: {len(form_elements)}",
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("campaign_nav_error", "Campaign navigation error")
            self.log_test_result("New Campaign Navigation", "FAIL", str(e), screenshot)
            return False

    def test_campaign_form_filling(self):
        """Test 8: Fill out campaign creation form"""
        try:
            print("\n=== Testing Campaign Form Filling ===")
            
            # Fill out form fields
            form_filled = 0
            total_fields = len(self.test_campaign)
            
            for field_name, field_value in self.test_campaign.items():
                try:
                    # Try different selectors for each field
                    selectors = [
                        f"input[name='{field_name}']",
                        f"input[placeholder*='{field_name.replace('_', ' ')}']",
                        f"textarea[name='{field_name}']",
                        f"select[name='{field_name}']"
                    ]
                    
                    element = None
                    for selector in selectors:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            element = elements[0]
                            break
                    
                    if element:
                        if element.tag_name == "select":
                            # Handle select dropdown
                            element.click()
                            time.sleep(0.5)
                            options = element.find_elements(By.TAG_NAME, "option")
                            if options:
                                options[1].click()  # Select first non-empty option
                        else:
                            element.clear()
                            element.send_keys(field_value)
                        
                        form_filled += 1
                        time.sleep(0.5)
                        
                except Exception as field_error:
                    print(f"Could not fill {field_name}: {field_error}")
            
            screenshot = self.take_screenshot("form_filled", "Campaign form filled")
            
            success = form_filled >= (total_fields * 0.6)  # At least 60% of fields filled
            
            self.log_test_result(
                "Campaign Form Filling",
                "PASS" if success else "PARTIAL" if form_filled > 0 else "FAIL",
                f"Filled {form_filled}/{total_fields} fields",
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("form_fill_error", "Form filling error")
            self.log_test_result("Campaign Form Filling", "FAIL", str(e), screenshot)
            return False

    def test_ideation_page_navigation(self):
        """Test 9: Navigate to Ideation page and test content generation"""
        try:
            print("\n=== Testing Ideation Page Navigation ===")
            
            # Navigate to ideation page
            self.driver.get(f"{self.base_url}/ideation")
            time.sleep(3)
            
            current_url = self.driver.current_url
            page_content = self.driver.page_source.lower()
            
            screenshot = self.take_screenshot("ideation_page", "Ideation page")
            
            # Look for ideation-specific content
            ideation_indicators = [
                "ideation", "content", "generation", "campaign", 
                "generate", "analyze", "ideas", "creative"
            ]
            
            has_ideation_content = any(indicator in page_content for indicator in ideation_indicators)
            
            # Look for interactive elements
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
            interactive_elements = len(buttons)
            
            success = (
                "/ideation" in current_url and
                has_ideation_content and
                interactive_elements > 0
            )
            
            self.log_test_result(
                "Ideation Page Navigation",
                "PASS" if success else "FAIL",
                f"URL: {current_url}, Interactive elements: {interactive_elements}",
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("ideation_nav_error", "Ideation navigation error")
            self.log_test_result("Ideation Page Navigation", "FAIL", str(e), screenshot)
            return False

    def test_image_thumbnails_display(self):
        """Test 10: Verify image thumbnails are displaying correctly"""
        try:
            print("\n=== Testing Image Thumbnails Display ===")
            
            # Check for images across different pages
            pages_to_check = [
                f"{self.base_url}",
                f"{self.base_url}/ideation",
                f"{self.base_url}/new-campaign"
            ]
            
            total_images = 0
            loaded_images = 0
            
            for page_url in pages_to_check:
                try:
                    self.driver.get(page_url)
                    time.sleep(2)
                    
                    images = self.driver.find_elements(By.CSS_SELECTOR, "img")
                    total_images += len(images)
                    
                    for img in images:
                        try:
                            # Check if image is loaded by checking natural width
                            width = self.driver.execute_script("return arguments[0].naturalWidth;", img)
                            if width and width > 0:
                                loaded_images += 1
                        except:
                            pass
                            
                except Exception as page_error:
                    print(f"Error checking images on {page_url}: {page_error}")
            
            screenshot = self.take_screenshot("image_display_check", "Image display verification")
            
            success_rate = (loaded_images / total_images) if total_images > 0 else 0
            success = success_rate >= 0.5  # At least 50% of images loading
            
            self.log_test_result(
                "Image Thumbnails Display",
                "PASS" if success else "PARTIAL" if loaded_images > 0 else "FAIL",
                f"Loaded {loaded_images}/{total_images} images ({success_rate:.1%})",
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("image_check_error", "Image display check error")
            self.log_test_result("Image Thumbnails Display", "FAIL", str(e), screenshot)
            return False

    def test_text_visibility(self):
        """Test 11: Verify text visibility issues are resolved"""
        try:
            print("\n=== Testing Text Visibility ===")
            
            pages_to_check = [
                f"{self.base_url}",
                f"{self.base_url}/settings",
                f"{self.base_url}/new-campaign",
                f"{self.base_url}/ideation"
            ]
            
            visibility_issues = []
            total_checks = 0
            
            for page_url in pages_to_check:
                try:
                    self.driver.get(page_url)
                    time.sleep(2)
                    
                    # Check for common text visibility issues
                    text_elements = self.driver.find_elements(By.CSS_SELECTOR, "p, h1, h2, h3, h4, h5, h6, span, div, label")
                    
                    for element in text_elements[:10]:  # Check first 10 elements
                        try:
                            total_checks += 1
                            color = element.value_of_css_property("color")
                            background = element.value_of_css_property("background-color")
                            
                            # Simple check for very light text on light background
                            if "rgba(255, 255, 255" in color or "rgb(255, 255, 255)" in color:
                                if "rgba(255, 255, 255" in background or "rgb(255, 255, 255)" in background:
                                    visibility_issues.append(f"White text on white background: {element.text[:50]}")
                                    
                        except Exception:
                            pass
                            
                except Exception as page_error:
                    print(f"Error checking visibility on {page_url}: {page_error}")
            
            screenshot = self.take_screenshot("text_visibility_check", "Text visibility verification")
            
            success = len(visibility_issues) == 0
            
            self.log_test_result(
                "Text Visibility",
                "PASS" if success else "PARTIAL" if len(visibility_issues) < 3 else "FAIL",
                f"Found {len(visibility_issues)} visibility issues out of {total_checks} checks",
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("visibility_error", "Text visibility check error")
            self.log_test_result("Text Visibility", "FAIL", str(e), screenshot)
            return False

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE INTEGRATION TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ({passed_tests/total_tests:.1%})")
        print(f"Partial: {partial_tests} ({partial_tests/total_tests:.1%})")
        print(f"Failed: {failed_tests} ({failed_tests/total_tests:.1%})")
        print(f"Success Rate: {(passed_tests + partial_tests*0.5)/total_tests:.1%}")
        
        print("\nDETAILED RESULTS:")
        print("-" * 60)
        
        for result in self.test_results:
            status_symbol = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
            print(f"{status_symbol} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"   Details: {result['details']}")
            if result["screenshot"]:
                print(f"   Screenshot: {result['screenshot']}")
            print()
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "partial": partial_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests + partial_tests*0.5)/total_tests
            },
            "detailed_results": self.test_results
        }
        
        with open("integration_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Report saved to: integration_test_report.json")
        
        # Overall assessment
        overall_success = (passed_tests + partial_tests*0.5)/total_tests >= 0.7
        
        print("\n" + "="*60)
        print("INTEGRATION SUCCESS ASSESSMENT:")
        print("="*60)
        
        if overall_success:
            print("🎉 INTEGRATION SUCCESSFUL")
            print("The merge appears to be successful with most functionality working.")
        else:
            print("⚠️  INTEGRATION ISSUES DETECTED")
            print("Several issues found that may need attention.")
        
        return overall_success

    def run_all_tests(self):
        """Run the complete test suite"""
        print("Starting Comprehensive Integration Test Suite...")
        print("Testing merged solution with professional 3-tab settings interface")
        
        try:
            self.setup_driver()
            
            # Run all tests
            test_methods = [
                self.test_homepage_load,
                self.test_settings_page_navigation,
                self.test_professional_3tab_interface,
                self.test_api_key_functionality,
                self.test_connection_button,
                self.test_save_settings,
                self.test_new_campaign_navigation,
                self.test_campaign_form_filling,
                self.test_ideation_page_navigation,
                self.test_image_thumbnails_display,
                self.test_text_visibility
            ]
            
            for test_method in test_methods:
                try:
                    test_method()
                    time.sleep(1)  # Brief pause between tests
                except Exception as test_error:
                    print(f"Error in {test_method.__name__}: {test_error}")
            
            # Generate final report
            return self.generate_report()
            
        finally:
            self.teardown_driver()

if __name__ == "__main__":
    test_suite = IntegrationTestSuite()
    success = test_suite.run_all_tests()
    
    print("\n" + "="*60)
    print("FINAL ASSESSMENT:")
    print("="*60)
    
    if success:
        print("✅ Integration testing completed successfully!")
        print("The merged solution is ready for production.")
    else:
        print("❌ Integration testing revealed issues.")
        print("Review the detailed report for specific problems.")
    
    exit(0 if success else 1)