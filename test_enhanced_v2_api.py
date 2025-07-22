#!/usr/bin/env python3
"""
Comprehensive test suite for Enhanced V2 API endpoints
Testing ADK v1.6+ features: A2A messaging, persistent memory, structured context
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestResult:
    endpoint: str
    method: str
    status_code: int
    response_data: Any
    success: bool
    error_message: Optional[str] = None
    duration_ms: float = 0

class EnhancedV2APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results: List[TestResult] = []
        self.campaign_id: Optional[str] = None
    
    def test_enhanced_health_check(self) -> TestResult:
        """Test Enhanced Health Check - Should return ADK v1.6+ features"""
        endpoint = f"{self.base_url}/api/v2/campaigns/health"
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            duration = (time.time() - start_time) * 1000
            
            result = TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=response.status_code,
                response_data=response.json() if response.status_code == 200 else response.text,
                success=response.status_code == 200,
                duration_ms=duration
            )
            
            # Validate ADK v1.6+ features in response
            if response.status_code == 200:
                data = response.json()
                expected_features = [
                    "a2a_messaging", "persistent_memory", 
                    "structured_context", "event_driven_coordination"
                ]
                
                # Check if response contains ADK v1.6+ feature indicators
                features_found = []
                response_str = json.dumps(data).lower()
                for feature in expected_features:
                    if feature.replace("_", " ") in response_str or feature in response_str:
                        features_found.append(feature)
                
                if features_found:
                    result.response_data["validated_features"] = features_found
                
            return result
            
        except Exception as e:
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def test_memory_statistics(self) -> TestResult:
        """Test Memory Statistics - Should return ADK v1.6+ memory metrics"""
        endpoint = f"{self.base_url}/api/v2/campaigns/debug/memory-stats"
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=response.status_code,
                response_data=response.json() if response.status_code == 200 else response.text,
                success=response.status_code == 200,
                duration_ms=duration
            )
            
        except Exception as e:
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def test_enhanced_campaign_creation(self) -> TestResult:
        """Test Enhanced Campaign Creation with A2A background processing"""
        endpoint = f"{self.base_url}/api/v2/campaigns/create"
        start_time = time.time()
        
        payload = {
            "campaign_name": "Enhanced V2 Test Campaign",
            "campaign_description": "Testing enhanced ADK v1.6+ features",
            "business_url": "https://example.com",
            "target_platforms": ["linkedin", "twitter"]
        }
        
        try:
            response = self.session.post(
                endpoint, 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            duration = (time.time() - start_time) * 1000
            
            result = TestResult(
                endpoint=endpoint,
                method="POST",
                status_code=response.status_code,
                response_data=response.json() if response.status_code in [200, 201] else response.text,
                success=response.status_code in [200, 201],
                duration_ms=duration
            )
            
            # Extract campaign_id for subsequent tests
            if result.success and isinstance(result.response_data, dict):
                self.campaign_id = result.response_data.get("campaign_id")
                
            return result
            
        except Exception as e:
            return TestResult(
                endpoint=endpoint,
                method="POST",
                status_code=0,
                response_data=None,
                success=False,
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def test_enhanced_campaign_status(self) -> TestResult:
        """Test Enhanced Campaign Status with persistent context tracking"""
        if not self.campaign_id:
            return TestResult(
                endpoint="N/A",
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message="No campaign_id available from previous test"
            )
        
        endpoint = f"{self.base_url}/api/v2/campaigns/{self.campaign_id}/status"
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=response.status_code,
                response_data=response.json() if response.status_code == 200 else response.text,
                success=response.status_code == 200,
                duration_ms=duration
            )
            
        except Exception as e:
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def test_campaign_context_zero_fidelity(self) -> TestResult:
        """Test Campaign Context with zero fidelity loss"""
        if not self.campaign_id:
            return TestResult(
                endpoint="N/A",
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message="No campaign_id available from previous test"
            )
        
        endpoint = f"{self.base_url}/api/v2/campaigns/{self.campaign_id}/context"
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=response.status_code,
                response_data=response.json() if response.status_code == 200 else response.text,
                success=response.status_code == 200,
                duration_ms=duration
            )
            
        except Exception as e:
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def test_a2a_message_history(self) -> TestResult:
        """Test A2A Message History - Agent-to-Agent communication tracking"""
        if not self.campaign_id:
            return TestResult(
                endpoint="N/A",
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message="No campaign_id available from previous test"
            )
        
        endpoint = f"{self.base_url}/api/v2/campaigns/{self.campaign_id}/messages"
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=response.status_code,
                response_data=response.json() if response.status_code == 200 else response.text,
                success=response.status_code == 200,
                duration_ms=duration
            )
            
        except Exception as e:
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def test_enhanced_campaign_list(self) -> TestResult:
        """Test Enhanced Campaign List with memory statistics"""
        endpoint = f"{self.base_url}/api/v2/campaigns/list"
        start_time = time.time()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=response.status_code,
                response_data=response.json() if response.status_code == 200 else response.text,
                success=response.status_code == 200,
                duration_ms=duration
            )
            
        except Exception as e:
            return TestResult(
                endpoint=endpoint,
                method="GET",
                status_code=0,
                response_data=None,
                success=False,
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite and return comprehensive results"""
        print("🚀 Starting Enhanced V2 API Test Suite")
        print("=" * 60)
        
        # Test 1: Enhanced Health Check
        print("1️⃣ Testing Enhanced Health Check...")
        result1 = self.test_enhanced_health_check()
        self.results.append(result1)
        print(f"   Status: {'✅ PASS' if result1.success else '❌ FAIL'} ({result1.status_code}) - {result1.duration_ms:.0f}ms")
        
        # Test 2: Memory Statistics
        print("2️⃣ Testing Memory Statistics...")
        result2 = self.test_memory_statistics()
        self.results.append(result2)
        print(f"   Status: {'✅ PASS' if result2.success else '❌ FAIL'} ({result2.status_code}) - {result2.duration_ms:.0f}ms")
        
        # Test 3: Enhanced Campaign Creation
        print("3️⃣ Testing Enhanced Campaign Creation...")
        result3 = self.test_enhanced_campaign_creation()
        self.results.append(result3)
        print(f"   Status: {'✅ PASS' if result3.success else '❌ FAIL'} ({result3.status_code}) - {result3.duration_ms:.0f}ms")
        if result3.success and self.campaign_id:
            print(f"   Campaign ID: {self.campaign_id}")
        
        # Test 4: Enhanced Campaign Status
        print("4️⃣ Testing Enhanced Campaign Status...")
        result4 = self.test_enhanced_campaign_status()
        self.results.append(result4)
        print(f"   Status: {'✅ PASS' if result4.success else '❌ FAIL'} ({result4.status_code}) - {result4.duration_ms:.0f}ms")
        
        # Test 5: Campaign Context (Zero Fidelity Loss)
        print("5️⃣ Testing Campaign Context (Zero Fidelity Loss)...")
        result5 = self.test_campaign_context_zero_fidelity()
        self.results.append(result5)
        print(f"   Status: {'✅ PASS' if result5.success else '❌ FAIL'} ({result5.status_code}) - {result5.duration_ms:.0f}ms")
        
        # Test 6: A2A Message History
        print("6️⃣ Testing A2A Message History...")
        result6 = self.test_a2a_message_history()
        self.results.append(result6)
        print(f"   Status: {'✅ PASS' if result6.success else '❌ FAIL'} ({result6.status_code}) - {result6.duration_ms:.0f}ms")
        
        # Test 7: Enhanced Campaign List
        print("7️⃣ Testing Enhanced Campaign List...")
        result7 = self.test_enhanced_campaign_list()
        self.results.append(result7)
        print(f"   Status: {'✅ PASS' if result7.success else '❌ FAIL'} ({result7.status_code}) - {result7.duration_ms:.0f}ms")
        
        # Summary
        passed_tests = sum(1 for r in self.results if r.success)
        total_tests = len(self.results)
        
        print("\n" + "=" * 60)
        print(f"📊 TEST SUITE SUMMARY: {passed_tests}/{total_tests} PASSED")
        print("=" * 60)
        
        return {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            },
            "campaign_id": self.campaign_id,
            "detailed_results": [
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "status_code": r.status_code,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "error_message": r.error_message,
                    "response_preview": str(r.response_data)[:200] + "..." if len(str(r.response_data)) > 200 else str(r.response_data)
                }
                for r in self.results
            ]
        }

def main():
    """Main test execution"""
    tester = EnhancedV2APITester()
    results = tester.run_complete_test_suite()
    
    # Save detailed results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"/tmp/enhanced_v2_api_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📝 Detailed results saved to: {results_file}")
    
    # Print key findings
    print("\n🔍 KEY FINDINGS:")
    for i, result in enumerate(tester.results, 1):
        if result.success:
            print(f"   {i}. {result.endpoint.split('/')[-1]}: ✅ Working")
        else:
            print(f"   {i}. {result.endpoint.split('/')[-1]}: ❌ {result.error_message or f'HTTP {result.status_code}'}")
    
    return results

if __name__ == "__main__":
    main()