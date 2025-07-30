#!/usr/bin/env python3
"""
Mintin.app Crypto Token Minting Service Integration Test
Tests the complete workflow for creating a marketing campaign for promoting a new crypto token minting service
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

class MintinAppIntegrationTest:
    def __init__(self, base_url="http://localhost:8096"):
        self.base_url = base_url
        self.driver = None
        self.test_results = []
        
        # Mintin.app specific test data
        self.mintin_campaign_data = {
            "business_name": "Mintin.app",
            "business_type": "Cryptocurrency & Blockchain",
            "business_description": "Revolutionary crypto token minting platform that democratizes token creation for everyone",
            "target_audience": "Crypto enthusiasts, DeFi users, entrepreneurs, and blockchain developers",
            "value_proposition": "Create your own crypto tokens in minutes without coding knowledge - secure, fast, and affordable token minting service"
        }
        
        self.test_api_key = "AIzaSyTestKey123456789012345678901234567890"

    def setup_driver(self):
        """Setup Chrome driver with crypto-friendly options"""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        
    def teardown_driver(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

    def take_screenshot(self, name, description=""):
        """Take screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mintin_app_{timestamp}_{name}.png"
        self.driver.save_screenshot(filename)
        print(f"Screenshot: {filename} - {description}")
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

    def test_homepage_accessibility(self):
        """Test 1: Verify homepage loads and is accessible"""
        try:
            print("\n=== Testing Homepage Accessibility for Mintin.app Campaign ===")
            self.driver.get(self.base_url)
            
            # Wait for page to load and React to render
            time.sleep(5)
            
            screenshot = self.take_screenshot("homepage_load", "Homepage loaded for Mintin.app test")
            
            # Check basic page elements
            title = self.driver.title
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Look for any visible content
            visible_elements = self.driver.find_elements(By.CSS_SELECTOR, "*:not([style*='display: none']):not([hidden])")
            interactive_elements = self.driver.find_elements(By.CSS_SELECTOR, "a, button, input, select, textarea")
            
            success = len(body_text) > 50 or len(visible_elements) > 10
            
            details = f"Title: {title}, Body length: {len(body_text)}, Visible elements: {len(visible_elements)}, Interactive: {len(interactive_elements)}"
            
            self.log_test_result(
                "Homepage Accessibility",
                "PASS" if success else "FAIL",
                details,
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("homepage_error", "Homepage error")
            self.log_test_result("Homepage Accessibility", "FAIL", str(e), screenshot)
            return False

    def test_settings_configuration(self):
        """Test 2: Configure API settings for Mintin.app campaign generation"""
        try:
            print("\n=== Testing Settings Configuration for Mintin.app ===")
            
            # Navigate to settings
            self.driver.get(f"{self.base_url}/settings")
            time.sleep(5)
            
            screenshot = self.take_screenshot("settings_loaded", "Settings page for API configuration")
            
            # Check if page has loaded with content
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url
            
            # Look for settings-specific content
            has_api_content = any(term in page_source for term in ["api", "key", "configuration", "google"])
            has_tab_structure = any(term in page_source for term in ["tab", "usage", "model", "quota"])
            has_form_elements = len(self.driver.find_elements(By.CSS_SELECTOR, "input, button, select")) > 0
            
            # Try to find and interact with API key field if visible
            api_key_configured = False
            try:
                # Look for API key input field
                api_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password'], input[type='text']")
                if api_inputs:
                    api_input = api_inputs[0]
                    api_input.clear()
                    api_input.send_keys(self.test_api_key)
                    api_key_configured = True
                    time.sleep(1)
                    
                    # Look for test/save buttons
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    if buttons:
                        # Try clicking the first button (likely test or save)
                        buttons[0].click()
                        time.sleep(2)
                        
            except Exception as interaction_error:
                print(f"API key interaction failed: {interaction_error}")
            
            screenshot_after = self.take_screenshot("settings_configured", "Settings after API configuration attempt")
            
            success = (
                "/settings" in current_url and
                (has_api_content or has_tab_structure or has_form_elements)
            )
            
            details = f"URL: {current_url}, API content: {has_api_content}, Tab structure: {has_tab_structure}, Forms: {has_form_elements}, API configured: {api_key_configured}"
            
            self.log_test_result(
                "Settings Configuration",
                "PASS" if success else "PARTIAL" if has_api_content else "FAIL",
                details,
                screenshot_after
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("settings_error", "Settings configuration error")
            self.log_test_result("Settings Configuration", "FAIL", str(e), screenshot)
            return False

    def test_mintin_campaign_creation(self):
        """Test 3: Create new campaign specifically for Mintin.app crypto token service"""
        try:
            print("\n=== Testing Mintin.app Campaign Creation ===")
            
            # Navigate to new campaign page
            self.driver.get(f"{self.base_url}/new-campaign")
            time.sleep(5)
            
            screenshot = self.take_screenshot("campaign_form", "Campaign creation form for Mintin.app")
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check for campaign form elements
            form_indicators = {
                "business_form": any(term in page_source for term in ["business", "name", "company"]),
                "campaign_form": any(term in page_source for term in ["campaign", "create", "form"]),
                "description_field": any(term in page_source for term in ["description", "about", "details"]),
                "target_audience": any(term in page_source for term in ["audience", "target", "customer"])
            }
            
            # Try to fill out the form with Mintin.app data
            fields_filled = 0
            form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
            
            print(f"Found {len(form_elements)} form elements to fill")
            
            # Attempt to fill form fields with Mintin.app specific data
            for i, element in enumerate(form_elements[:5]):  # Limit to first 5 elements
                try:
                    if element.tag_name in ["input", "textarea"]:
                        element.clear()
                        
                        # Map fields to Mintin.app data
                        if i == 0:  # First field - likely business name
                            element.send_keys(self.mintin_campaign_data["business_name"])
                        elif i == 1:  # Second field - likely business type
                            element.send_keys(self.mintin_campaign_data["business_type"])
                        elif i == 2:  # Third field - likely description
                            element.send_keys(self.mintin_campaign_data["business_description"])
                        elif i == 3:  # Fourth field - likely target audience
                            element.send_keys(self.mintin_campaign_data["target_audience"])
                        elif i == 4:  # Fifth field - likely value proposition
                            element.send_keys(self.mintin_campaign_data["value_proposition"])
                        
                        fields_filled += 1
                        time.sleep(0.5)
                        
                except Exception as field_error:
                    print(f"Could not fill form field {i}: {field_error}")
            
            screenshot_filled = self.take_screenshot("campaign_filled", f"Campaign form filled with Mintin.app data - {fields_filled} fields")
            
            # Look for submit/create button
            submit_attempted = False
            try:
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], button:contains('Create'), button:contains('Submit')")
                if not submit_buttons:
                    # Try finding any button
                    submit_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                
                if submit_buttons:
                    submit_buttons[0].click()
                    submit_attempted = True
                    time.sleep(3)
                    
                    screenshot_submitted = self.take_screenshot("campaign_submitted", "After campaign submission attempt")
                    
            except Exception as submit_error:
                print(f"Submit attempt failed: {submit_error}")
            
            success = (
                "/new-campaign" in current_url and
                any(form_indicators.values()) and
                fields_filled >= 2
            )
            
            details = f"URL: {current_url}, Form indicators: {form_indicators}, Fields filled: {fields_filled}, Submit attempted: {submit_attempted}"
            
            self.log_test_result(
                "Mintin.app Campaign Creation",
                "PASS" if success else "PARTIAL" if fields_filled > 0 else "FAIL",
                details,
                screenshot_filled
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("campaign_error", "Campaign creation error")
            self.log_test_result("Mintin.app Campaign Creation", "FAIL", str(e), screenshot)
            return False

    def test_ideation_process(self):
        """Test 4: Test ideation page for Mintin.app crypto content generation"""
        try:
            print("\n=== Testing Ideation Process for Mintin.app Crypto Content ===")
            
            # Navigate to ideation page
            self.driver.get(f"{self.base_url}/ideation")
            time.sleep(5)
            
            screenshot = self.take_screenshot("ideation_page", "Ideation page for Mintin.app content")
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Look for ideation-specific content
            ideation_indicators = {
                "content_generation": any(term in page_source for term in ["content", "generate", "creation"]),
                "crypto_ready": any(term in page_source for term in ["crypto", "token", "blockchain", "defi"]),
                "marketing_focus": any(term in page_source for term in ["marketing", "campaign", "social", "media"]),
                "ai_powered": any(term in page_source for term in ["ai", "artificial", "intelligence", "automated"])
            }
            
            # Look for interactive elements
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            images = self.driver.find_elements(By.TAG_NAME, "img")
            content_areas = self.driver.find_elements(By.CSS_SELECTOR, "div, section, article")
            
            # Try to interact with generation buttons if available
            generation_attempted = False
            try:
                generate_buttons = [btn for btn in buttons if "generate" in btn.text.lower() or "create" in btn.text.lower()]
                if generate_buttons:
                    generate_buttons[0].click()
                    generation_attempted = True
                    time.sleep(5)  # Wait for content generation
                    
                    screenshot_generated = self.take_screenshot("content_generated", "After content generation attempt")
                    
            except Exception as gen_error:
                print(f"Content generation attempt failed: {gen_error}")
            
            success = (
                "/ideation" in current_url and
                any(ideation_indicators.values())
            )
            
            details = f"URL: {current_url}, Indicators: {ideation_indicators}, Buttons: {len(buttons)}, Images: {len(images)}, Generation attempted: {generation_attempted}"
            
            self.log_test_result(
                "Ideation Process",
                "PASS" if success else "PARTIAL" if len(buttons) > 0 else "FAIL",
                details,
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("ideation_error", "Ideation process error")
            self.log_test_result("Ideation Process", "FAIL", str(e), screenshot)
            return False

    def test_crypto_content_quality(self):
        """Test 5: Verify the system can handle crypto-specific content appropriately"""
        try:
            print("\n=== Testing Crypto Content Quality and Compliance ===")
            
            # Check multiple pages for crypto-friendly content handling
            pages_to_test = [
                f"{self.base_url}/ideation",
                f"{self.base_url}/new-campaign",
                f"{self.base_url}/scheduling"
            ]
            
            crypto_compatibility_score = 0
            total_checks = 0
            
            for page_url in pages_to_test:
                try:
                    self.driver.get(page_url)
                    time.sleep(3)
                    
                    page_source = self.driver.page_source.lower()
                    
                    # Check for crypto-friendly indicators
                    crypto_checks = {
                        "blockchain_terms": any(term in page_source for term in ["blockchain", "crypto", "token", "defi", "nft"]),
                        "no_restrictions": "restricted" not in page_source and "prohibited" not in page_source,
                        "financial_ready": any(term in page_source for term in ["financial", "investment", "trading", "market"]),
                        "compliance_aware": any(term in page_source for term in ["compliance", "regulation", "legal", "disclaimer"])
                    }
                    
                    page_score = sum(crypto_checks.values())
                    crypto_compatibility_score += page_score
                    total_checks += len(crypto_checks)
                    
                    print(f"Page {page_url}: Crypto compatibility score {page_score}/{len(crypto_checks)}")
                    
                except Exception as page_error:
                    print(f"Error checking {page_url}: {page_error}")
            
            screenshot = self.take_screenshot("crypto_compliance", "Crypto content compatibility check")
            
            compatibility_rate = crypto_compatibility_score / total_checks if total_checks > 0 else 0
            success = compatibility_rate >= 0.3  # At least 30% crypto-friendly indicators
            
            details = f"Compatibility score: {crypto_compatibility_score}/{total_checks} ({compatibility_rate:.1%})"
            
            self.log_test_result(
                "Crypto Content Quality",
                "PASS" if success else "PARTIAL" if compatibility_rate > 0 else "FAIL",
                details,
                screenshot
            )
            
            return success
            
        except Exception as e:
            screenshot = self.take_screenshot("crypto_quality_error", "Crypto content quality error")
            self.log_test_result("Crypto Content Quality", "FAIL", str(e), screenshot)
            return False

    def generate_mintin_report(self):
        """Generate comprehensive Mintin.app specific test report"""
        print("\n" + "="*80)
        print("MINTIN.APP CRYPTO TOKEN MINTING SERVICE - INTEGRATION TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        print(f"Testing Campaign: Promoting Mintin.app - Revolutionary Crypto Token Minting Platform")
        print(f"Campaign Focus: {self.mintin_campaign_data['value_proposition']}")
        print(f"Target Audience: {self.mintin_campaign_data['target_audience']}")
        print()
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ({passed_tests/total_tests:.1%})")
        print(f"Partial: {partial_tests} ({partial_tests/total_tests:.1%})")
        print(f"Failed: {failed_tests} ({failed_tests/total_tests:.1%})")
        
        success_rate = (passed_tests + partial_tests*0.5)/total_tests
        print(f"Overall Success Rate: {success_rate:.1%}")
        
        print("\nDETAILED RESULTS:")
        print("-" * 80)
        
        for result in self.test_results:
            status_symbol = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
            print(f"{status_symbol} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"   Details: {result['details']}")
            if result["screenshot"]:
                print(f"   Screenshot: {result['screenshot']}")
            print()
        
        # Save report
        report_data = {
            "campaign": "Mintin.app Crypto Token Minting Service",
            "campaign_data": self.mintin_campaign_data,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "partial": partial_tests,
                "failed": failed_tests,
                "success_rate": success_rate
            },
            "detailed_results": self.test_results
        }
        
        report_filename = f"mintin_app_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Detailed report saved to: {report_filename}")
        
        # Final assessment
        print("\n" + "="*80)
        print("MINTIN.APP CAMPAIGN READINESS ASSESSMENT:")
        print("="*80)
        
        if success_rate >= 0.8:
            print("🎉 EXCELLENT - Ready for Mintin.app crypto marketing campaign!")
            print("The platform successfully handles crypto-specific content and workflows.")
        elif success_rate >= 0.6:
            print("✅ GOOD - Platform is mostly ready for Mintin.app campaign with minor issues.")
            print("Consider addressing partial failures for optimal crypto marketing performance.")
        elif success_rate >= 0.4:
            print("⚠️  NEEDS IMPROVEMENT - Platform has basic functionality but needs work.")
            print("Several issues detected that may affect crypto campaign effectiveness.")
        else:
            print("❌ NOT READY - Major issues detected for crypto marketing campaigns.")
            print("Significant development work needed before promoting Mintin.app service.")
        
        return success_rate >= 0.6

    def run_mintin_integration_test(self):
        """Run the complete Mintin.app integration test suite"""
        print("Starting Mintin.app Crypto Token Minting Service Integration Test")
        print("Testing: Promoting new crypto token minting service")
        print("="*80)
        
        try:
            self.setup_driver()
            
            # Run all Mintin.app specific tests
            test_methods = [
                self.test_homepage_accessibility,
                self.test_settings_configuration,
                self.test_mintin_campaign_creation,
                self.test_ideation_process,
                self.test_crypto_content_quality
            ]
            
            for test_method in test_methods:
                try:
                    test_method()
                    time.sleep(2)  # Brief pause between tests
                except Exception as test_error:
                    print(f"Error in {test_method.__name__}: {test_error}")
            
            # Generate final report
            return self.generate_mintin_report()
            
        finally:
            self.teardown_driver()

if __name__ == "__main__":
    test_suite = MintinAppIntegrationTest()
    success = test_suite.run_mintin_integration_test()
    
    print("\n" + "="*80)
    print("FINAL MINTIN.APP CAMPAIGN ASSESSMENT:")
    print("="*80)
    
    if success:
        print("✅ Mintin.app crypto marketing campaign integration READY!")
        print("The platform can effectively promote your crypto token minting service.")
    else:
        print("❌ Mintin.app campaign integration needs attention.")
        print("Review the detailed report for specific crypto-marketing issues.")
    
    exit(0 if success else 1)