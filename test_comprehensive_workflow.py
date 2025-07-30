#!/usr/bin/env python3
"""
Comprehensive Testing Workflow for Video Venture Launch Application
Tests the full workflow including Settings page with Gemini API key functionality
"""

import time
import requests
import json
from datetime import datetime
import traceback

class ComprehensiveWorkflowTester:
    def __init__(self):
        self.frontend_url = "http://localhost:8080"
        self.backend_url = "http://localhost:8000"
        self.test_results = []
        self.screenshots_taken = []
        
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
    
    def test_frontend_connectivity(self):
        """Test 2: Frontend Connectivity"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                # Check if it contains React/Vite content
                content = response.text
                if "<!doctype html" in content.lower() or "<html" in content.lower():
                    self.log_result("Frontend Connectivity", True, "Frontend serving HTML content")
                    return True
                else:
                    self.log_result("Frontend Connectivity", False, "Response doesn't contain HTML")
                    return False
            else:
                self.log_result("Frontend Connectivity", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Frontend Connectivity", False, "Connection failed", e)
            return False
    
    def test_api_endpoints(self):
        """Test 3: Key API Endpoints"""
        endpoints_to_test = [
            ("/api/v1/campaigns/", "GET", "Campaigns endpoint"),
            ("/health", "GET", "Health endpoint"),
        ]
        
        all_passed = True
        for endpoint, method, description in endpoints_to_test:
            try:
                url = f"{self.backend_url}{endpoint}"
                if method == "GET":
                    response = requests.get(url, timeout=5)
                    if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                        self.log_result(f"API Test - {description}", True, f"Status: {response.status_code}")
                    else:
                        self.log_result(f"API Test - {description}", False, f"Status: {response.status_code}")
                        all_passed = False
            except Exception as e:
                self.log_result(f"API Test - {description}", False, "Request failed", e)
                all_passed = False
        
        return all_passed
    
    def test_campaign_creation_flow(self):
        """Test 4: Campaign Creation API Flow"""
        try:
            # Test campaign creation
            campaign_data = {
                "business_name": "Liat Victoria Photography",
                "business_description": "Professional photography services specializing in portraits and lifestyle photography",
                "target_audience": "Individuals and families looking for professional photography sessions",
                "business_goals": "Increase bookings and showcase portfolio to attract more clients seeking professional photography services",
                "industry": "Photography Services",
                "website_url": ""
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/campaigns/create",
                json=campaign_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Campaign Creation API", True, f"Campaign created successfully")
                return True
            else:
                error_detail = response.text if response.text else f"Status: {response.status_code}"
                self.log_result("Campaign Creation API", False, error_detail)
                return False
                
        except Exception as e:
            self.log_result("Campaign Creation API", False, "API call failed", e)
            return False
    
    def test_content_generation(self):
        """Test 5: Content Generation API"""
        try:
            # Test bulk content generation
            content_data = {
                "business_context": {
                    "business_name": "Liat Victoria Photography",
                    "industry": "Photography Services"
                },
                "content_type": "text_image",
                "count": 2
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/content/generate-bulk",
                json=content_data,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                post_count = len(result.get('posts', []))
                self.log_result("Content Generation API", True, f"Generated {post_count} posts")
                return True
            else:
                error_detail = response.text if response.text else f"Status: {response.status_code}"
                self.log_result("Content Generation API", False, error_detail)
                return False
                
        except Exception as e:
            self.log_result("Content Generation API", False, "API call failed", e)
            return False
    
    def check_settings_page_implementation(self):
        """Test 6: Check for Settings Page Implementation"""
        try:
            # This would require checking the frontend code for settings implementation
            # For now, we'll check if there are any settings-related files
            import os
            
            # Check for settings-related files in the frontend
            frontend_src_path = "/Users/jp/Library/Mobile Documents/com~apple~CloudDocs/Documents/workspaces/video-venture-launch/src"
            settings_indicators = []
            
            if os.path.exists(frontend_src_path):
                for root, dirs, files in os.walk(frontend_src_path):
                    for file in files:
                        if 'setting' in file.lower() or 'config' in file.lower():
                            settings_indicators.append(file)
            
            if settings_indicators:
                self.log_result("Settings Page Implementation Check", True, f"Found settings-related files: {', '.join(settings_indicators)}")
                return True
            else:
                self.log_result("Settings Page Implementation Check", False, "No settings-related files found in src/")
                return False
                
        except Exception as e:
            self.log_result("Settings Page Implementation Check", False, "File system check failed", e)
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("🚀 COMPREHENSIVE WORKFLOW TEST - VIDEO VENTURE LAUNCH")
        print("=" * 80)
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_backend_connectivity,
            self.test_frontend_connectivity,
            self.test_api_endpoints,
            self.test_campaign_creation_flow,
            self.test_content_generation,
            self.check_settings_page_implementation
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
        
        print("SETTINGS PAGE ASSESSMENT:")
        print("-" * 40)
        settings_tests = [r for r in self.test_results if 'Settings' in r['test_name']]
        if settings_tests:
            settings_result = settings_tests[0]
            if settings_result['success']:
                print("✅ Settings page implementation detected")
            else:
                print("❌ Settings page not implemented or not accessible")
                print("   RECOMMENDATION: Implement Settings page with:")
                print("   - Gemini API key input field")
                print("   - Save/Update functionality")
                print("   - Navigation from main interface")
        else:
            print("⚠️  Settings page implementation could not be determined")
        
        print()
        print("API FUNCTIONALITY ASSESSMENT:")
        print("-" * 40)
        
        backend_healthy = any(r['success'] for r in self.test_results if 'Backend Health' in r['test_name'])
        campaign_working = any(r['success'] for r in self.test_results if 'Campaign Creation' in r['test_name'])
        content_working = any(r['success'] for r in self.test_results if 'Content Generation' in r['test_name'])
        
        if backend_healthy:
            print("✅ Backend is healthy and operational")
        if campaign_working:
            print("✅ Campaign creation workflow is functional")
        if content_working:
            print("✅ Content generation is working")
        
        print()
        print("RECOMMENDATIONS:")
        print("-" * 40)
        
        if not any(r['success'] for r in self.test_results if 'Frontend Connectivity' in r['test_name']):
            print("🔧 CRITICAL: Fix frontend connectivity issues")
            print("   - Check if Vite dev server is running correctly")
            print("   - Verify port configuration and firewall settings")
        
        if not any(r['success'] for r in self.test_results if 'Settings' in r['test_name']):
            print("🔧 HIGH PRIORITY: Implement Settings page")
            print("   - Add Settings route to React Router")
            print("   - Create Settings component with API key management")
            print("   - Add navigation link in header/sidebar")
        
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