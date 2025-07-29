#!/usr/bin/env python3
"""
FILENAME: run_visual_content_regression_tests.py
DESCRIPTION/PURPOSE: Comprehensive test runner for visual content regression prevention
Author: JP + 2025-07-23

This script runs all visual content regression tests to ensure that the system
never again shows mountain landscape images for business marketing campaigns.

Usage:
    python run_visual_content_regression_tests.py
    python run_visual_content_regression_tests.py --fast  # Skip slow integration tests
    python run_visual_content_regression_tests.py --frontend-only  # Frontend tests only
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

# Test files to run for comprehensive regression prevention
REGRESSION_TEST_FILES = [
    "tests/test_visual_content_context_fidelity.py",
    "tests/test_visual_content.py", 
    "tests/test_visual_content_integration.py",
    "tests/test-visual-content-context-regression.js"
]

# Critical tests that must always pass
CRITICAL_TESTS = [
    "tests/test_visual_content_context_fidelity.py::TestVisualContentContextFidelity::test_no_forbidden_demo_urls_in_production_response",
    "tests/test_visual_content.py::TestVisualContentRegressionPrevention::test_no_mountain_images_for_business_context",
    "tests/test_visual_content.py::TestVisualContentRegressionPrevention::test_forbidden_url_detection_comprehensive"
]

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}{'...' if len(result.stdout) > 500 else ''}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            print(f"Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def run_pytest_tests(test_files, args):
    """Run Python pytest tests."""
    print("\n" + "="*60)
    print("🐍 RUNNING PYTHON REGRESSION TESTS")
    print("="*60)
    
    success_count = 0
    total_count = 0
    
    for test_file in test_files:
        if test_file.endswith('.py'):
            total_count += 1
            
            # Check if test file exists
            if not Path(test_file).exists():
                print(f"⚠️ Test file not found: {test_file}")
                continue
            
            # Build pytest command
            pytest_cmd = ['python', '-m', 'pytest', test_file, '-v']
            
            if args.fast:
                pytest_cmd.extend(['-k', 'not integration'])
            
            success = run_command(pytest_cmd, f"Running {test_file}")
            if success:
                success_count += 1
    
    return success_count, total_count

def run_frontend_tests(test_files, args):
    """Run frontend JavaScript/Playwright tests."""
    print("\n" + "="*60)
    print("🌐 RUNNING FRONTEND REGRESSION TESTS") 
    print("="*60)
    
    success_count = 0
    total_count = 0
    
    for test_file in test_files:
        if test_file.endswith('.js'):
            total_count += 1
            
            # Check if test file exists
            if not Path(test_file).exists():
                print(f"⚠️ Test file not found: {test_file}")
                continue
            
            # Try different test runners
            runners = [
                ['npx', 'playwright', 'test', test_file],
                ['node', test_file]
            ]
            
            success = False
            for runner in runners:
                success = run_command(runner, f"Running {test_file} with {runner[0]}")
                if success:
                    break
            
            if success:
                success_count += 1
    
    return success_count, total_count

def run_critical_tests():
    """Run the most critical regression prevention tests."""
    print("\n" + "="*60)
    print("🚨 RUNNING CRITICAL REGRESSION TESTS")
    print("="*60)
    
    success_count = 0
    total_count = len(CRITICAL_TESTS)
    
    for critical_test in CRITICAL_TESTS:
        success = run_command(
            ['python', '-m', 'pytest', critical_test, '-v', '--tb=short'],
            f"Critical test: {critical_test.split('::')[-1]}"
        )
        if success:
            success_count += 1
    
    return success_count, total_count

def validate_environment():
    """Validate that test environment is properly set up."""
    print("\n🔧 VALIDATING TEST ENVIRONMENT...")
    
    validations = [
        {
            "check": lambda: Path("backend/agents/visual_content_agent.py").exists(),
            "description": "Visual content agent exists",
            "required": True
        },
        {
            "check": lambda: Path("src/pages/IdeationPage.tsx").exists(),
            "description": "Ideation page component exists", 
            "required": True
        },
        {
            "check": lambda: subprocess.run(['python', '-c', 'import pytest'], capture_output=True).returncode == 0,
            "description": "pytest is available",
            "required": True
        },
        {
            "check": lambda: subprocess.run(['which', 'node'], capture_output=True).returncode == 0,
            "description": "Node.js is available",
            "required": False
        }
    ]
    
    all_required_pass = True
    
    for validation in validations:
        try:
            if validation["check"]():
                print(f"✅ {validation['description']}")
            else:
                print(f"❌ {validation['description']}")
                if validation["required"]:
                    all_required_pass = False
        except Exception as e:
            print(f"⚠️ {validation['description']} - Error: {e}")
            if validation["required"]:
                all_required_pass = False
    
    return all_required_pass

def main():
    parser = argparse.ArgumentParser(description="Run visual content regression tests")
    parser.add_argument('--fast', action='store_true', help='Skip slow integration tests')
    parser.add_argument('--frontend-only', action='store_true', help='Run frontend tests only')
    parser.add_argument('--backend-only', action='store_true', help='Run backend tests only')
    parser.add_argument('--critical-only', action='store_true', help='Run only critical regression tests')
    
    args = parser.parse_args()
    
    print("🚀 VISUAL CONTENT REGRESSION TEST RUNNER")
    print("="*60)
    print("Purpose: Prevent the regression where mountain landscape images")
    print("         were shown for business marketing campaigns.")
    print("="*60)
    
    # Validate environment
    if not validate_environment():
        print("\n❌ Environment validation failed. Please fix issues before running tests.")
        sys.exit(1)
    
    total_success = 0
    total_tests = 0
    
    # Run critical tests first
    if args.critical_only:
        print("\n🎯 Running CRITICAL TESTS ONLY...")
        success, count = run_critical_tests()
        total_success += success
        total_tests += count
    else:
        # Run backend tests
        if not args.frontend_only:
            python_files = [f for f in REGRESSION_TEST_FILES if f.endswith('.py')]
            success, count = run_pytest_tests(python_files, args)
            total_success += success
            total_tests += count
        
        # Run frontend tests
        if not args.backend_only:
            js_files = [f for f in REGRESSION_TEST_FILES if f.endswith('.js')]
            success, count = run_frontend_tests(js_files, args)
            total_success += success
            total_tests += count
        
        # Always run critical tests
        print("\n🚨 Running critical regression tests...")
        success, count = run_critical_tests()
        # Don't double-count these in totals since they overlap with other tests
    
    # Final summary
    print("\n" + "="*60)
    print("📊 REGRESSION TEST SUMMARY")
    print("="*60)
    
    if total_tests > 0:
        success_rate = (total_success / total_tests) * 100
        print(f"Tests Passed: {total_success}/{total_tests} ({success_rate:.1f}%)")
        
        if total_success == total_tests:
            print("✅ ALL REGRESSION TESTS PASSED")
            print("   The system is protected against the mountain landscape regression.")
            sys.exit(0)
        else:
            print("❌ SOME REGRESSION TESTS FAILED")
            print("   CRITICAL: The system may show irrelevant content for business campaigns.")
            print("   Please fix failing tests before deploying.")
            sys.exit(1)
    else:
        print("⚠️ No tests were run. Check test file paths and environment setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()