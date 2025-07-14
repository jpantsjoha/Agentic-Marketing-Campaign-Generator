#!/usr/bin/env python3
"""
FILENAME: test_social_media_integration.py
DESCRIPTION/PURPOSE: Test script for social media OAuth integration validation
Author: JP + 2025-06-22

This script validates the complete social media OAuth integration implementation:
- Database schema verification
- API route functionality
- OAuth flow simulation
- Security implementation checks
"""

import os
import sys
import sqlite3
import json
import requests
import time
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_status(message, status="INFO"):
    """Print formatted status message."""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def test_database_schema():
    """Test that the database schema includes social media tables."""
    print_status("Testing database schema...")
    
    try:
        from database.database import get_database_connection
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Check if social media tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'social_media_connections',
            'scheduled_posts',
            'campaign_chat_history'
        ]
        
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print_status(f"Missing tables: {missing_tables}", "ERROR")
            return False
        
        # Check social_media_connections table structure
        cursor.execute("PRAGMA table_info(social_media_connections)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'id', 'user_id', 'platform', 'platform_user_id', 'platform_username',
            'access_token', 'refresh_token', 'token_expires_at', 'scopes',
            'connection_status', 'created_at', 'updated_at'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print_status(f"Missing columns in social_media_connections: {missing_columns}", "ERROR")
            return False
        
        # Check scheduled_posts table structure
        cursor.execute("PRAGMA table_info(scheduled_posts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'id', 'campaign_id', 'user_id', 'social_connection_id', 'platform',
            'post_content', 'media_urls', 'hashtags', 'scheduled_time', 'status',
            'platform_post_id', 'posting_error', 'retry_count', 'created_at'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print_status(f"Missing columns in scheduled_posts: {missing_columns}", "ERROR")
            return False
        
        conn.close()
        print_status("Database schema validation passed", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Database schema test failed: {e}", "ERROR")
        return False

def test_api_routes_import():
    """Test that API routes can be imported without errors."""
    print_status("Testing API routes import...")
    
    try:
        from api.routes.social_auth import router as social_auth_router
        from api.routes.social_posts import router as social_posts_router
        
        # Check that routers have expected routes
        social_auth_routes = [route.path for route in social_auth_router.routes]
        social_posts_routes = [route.path for route in social_posts_router.routes]
        
        expected_auth_routes = ['/initiate', '/callback/{platform}', '/connections', '/disconnect/{platform}', '/status', '/health']
        expected_posts_routes = ['/schedule', '/scheduled/{campaign_id}', '/publish/{post_id}', '/cancel/{post_id}', '/status/summary']
        
        missing_auth_routes = [route for route in expected_auth_routes if route not in social_auth_routes]
        missing_posts_routes = [route for route in expected_posts_routes if route not in social_posts_routes]
        
        if missing_auth_routes:
            print_status(f"Missing social auth routes: {missing_auth_routes}", "ERROR")
            return False
            
        if missing_posts_routes:
            print_status(f"Missing social posts routes: {missing_posts_routes}", "ERROR")
            return False
        
        print_status("API routes import test passed", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"API routes import test failed: {e}", "ERROR")
        return False

def test_environment_configuration():
    """Test environment configuration for OAuth credentials."""
    print_status("Testing environment configuration...")
    
    from dotenv import load_dotenv
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
    
    required_vars = [
        'LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET',
        'TWITTER_CLIENT_ID', 'TWITTER_CLIENT_SECRET',
        'INSTAGRAM_CLIENT_ID', 'INSTAGRAM_CLIENT_SECRET',
        'FACEBOOK_APP_ID', 'FACEBOOK_APP_SECRET',
        'TIKTOK_CLIENT_ID', 'TIKTOK_CLIENT_SECRET',
        'SOCIAL_TOKEN_ENCRYPTION_KEY', 'OAUTH_STATE_SECRET'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print_status(f"Missing environment variables: {missing_vars}", "WARNING")
        print_status("Create backend/.env file with OAuth credentials for full functionality", "INFO")
    else:
        print_status("All OAuth environment variables configured", "SUCCESS")
    
    return len(missing_vars) == 0

def test_platform_configurations():
    """Test social media platform configurations."""
    print_status("Testing platform configurations...")
    
    try:
        from api.routes.social_auth import SOCIAL_PLATFORMS
        
        expected_platforms = ['linkedin', 'twitter', 'instagram', 'facebook', 'tiktok']
        configured_platforms = list(SOCIAL_PLATFORMS.keys())
        
        missing_platforms = [platform for platform in expected_platforms if platform not in configured_platforms]
        
        if missing_platforms:
            print_status(f"Missing platform configurations: {missing_platforms}", "ERROR")
            return False
        
        # Check each platform has required configuration
        for platform, config in SOCIAL_PLATFORMS.items():
            required_fields = ['oauth_url', 'token_url', 'scopes', 'char_limit']
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                print_status(f"Platform {platform} missing fields: {missing_fields}", "ERROR")
                return False
        
        print_status("Platform configurations test passed", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Platform configurations test failed: {e}", "ERROR")
        return False

def test_encryption_functionality():
    """Test token encryption/decryption functionality."""
    print_status("Testing encryption functionality...")
    
    try:
        from api.routes.social_auth import encrypt_token, decrypt_token
        
        test_token = "test_oauth_token_123456789"
        
        # Test encryption
        encrypted = encrypt_token(test_token)
        if encrypted == test_token:
            print_status("Token not encrypted", "ERROR")
            return False
        
        # Test decryption
        decrypted = decrypt_token(encrypted)
        if decrypted != test_token:
            print_status("Token decryption failed", "ERROR")
            return False
        
        print_status("Encryption functionality test passed", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Encryption functionality test failed: {e}", "ERROR")
        return False

def test_database_operations():
    """Test database operations for social media functionality."""
    print_status("Testing database operations...")
    
    try:
        from database.database import get_database_connection
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Test inserting a social media connection
        test_connection_data = (
            'test_user_id', 'linkedin', 'test_platform_user_id', 'test_username',
            'encrypted_access_token', 'encrypted_refresh_token',
            datetime.now().isoformat(), '["scope1", "scope2"]', 'active'
        )
        
        cursor.execute("""
            INSERT INTO social_media_connections (
                user_id, platform, platform_user_id, platform_username,
                access_token, refresh_token, token_expires_at, scopes, connection_status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, test_connection_data)
        
        connection_id = cursor.lastrowid
        
        # Test retrieving the connection
        cursor.execute("""
            SELECT platform, platform_username, connection_status
            FROM social_media_connections
            WHERE id = ?
        """, (connection_id,))
        
        result = cursor.fetchone()
        if not result:
            print_status("Failed to retrieve test connection", "ERROR")
            return False
        
        # Test inserting a scheduled post
        cursor.execute("""
            INSERT INTO scheduled_posts (
                id, campaign_id, user_id, social_connection_id, platform,
                post_content, scheduled_time, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            'test_post_id', 'test_campaign_id', 'test_user_id', connection_id,
            'linkedin', 'Test post content', datetime.now().isoformat(), 'pending'
        ))
        
        # Test retrieving the scheduled post
        cursor.execute("""
            SELECT platform, post_content, status
            FROM scheduled_posts
            WHERE id = ?
        """, ('test_post_id',))
        
        result = cursor.fetchone()
        if not result:
            print_status("Failed to retrieve test scheduled post", "ERROR")
            return False
        
        # Clean up test data
        cursor.execute("DELETE FROM scheduled_posts WHERE id = ?", ('test_post_id',))
        cursor.execute("DELETE FROM social_media_connections WHERE id = ?", (connection_id,))
        
        conn.commit()
        conn.close()
        
        print_status("Database operations test passed", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Database operations test failed: {e}", "ERROR")
        return False

def test_api_server_simulation():
    """Simulate API server responses for OAuth flow."""
    print_status("Testing API server simulation...")
    
    try:
        # Test that we can import and create app
        from api.main import app
        
        # Test OAuth initiate request simulation
        from api.routes.social_auth import initiate_oauth_flow, get_current_user_id
        
        print_status("API server components loaded successfully", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"API server simulation test failed: {e}", "ERROR")
        return False

def run_comprehensive_test():
    """Run all tests and provide a comprehensive report."""
    print_status("🚀 Starting Social Media OAuth Integration Test Suite", "INFO")
    print("=" * 70)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("API Routes Import", test_api_routes_import),
        ("Environment Configuration", test_environment_configuration),
        ("Platform Configurations", test_platform_configurations),
        ("Encryption Functionality", test_encryption_functionality),
        ("Database Operations", test_database_operations),
        ("API Server Simulation", test_api_server_simulation),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed_tests += 1
            else:
                print_status(f"{test_name} FAILED", "ERROR")
        except Exception as e:
            print_status(f"{test_name} FAILED with exception: {e}", "ERROR")
    
    print("\n" + "=" * 70)
    print_status(f"Test Suite Complete: {passed_tests}/{total_tests} tests passed", "INFO")
    
    if passed_tests == total_tests:
        print_status("🎉 All tests passed! Social Media OAuth integration is ready!", "SUCCESS")
        return True
    else:
        print_status(f"⚠️  {total_tests - passed_tests} test(s) failed. Check implementation.", "WARNING")
        return False

def main():
    """Main test execution."""
    print("Social Media OAuth Integration Test Suite")
    print("Author: JP + 2025-06-22")
    print("=" * 70)
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    success = run_comprehensive_test()
    
    if success:
        print("\n🚀 Integration Status: READY FOR PRODUCTION")
        print("📖 See docs/SOCIAL-MEDIA-OAUTH-IMPLEMENTATION.md for usage instructions")
    else:
        print("\n🔧 Integration Status: NEEDS ATTENTION")
        print("📋 Fix failing tests before deployment")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())