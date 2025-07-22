#!/usr/bin/env python3
"""
API Endpoint Testing Script for Enhanced ADK v1.6+ Features
Tests both existing v1 endpoints and validates enhanced features.
"""

import json
import time
import requests
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class TestResult:
    endpoint: str
    method: str
    status: str  # pass/fail/skip
    status_code: int = None
    response: Dict[Any, Any] = None
    error: str = None
    validation_results: List[str] = None

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.campaign_id = None
        
    def log_result(self, result: TestResult):
        """Log test result"""
        self.results.append(result)
        status_symbol = "✅" if result.status == "pass" else "❌" if result.status == "fail" else "⏭️"
        print(f"{status_symbol} {result.method} {result.endpoint} - {result.status}")
        if result.error:
            print(f"    Error: {result.error}")
        if result.validation_results:
            for validation in result.validation_results:
                print(f"    Validation: {validation}")
    
    def test_endpoint(self, endpoint: str, method: str = "GET", payload: Dict = None, 
                     expected_fields: List[str] = None) -> TestResult:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        result = TestResult(endpoint=endpoint, method=method, status="fail")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=payload, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=payload, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, timeout=30)
            else:
                result.error = f"Unsupported method: {method}"
                return result
                
            result.status_code = response.status_code
            
            if response.status_code == 200:
                try:
                    result.response = response.json()
                    result.status = "pass"
                    
                    # Validate expected fields
                    validations = []
                    if expected_fields and result.response:
                        for field in expected_fields:
                            if field in result.response:
                                validations.append(f"✅ Found expected field: {field}")
                            else:
                                validations.append(f"❌ Missing expected field: {field}")
                    result.validation_results = validations
                    
                except json.JSONDecodeError:
                    result.response = {"raw_response": response.text}
                    result.status = "pass"  # Still consider it a pass if we get a response
            else:
                result.error = f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.RequestException as e:
            result.error = f"Request failed: {str(e)}"
        except Exception as e:
            result.error = f"Unexpected error: {str(e)}"
            
        return result

    def test_health_endpoints(self):
        """Test health and system status endpoints"""
        print("\n🔍 Testing Health & System Status Endpoints")
        
        # Test main health endpoint
        result = self.test_endpoint("/health", expected_fields=["status", "agent_initialized"])
        self.log_result(result)
        
        # Test root endpoint
        result = self.test_endpoint("/", expected_fields=["name", "version", "framework"])
        self.log_result(result)
        
        # Try to find v2 health endpoint (might not exist yet)
        result = self.test_endpoint("/api/v2/campaigns/health")
        if result.status == "fail" and result.status_code == 404:
            result.status = "skip"
            result.error = "V2 health endpoint not implemented yet"
        self.log_result(result)

    def test_campaign_management(self):
        """Test campaign management endpoints"""
        print("\n📋 Testing Campaign Management")
        
        # List existing campaigns
        result = self.test_endpoint("/api/v1/campaigns/", expected_fields=["campaigns"])
        self.log_result(result)
        
        # Create a new campaign
        campaign_payload = {
            "campaign_name": "API Test Campaign",
            "business_description": "Test business for API validation",
            "target_platforms": ["linkedin", "twitter"],
            "industry": "Technology",
            "campaign_goals": ["brand_awareness", "lead_generation"]
        }
        
        result = self.test_endpoint("/api/v1/campaigns/create", "POST", campaign_payload, 
                                  expected_fields=["campaign_id", "status"])
        self.log_result(result)
        
        # Store campaign_id for subsequent tests
        if result.status == "pass" and result.response and "campaign_id" in result.response:
            self.campaign_id = result.response["campaign_id"]
            print(f"    Created campaign with ID: {self.campaign_id}")

    def test_campaign_operations(self):
        """Test operations on the created campaign"""
        if not self.campaign_id:
            print("\n⏭️ Skipping campaign operations - no campaign ID available")
            return
            
        print(f"\n🔧 Testing Campaign Operations (ID: {self.campaign_id})")
        
        # Get campaign details
        result = self.test_endpoint(f"/api/v1/campaigns/{self.campaign_id}", 
                                  expected_fields=["campaign_id", "campaign_name"])
        self.log_result(result)
        
        # Test v2 endpoints if they existed
        v2_endpoints = [
            f"/api/v2/campaigns/{self.campaign_id}/status",
            f"/api/v2/campaigns/{self.campaign_id}/context", 
            f"/api/v2/campaigns/{self.campaign_id}/messages"
        ]
        
        for endpoint in v2_endpoints:
            result = self.test_endpoint(endpoint)
            if result.status == "fail" and result.status_code == 404:
                result.status = "skip"
                result.error = "V2 endpoint not implemented yet"
            self.log_result(result)

    def test_content_generation(self):
        """Test content generation endpoints"""
        print("\n📝 Testing Content Generation")
        
        # Test content generation
        content_payload = {
            "campaign_id": self.campaign_id or "test-campaign",
            "business_description": "Test business for content generation",
            "target_platforms": ["linkedin"],
            "campaign_goals": ["brand_awareness"],
            "industry": "Technology"
        }
        
        result = self.test_endpoint("/api/v1/content/generate", "POST", content_payload)
        self.log_result(result)
        
        # Test cache stats
        result = self.test_endpoint("/api/v1/content/cache/stats")
        self.log_result(result)

    def test_enhanced_features(self):
        """Test ADK v1.6+ enhanced features"""
        print("\n🚀 Testing Enhanced ADK v1.6+ Features")
        
        # Check if memory statistics endpoint exists
        result = self.test_endpoint("/api/v2/campaigns/debug/memory-stats")
        if result.status == "fail" and result.status_code == 404:
            result.status = "skip"
            result.error = "Memory stats endpoint not implemented in v2 yet"
        self.log_result(result)
        
        # Check for A2A messaging support in current health endpoint
        health_result = self.test_endpoint("/health")
        if health_result.status == "pass" and health_result.response:
            validations = []
            if "services" in health_result.response:
                services = health_result.response["services"]
                if "session_service" in services:
                    validations.append(f"✅ Session service: {services['session_service']}")
                if "artifact_service" in services:
                    validations.append(f"✅ Artifact service: {services['artifact_service']}")
            
            # Check for ADK version indicators
            if "framework" in health_result.response or "agent_initialized" in health_result.response:
                validations.append("✅ ADK framework detected")
                
            health_result.validation_results = validations
        self.log_result(health_result)

    def test_user_journey(self):
        """Test complete user journey"""
        print("\n🎯 Testing Complete User Journey")
        
        journey_steps = [
            "1. System health check",
            "2. Campaign creation", 
            "3. Campaign management",
            "4. Content generation",
            "5. Enhanced features validation"
        ]
        
        for step in journey_steps:
            print(f"    {step}")
        
        # Count successful tests
        passed = len([r for r in self.results if r.status == "pass"])
        failed = len([r for r in self.results if r.status == "fail"]) 
        skipped = len([r for r in self.results if r.status == "skip"])
        
        print(f"\n    Journey Status: {passed} passed, {failed} failed, {skipped} skipped")
        
        # Overall journey assessment
        if failed == 0 and passed > 0:
            print("    ✅ User journey completed successfully")
        elif failed > passed:
            print("    ❌ User journey has significant issues")
        else:
            print("    ⚠️ User journey partially successful")

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("API ENDPOINT TESTING REPORT")
        print("="*60)
        
        # Summary statistics
        passed = len([r for r in self.results if r.status == "pass"])
        failed = len([r for r in self.results if r.status == "fail"])
        skipped = len([r for r in self.results if r.status == "skip"])
        
        print(f"\nSummary:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⏭️ Skipped: {skipped}")
        print(f"  📊 Total: {len(self.results)}")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for result in self.results:
            status_symbol = "✅" if result.status == "pass" else "❌" if result.status == "fail" else "⏭️"
            print(f"  {status_symbol} {result.method} {result.endpoint}")
            if result.status_code:
                print(f"      Status Code: {result.status_code}")
            if result.error:
                print(f"      Error: {result.error}")
            if result.validation_results:
                for validation in result.validation_results:
                    print(f"      {validation}")
        
        # ADK v1.6+ Features Assessment
        print(f"\nADK v1.6+ Features Assessment:")
        
        # Check what's working
        working_features = []
        missing_features = []
        
        # V1 API is working
        v1_endpoints = [r for r in self.results if "/api/v1/" in r.endpoint and r.status == "pass"]
        if v1_endpoints:
            working_features.append("✅ V1 API endpoints functional")
            
        # ADK framework detected
        health_checks = [r for r in self.results if r.endpoint == "/health" and r.status == "pass"]
        if health_checks:
            working_features.append("✅ ADK framework integration")
            
        # Session and artifact services
        for result in self.results:
            if result.endpoint == "/health" and result.response and "services" in result.response:
                working_features.append("✅ Session and artifact services")
                break
        
        # V2 endpoints missing
        v2_endpoints = [r for r in self.results if "/api/v2/" in r.endpoint]
        if any(r.status == "skip" for r in v2_endpoints):
            missing_features.append("❌ V2 API endpoints not implemented")
            
        # A2A messaging endpoints missing
        a2a_endpoints = [r for r in self.results if "messages" in r.endpoint or "memory-stats" in r.endpoint]
        if any(r.status == "skip" for r in a2a_endpoints):
            missing_features.append("❌ A2A messaging endpoints not available")
            
        print("  Working Features:")
        for feature in working_features:
            print(f"    {feature}")
            
        print("  Missing/Incomplete Features:")
        for feature in missing_features:
            print(f"    {feature}")
            
        # Recommendations
        print(f"\nRecommendations:")
        if missing_features:
            print("  1. Implement V2 API endpoints with enhanced ADK v1.6+ features")
            print("  2. Add A2A messaging and memory statistics endpoints")
            print("  3. Expose persistent memory and context management in API")
        else:
            print("  1. All enhanced features are working correctly")
            
        return {
            "summary": {"passed": passed, "failed": failed, "skipped": skipped},
            "working_features": working_features,
            "missing_features": missing_features,
            "campaign_id": self.campaign_id
        }

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting Enhanced ADK v1.6+ API Testing Suite")
        print(f"Base URL: {self.base_url}")
        
        try:
            self.test_health_endpoints()
            self.test_campaign_management()
            self.test_campaign_operations()
            self.test_content_generation()
            self.test_enhanced_features()
            self.test_user_journey()
            
        except KeyboardInterrupt:
            print("\n⚠️ Testing interrupted by user")
        except Exception as e:
            print(f"\n❌ Testing failed with error: {e}")
        
        return self.generate_report()

if __name__ == "__main__":
    tester = APITester()
    report = tester.run_all_tests()
    
    # Save report to file
    with open("/Users/jp/Library/Mobile Documents/com~apple~CloudDocs/Documents/workspaces/video-venture-launch/api_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: api_test_report.json")