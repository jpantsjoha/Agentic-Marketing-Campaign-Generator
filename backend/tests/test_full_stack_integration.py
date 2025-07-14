#!/usr/bin/env python3
"""
FILENAME: test_full_stack_integration.py
DESCRIPTION/PURPOSE: Comprehensive full-stack integration testing script for AI Marketing Campaign Post Generator
Author: JP + 2025-06-16

This script validates the complete application stack:
- SQLite Database connectivity and schema
- Backend API endpoints and functionality
- Frontend-Backend integration
- End-to-end user workflows
- Visual content generation capabilities
"""

import requests
import json
import time
import sqlite3
import os
import sys
from typing import Dict, Any, List
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:8080"
BACKEND_URL = "http://localhost:8000"
DATABASE_PATH = "database/data/database.db"
TEST_TIMEOUT = 30

class FullStackTester:
    """Comprehensive full-stack testing suite for AI Marketing Campaign Post Generator."""
    
    def __init__(self):
        self.test_results = {
            'database': [],
            'backend': [],
            'frontend': [],
            'integration': [],
            'e2e': []
        }
        self.start_time = time.time()
        
    def log_test(self, category: str, test_name: str, status: str, details: str = ""):
        """Log test result with timestamp."""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results[category].append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"  {status_emoji} {test_name}: {status}")
        if details and status != "PASS":
            print(f"     Details: {details}")
    
    def test_database_layer(self) -> bool:
        """Test SQLite database connectivity and schema."""
        print("\n🗄️  Testing Database Layer...")
        print("=" * 40)
        
        success_count = 0
        total_tests = 4
        
        # Test 1: Database file exists
        try:
            if os.path.exists(DATABASE_PATH):
                self.log_test('database', 'Database File Exists', 'PASS')
                success_count += 1
            else:
                self.log_test('database', 'Database File Exists', 'FAIL', f'Database not found at {DATABASE_PATH}')
        except Exception as e:
            self.log_test('database', 'Database File Exists', 'FAIL', str(e))
        
        # Test 2: Database connectivity
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if tables:
                self.log_test('database', 'Database Connectivity', 'PASS', f'Found {len(tables)} tables')
                success_count += 1
            else:
                self.log_test('database', 'Database Connectivity', 'FAIL', 'No tables found')
        except Exception as e:
            self.log_test('database', 'Database Connectivity', 'FAIL', str(e))
        
        # Test 3: Required tables exist
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            required_tables = ['users', 'campaigns', 'posts', 'media_files']
            existing_tables = []
            
            for table in required_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
                if cursor.fetchone():
                    existing_tables.append(table)
            
            conn.close()
            
            if len(existing_tables) == len(required_tables):
                self.log_test('database', 'Required Tables Exist', 'PASS', f'All {len(required_tables)} tables found')
                success_count += 1
            else:
                missing = set(required_tables) - set(existing_tables)
                self.log_test('database', 'Required Tables Exist', 'FAIL', f'Missing tables: {missing}')
        except Exception as e:
            self.log_test('database', 'Required Tables Exist', 'FAIL', str(e))
        
        # Test 4: Basic CRUD operations
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Test insert
            test_user_id = f"test_user_{int(time.time())}"
            cursor.execute("""
                INSERT OR REPLACE INTO users (id, email, created_at, updated_at) 
                VALUES (?, ?, datetime('now'), datetime('now'))
            """, (test_user_id, f"{test_user_id}@test.com"))
            
            # Test select
            cursor.execute("SELECT id, email FROM users WHERE id = ?", (test_user_id,))
            result = cursor.fetchone()
            
            # Test delete
            cursor.execute("DELETE FROM users WHERE id = ?", (test_user_id,))
            
            conn.commit()
            conn.close()
            
            if result and result[0] == test_user_id:
                self.log_test('database', 'Basic CRUD Operations', 'PASS')
                success_count += 1
            else:
                self.log_test('database', 'Basic CRUD Operations', 'FAIL', 'CRUD operations failed')
        except Exception as e:
            self.log_test('database', 'Basic CRUD Operations', 'FAIL', str(e))
        
        print(f"\n📊 Database Layer: {success_count}/{total_tests} tests passed")
        return success_count == total_tests
    
    def test_backend_layer(self) -> bool:
        """Test backend API endpoints."""
        print("\n🔌 Testing Backend API Layer...")
        print("=" * 40)
        
        success_count = 0
        total_tests = 6
        
        # Test 1: Backend server is running
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                self.log_test('backend', 'Backend Server Running', 'PASS')
                success_count += 1
            else:
                self.log_test('backend', 'Backend Server Running', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('backend', 'Backend Server Running', 'FAIL', str(e))
            return False  # Can't continue without backend
        
        # Test 2: Health endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log_test('backend', 'Health Endpoint', 'PASS')
                success_count += 1
            else:
                self.log_test('backend', 'Health Endpoint', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('backend', 'Health Endpoint', 'FAIL', str(e))
        
        # Test 3: URL Analysis API
        try:
            test_data = {
                "urls": ["https://example.com"],
                "analysis_depth": "standard"
            }
            response = requests.post(f"{BACKEND_URL}/api/v1/analysis/url", json=test_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "business_intelligence" in data and "url_insights" in data:
                    self.log_test('backend', 'URL Analysis API', 'PASS')
                    success_count += 1
                else:
                    self.log_test('backend', 'URL Analysis API', 'FAIL', 'Missing required response fields')
            else:
                self.log_test('backend', 'URL Analysis API', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('backend', 'URL Analysis API', 'FAIL', str(e))
        
        # Test 4: Campaign Creation API
        try:
            campaign_data = {
                "name": "Full Stack Test Campaign",
                "objective": "Test backend API functionality",
                "business_description": "Full-stack testing solution",
                "campaign_type": "product",
                "target_audience": "Developers and testers",
                "creativity_level": 7
            }
            response = requests.post(f"{BACKEND_URL}/api/v1/campaigns/create", json=campaign_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.campaign_id = data["data"]["id"]  # Store for later tests
                    self.log_test('backend', 'Campaign Creation API', 'PASS')
                    success_count += 1
                else:
                    self.log_test('backend', 'Campaign Creation API', 'FAIL', 'Invalid response structure')
            else:
                self.log_test('backend', 'Campaign Creation API', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('backend', 'Campaign Creation API', 'FAIL', str(e))
        
        # Test 5: Content Generation API
        try:
            if hasattr(self, 'campaign_id'):
                content_data = {
                    "campaign_id": self.campaign_id,
                    "platforms": ["twitter", "linkedin"],
                    "post_count": 2,
                    "creativity_level": 6,
                    "include_hashtags": True,
                    "business_context": {
                        "industry": "Technology",
                        "target_audience": "Developers",
                        "brand_voice": "Professional"
                    },
                    "campaign_objective": "Test content generation"
                }
                response = requests.post(f"{BACKEND_URL}/api/v1/content/generate", json=content_data, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data and "posts" in data["data"]:
                        self.log_test('backend', 'Content Generation API', 'PASS')
                        success_count += 1
                    else:
                        self.log_test('backend', 'Content Generation API', 'FAIL', 'Invalid response structure')
                else:
                    self.log_test('backend', 'Content Generation API', 'FAIL', f'Status: {response.status_code}')
            else:
                self.log_test('backend', 'Content Generation API', 'SKIP', 'No campaign ID available')
        except Exception as e:
            self.log_test('backend', 'Content Generation API', 'FAIL', str(e))
        
        # Test 6: Visual Content Generation API
        try:
            if hasattr(self, 'campaign_id'):
                visual_data = {
                    "campaign_id": self.campaign_id,
                    "content_type": "social_media_post",
                    "platforms": ["instagram", "twitter"],
                    "image_count": 2,
                    "video_count": 1,
                    "business_context": {
                        "industry": "Technology",
                        "brand_voice": "Professional",
                        "target_audience": "Tech professionals"
                    }
                }
                response = requests.post(f"{BACKEND_URL}/api/v1/content/generate-visuals", json=visual_data, timeout=25)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        self.log_test('backend', 'Visual Content Generation API', 'PASS')
                        success_count += 1
                    else:
                        self.log_test('backend', 'Visual Content Generation API', 'FAIL', 'Invalid response structure')
                else:
                    self.log_test('backend', 'Visual Content Generation API', 'FAIL', f'Status: {response.status_code}')
            else:
                self.log_test('backend', 'Visual Content Generation API', 'SKIP', 'No campaign ID available')
        except Exception as e:
            self.log_test('backend', 'Visual Content Generation API', 'FAIL', str(e))
        
        print(f"\n📊 Backend Layer: {success_count}/{total_tests} tests passed")
        return success_count >= 4  # Allow some flexibility for optional endpoints
    
    def test_frontend_layer(self) -> bool:
        """Test frontend accessibility and basic functionality."""
        print("\n🎨 Testing Frontend Layer...")
        print("=" * 40)
        
        success_count = 0
        total_tests = 4
        
        # Test 1: Frontend server is running
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200 and "<!DOCTYPE html" in response.text:
                self.log_test('frontend', 'Frontend Server Running', 'PASS')
                success_count += 1
            else:
                self.log_test('frontend', 'Frontend Server Running', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('frontend', 'Frontend Server Running', 'FAIL', str(e))
            return False  # Can't continue without frontend
        
        # Test 2: Main pages are accessible
        pages = [
            ('/', 'Dashboard'),
            ('/new-campaign', 'New Campaign'),
            ('/ideation', 'Ideation'),
            ('/proposals', 'Proposals')
        ]
        
        accessible_pages = 0
        for path, name in pages:
            try:
                response = requests.get(f"{FRONTEND_URL}{path}", timeout=5)
                if response.status_code == 200 and "<!DOCTYPE html" in response.text:
                    accessible_pages += 1
            except:
                pass
        
        if accessible_pages == len(pages):
            self.log_test('frontend', 'Main Pages Accessible', 'PASS', f'All {len(pages)} pages accessible')
            success_count += 1
        else:
            self.log_test('frontend', 'Main Pages Accessible', 'FAIL', f'Only {accessible_pages}/{len(pages)} pages accessible')
        
        # Test 3: Static assets loading
        try:
            # Check if Vite dev server is serving assets
            response = requests.get(f"{FRONTEND_URL}/@vite/client", timeout=5)
            if response.status_code == 200:
                self.log_test('frontend', 'Static Assets Loading', 'PASS')
                success_count += 1
            else:
                self.log_test('frontend', 'Static Assets Loading', 'FAIL', 'Vite client not accessible')
        except Exception as e:
            self.log_test('frontend', 'Static Assets Loading', 'FAIL', str(e))
        
        # Test 4: CORS configuration
        try:
            response = requests.options(
                f"{BACKEND_URL}/api/v1/analysis/url",
                headers={
                    "Origin": FRONTEND_URL,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=5
            )
            
            if "Access-Control-Allow-Origin" in response.headers:
                self.log_test('frontend', 'CORS Configuration', 'PASS')
                success_count += 1
            else:
                self.log_test('frontend', 'CORS Configuration', 'FAIL', 'CORS headers missing')
        except Exception as e:
            self.log_test('frontend', 'CORS Configuration', 'FAIL', str(e))
        
        print(f"\n📊 Frontend Layer: {success_count}/{total_tests} tests passed")
        return success_count >= 2  # Frontend and basic accessibility
    
    def test_integration_layer(self) -> bool:
        """Test frontend-backend integration."""
        print("\n🔗 Testing Integration Layer...")
        print("=" * 40)
        
        success_count = 0
        total_tests = 3
        
        # Test 1: API communication
        try:
            # Simulate frontend API call
            response = requests.post(
                f"{BACKEND_URL}/api/v1/analysis/url",
                json={"urls": ["https://example.com"], "analysis_depth": "standard"},
                headers={
                    "Content-Type": "application/json",
                    "Origin": FRONTEND_URL
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if "business_intelligence" in data:
                    self.log_test('integration', 'API Communication', 'PASS')
                    success_count += 1
                else:
                    self.log_test('integration', 'API Communication', 'FAIL', 'Invalid API response')
            else:
                self.log_test('integration', 'API Communication', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('integration', 'API Communication', 'FAIL', str(e))
        
        # Test 2: Error handling
        try:
            # Test invalid request
            response = requests.post(
                f"{BACKEND_URL}/api/v1/campaigns/create",
                json={"invalid": "data"},
                headers={"Origin": FRONTEND_URL},
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error expected
                self.log_test('integration', 'Error Handling', 'PASS')
                success_count += 1
            else:
                self.log_test('integration', 'Error Handling', 'FAIL', f'Expected 422, got {response.status_code}')
        except Exception as e:
            self.log_test('integration', 'Error Handling', 'FAIL', str(e))
        
        # Test 3: Response time performance
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 2.0:
                self.log_test('integration', 'Response Time Performance', 'PASS', f'{response_time:.2f}s')
                success_count += 1
            else:
                self.log_test('integration', 'Response Time Performance', 'FAIL', f'Slow response: {response_time:.2f}s')
        except Exception as e:
            self.log_test('integration', 'Response Time Performance', 'FAIL', str(e))
        
        print(f"\n📊 Integration Layer: {success_count}/{total_tests} tests passed")
        return success_count >= 2
    
    def test_e2e_flows(self) -> bool:
        """Test end-to-end user workflows."""
        print("\n🎯 Testing End-to-End Flows...")
        print("=" * 40)
        
        success_count = 0
        total_tests = 2
        
        # Test 1: Complete happy path workflow
        try:
            print("    🛤️  Testing Happy Path Workflow...")
            
            # Step 1: URL Analysis
            analysis_response = requests.post(
                f"{BACKEND_URL}/api/v1/analysis/url",
                json={"urls": ["https://example.com"], "analysis_depth": "standard"},
                timeout=15
            )
            
            if analysis_response.status_code != 200:
                raise Exception(f"URL analysis failed: {analysis_response.status_code}")
            
            # Step 2: Campaign Creation
            campaign_data = {
                "name": "E2E Test Campaign",
                "objective": "Test complete workflow",
                "business_description": "End-to-end testing solution",
                "campaign_type": "product",
                "target_audience": "QA Engineers",
                "creativity_level": 7
            }
            campaign_response = requests.post(
                f"{BACKEND_URL}/api/v1/campaigns/create",
                json=campaign_data,
                timeout=10
            )
            
            if campaign_response.status_code != 200:
                raise Exception(f"Campaign creation failed: {campaign_response.status_code}")
            
            campaign_id = campaign_response.json()["data"]["id"]
            
            # Step 3: Content Generation
            content_data = {
                "campaign_id": campaign_id,
                "platforms": ["twitter", "linkedin"],
                "post_count": 2,
                "creativity_level": 6,
                "include_hashtags": True,
                "business_context": {
                    "industry": "Technology",
                    "target_audience": "QA Engineers",
                    "brand_voice": "Professional"
                },
                "campaign_objective": "Test complete workflow"
            }
            content_response = requests.post(
                f"{BACKEND_URL}/api/v1/content/generate",
                json=content_data,
                timeout=20
            )
            
            if content_response.status_code != 200:
                raise Exception(f"Content generation failed: {content_response.status_code}")
            
            self.log_test('e2e', 'Happy Path Workflow', 'PASS', 'Complete workflow successful')
            success_count += 1
            
        except Exception as e:
            self.log_test('e2e', 'Happy Path Workflow', 'FAIL', str(e))
        
        # Test 2: Visual content generation workflow
        try:
            print("    🎨 Testing Visual Content Workflow...")
            
            if hasattr(self, 'campaign_id'):
                visual_data = {
                    "campaign_id": self.campaign_id,
                    "content_type": "social_media_post",
                    "platforms": ["instagram"],
                    "image_count": 1,
                    "video_count": 1,
                    "business_context": {
                        "industry": "Technology",
                        "brand_voice": "Creative",
                        "target_audience": "Tech enthusiasts"
                    }
                }
                
                visual_response = requests.post(
                    f"{BACKEND_URL}/api/v1/content/generate-visuals",
                    json=visual_data,
                    timeout=25
                )
                
                if visual_response.status_code == 200:
                    data = visual_response.json()
                    if data.get("success"):
                        self.log_test('e2e', 'Visual Content Workflow', 'PASS')
                        success_count += 1
                    else:
                        self.log_test('e2e', 'Visual Content Workflow', 'FAIL', 'Visual generation unsuccessful')
                else:
                    self.log_test('e2e', 'Visual Content Workflow', 'FAIL', f'Status: {visual_response.status_code}')
            else:
                self.log_test('e2e', 'Visual Content Workflow', 'SKIP', 'No campaign available')
                
        except Exception as e:
            self.log_test('e2e', 'Visual Content Workflow', 'FAIL', str(e))
        
        print(f"\n📊 End-to-End Flows: {success_count}/{total_tests} tests passed")
        return success_count >= 1
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_time = time.time() - self.start_time
        
        # Calculate statistics
        stats = {}
        total_tests = 0
        total_passed = 0
        
        for category, tests in self.test_results.items():
            passed = len([t for t in tests if t['status'] == 'PASS'])
            failed = len([t for t in tests if t['status'] == 'FAIL'])
            skipped = len([t for t in tests if t['status'] == 'SKIP'])
            
            stats[category] = {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total': len(tests),
                'success_rate': (passed / len(tests) * 100) if tests else 0
            }
            
            total_tests += len(tests)
            total_passed += passed
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'duration': f"{total_time:.2f}s",
            'overall_success_rate': f"{overall_success_rate:.1f}%",
            'total_tests': total_tests,
            'total_passed': total_passed,
            'statistics': stats,
            'detailed_results': self.test_results
        }
    
    def run_all_tests(self) -> bool:
        """Run complete full-stack test suite."""
        print("🧪 Starting Full-Stack Integration Testing")
        print("=" * 50)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test layers
        database_ok = self.test_database_layer()
        backend_ok = self.test_backend_layer()
        frontend_ok = self.test_frontend_layer()
        integration_ok = self.test_integration_layer()
        e2e_ok = self.test_e2e_flows()
        
        # Generate and display report
        report = self.generate_report()
        
        print("\n" + "=" * 50)
        print("📊 FULL-STACK TEST SUMMARY")
        print("=" * 50)
        print(f"⏱️  Total Duration: {report['duration']}")
        print(f"📈 Overall Success Rate: {report['overall_success_rate']}")
        print(f"🧪 Total Tests: {report['total_passed']}/{report['total_tests']} passed")
        print()
        
        for category, stats in report['statistics'].items():
            status_emoji = "✅" if stats['success_rate'] >= 80 else "⚠️" if stats['success_rate'] >= 50 else "❌"
            print(f"{status_emoji} {category.title()}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        
        print()
        
        # Overall assessment
        all_critical_passed = database_ok and backend_ok and frontend_ok
        if all_critical_passed and integration_ok and e2e_ok:
            print("🎉 FULL-STACK TESTING: ALL SYSTEMS OPERATIONAL")
            print("✅ Application is ready for production deployment")
        elif all_critical_passed:
            print("⚠️  FULL-STACK TESTING: CORE SYSTEMS OPERATIONAL")
            print("✅ Application core functionality is working")
            print("⚠️  Some advanced features need attention")
        else:
            print("❌ FULL-STACK TESTING: CRITICAL ISSUES DETECTED")
            print("🔧 Application requires fixes before deployment")
        
        return all_critical_passed

def main():
    """Main execution function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Full-Stack Integration Tester for AI Marketing Campaign Post Generator")
        print("Usage: python test_full_stack_integration.py")
        print()
        print("This script tests:")
        print("- SQLite database connectivity and schema")
        print("- Backend API endpoints and functionality")
        print("- Frontend accessibility and basic functionality")
        print("- Frontend-Backend integration")
        print("- End-to-end user workflows")
        return
    
    # Change to backend directory if needed
    if not os.path.exists(DATABASE_PATH) and os.path.exists('backend'):
        os.chdir('backend')
    
    tester = FullStackTester()
    success = tester.run_all_tests()
    
    # Save detailed report
    report = tester.generate_report()
    with open('full_stack_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: full_stack_test_report.json")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 