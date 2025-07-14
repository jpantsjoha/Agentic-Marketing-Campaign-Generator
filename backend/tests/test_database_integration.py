"""
FILENAME: test_database_integration.py
DESCRIPTION/PURPOSE: Comprehensive database integration tests for SQLite database operations
Author: JP + 2025-06-15

This module provides comprehensive testing for:
1. SQLite database operations and data integrity
2. API-database correlation and data structures
3. User journey testing with database persistence
4. Regression testing for database schema and operations
5. Data model validation and constraints
"""

import pytest
import sqlite3
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path

from database.models import (
    User, Campaign, GeneratedContent, UploadedFile, 
    CampaignTemplate, UserSession, CampaignType, 
    ContentType, Platform, FileCategory, CampaignStatus
)
from database.db_status import check_database_status


class TestDatabaseIntegration:
    """Comprehensive database integration test suite."""
    
    @pytest.fixture(scope="class")
    def test_db_path(self):
        """Create a temporary test database."""
        test_dir = tempfile.mkdtemp()
        db_path = os.path.join(test_dir, "test_video_venture_launch.db")
        
        # Initialize test database with schema
        self._initialize_test_database(db_path)
        
        yield db_path
        
        # Cleanup
        shutil.rmtree(test_dir)
    
    def _initialize_test_database(self, db_path: str):
        """Initialize test database with schema."""
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        
        with sqlite3.connect(db_path) as conn:
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
    
    @pytest.fixture
    def db_connection(self, test_db_path):
        """Provide database connection for tests."""
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        yield conn
        conn.close()
    
    def test_database_schema_integrity(self, db_connection):
        """Test database schema integrity and structure."""
        cursor = db_connection.cursor()
        
        # Test table existence
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'campaign_templates', 'campaigns', 'generated_content',
            'schema_version', 'uploaded_files', 'user_sessions', 'users',
            'social_media_connections', 'scheduled_posts', 'campaign_chat_history'
        ]
        
        assert set(tables) == set(expected_tables), f"Missing tables: {set(expected_tables) - set(tables)}"
        
        # Test views existence
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
            ORDER BY name
        """)
        views = [row[0] for row in cursor.fetchall()]
        
        expected_views = ['campaign_summary', 'content_performance', 'user_activity_summary']
        assert set(views) == set(expected_views), f"Missing views: {set(expected_views) - set(views)}"
        
        # Test indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        indexes = cursor.fetchall()
        assert len(indexes) >= 29, f"Expected at least 29 custom indexes, found {len(indexes)}"
    
    def test_user_crud_operations(self, db_connection):
        """Test User CRUD operations and data integrity."""
        cursor = db_connection.cursor()
        
        # Test CREATE
        user_data = {
            'id': 'test-user-123',
            'email': 'test@example.com',
            'username': 'testuser',
            'full_name': 'Test User',
            'profile_data': '{"preferences": {"theme": "dark"}}',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO users (id, email, username, full_name, profile_data, is_active, created_at, updated_at)
            VALUES (:id, :email, :username, :full_name, :profile_data, :is_active, :created_at, :updated_at)
        """, user_data)
        db_connection.commit()
        
        # Test READ
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_data['id'],))
        user_row = cursor.fetchone()
        assert user_row is not None
        assert user_row['email'] == user_data['email']
        assert user_row['username'] == user_data['username']
        
        # Test UPDATE
        new_full_name = 'Updated Test User'
        cursor.execute("""
            UPDATE users SET full_name = ?, updated_at = ? 
            WHERE id = ?
        """, (new_full_name, datetime.now().isoformat(), user_data['id']))
        db_connection.commit()
        
        cursor.execute("SELECT full_name FROM users WHERE id = ?", (user_data['id'],))
        updated_user = cursor.fetchone()
        assert updated_user['full_name'] == new_full_name
        
        # Test constraints
        with pytest.raises(sqlite3.IntegrityError):
            # Duplicate email should fail
            cursor.execute("""
                INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('test-user-456', user_data['email'], 'testuser2', 'Test User 2', True, 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            db_connection.commit()
    
    def test_campaign_lifecycle(self, db_connection):
        """Test complete campaign lifecycle with database operations."""
        cursor = db_connection.cursor()
        
        # First create a user
        user_id = 'campaign-test-user'
        cursor.execute("""
            INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, 'campaign@test.com', 'campaignuser', 'Campaign User', True,
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Create campaign
        campaign_data = {
            'id': 'test-campaign-123',
            'user_id': user_id,
            'name': 'Test Product Launch',
            'description': 'Testing campaign creation',
            'campaign_type': 'product',
            'status': 'draft',
            'business_context': '{"company": "Test Corp", "industry": "Technology"}',
            'target_audience': 'Tech professionals',
            'objectives': 'Increase brand awareness',
            'creativity_level': 7,
            'ai_analysis': '{"sentiment": "positive", "keywords": ["innovation", "tech"]}',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO campaigns (
                id, user_id, name, description, campaign_type, status,
                business_context, target_audience, objectives, creativity_level,
                ai_analysis, created_at, updated_at
            ) VALUES (
                :id, :user_id, :name, :description, :campaign_type, :status,
                :business_context, :target_audience, :objectives, :creativity_level,
                :ai_analysis, :created_at, :updated_at
            )
        """, campaign_data)
        db_connection.commit()
        
        # Test campaign status transitions
        status_transitions = ['active', 'completed', 'archived']
        for status in status_transitions:
            cursor.execute("""
                UPDATE campaigns SET status = ?, updated_at = ? WHERE id = ?
            """, (status, datetime.now().isoformat(), campaign_data['id']))
            db_connection.commit()
            
            cursor.execute("SELECT status FROM campaigns WHERE id = ?", (campaign_data['id'],))
            current_status = cursor.fetchone()['status']
            assert current_status == status
        
        # Test campaign with generated content
        content_data = {
            'id': 'test-content-123',
            'campaign_id': campaign_data['id'],
            'content_type': 'text_image',
            'platform': 'instagram',
            'content_data': '{"text": "Amazing product launch!", "hashtags": ["#innovation"]}',
            'ai_metadata': '{"model": "gemini-2.0-flash", "confidence": 0.95}',
            'user_rating': 4,  # Fixed: should be 1-5 range
            'is_selected': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO generated_content (
                id, campaign_id, content_type, platform, content_data,
                ai_metadata, user_rating, is_selected, created_at, updated_at
            ) VALUES (
                :id, :campaign_id, :content_type, :platform, :content_data,
                :ai_metadata, :user_rating, :is_selected, :created_at, :updated_at
            )
        """, content_data)
        db_connection.commit()
        
        # Test foreign key relationship
        cursor.execute("""
            SELECT c.name, gc.content_type, gc.platform 
            FROM campaigns c 
            JOIN generated_content gc ON c.id = gc.campaign_id 
            WHERE c.id = ?
        """, (campaign_data['id'],))
        
        result = cursor.fetchone()
        assert result is not None
        assert result['name'] == campaign_data['name']
        assert result['content_type'] == content_data['content_type']
    
    def test_data_model_validation(self, db_connection):
        """Test Pydantic data model validation against database schema."""
        cursor = db_connection.cursor()
        
        # Test User model validation
        user_dict = {
            'id': 'model-test-user',
            'email': 'model@test.com',
            'username': 'modeluser',
            'full_name': 'Model Test User',
            'profile_data': {'preferences': {'theme': 'light'}},
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Validate with Pydantic model
        user_model = User(**user_dict)
        assert user_model.email == user_dict['email']
        assert user_model.is_active == user_dict['is_active']
        
        # Test Campaign model validation
        campaign_dict = {
            'id': 'model-test-campaign',
            'user_id': user_dict['id'],
            'name': 'Model Test Campaign',
            'description': 'Testing model validation',
            'campaign_type': CampaignType.PRODUCT,
            'status': CampaignStatus.DRAFT,
            'business_context': {'company': 'Test Corp'},
            'target_audience': 'Developers',
            'objectives': 'Test objectives',
            'creativity_level': 5,
            'ai_analysis': {'confidence': 0.8},
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        campaign_model = Campaign(**campaign_dict)
        assert campaign_model.campaign_type == CampaignType.PRODUCT
        assert campaign_model.creativity_level == 5
        
        # Test enum validation
        with pytest.raises(ValueError):
            Campaign(**{**campaign_dict, 'campaign_type': 'invalid_type'})
        
        with pytest.raises(ValueError):
            Campaign(**{**campaign_dict, 'creativity_level': 15})  # Should be 1-10
    
    def test_database_views_and_analytics(self, db_connection):
        """Test database views and analytics functionality."""
        cursor = db_connection.cursor()
        
        # Create test data for views
        user_id = 'analytics-user'
        campaign_id = 'analytics-campaign'
        
        # Insert test user
        cursor.execute("""
            INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, 'analytics@test.com', 'analyticsuser', 'Analytics User', True,
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Insert test campaign
        cursor.execute("""
            INSERT INTO campaigns (
                id, user_id, name, description, campaign_type, status,
                business_context, target_audience, objectives, creativity_level,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (campaign_id, user_id, 'Analytics Campaign', 'Test campaign for analytics',
              'brand', 'active', '{}', 'Test audience', 'Test objectives', 6,
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Insert test content
        for i in range(3):
            cursor.execute("""
                INSERT INTO generated_content (
                    id, campaign_id, content_type, platform, content_data,
                    user_rating, is_selected, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f'analytics-content-{i}', campaign_id, 'text_image', 'instagram',
                  '{"text": "Test content"}', min(5, 3 + i), i == 0,  # Fixed: ensure 1-5 range
                  datetime.now().isoformat(), datetime.now().isoformat()))
        
        db_connection.commit()
        
        # Test campaign_summary view
        cursor.execute("SELECT * FROM campaign_summary WHERE id = ?", (campaign_id,))
        summary = cursor.fetchone()
        assert summary is not None
        assert summary['name'] == 'Analytics Campaign'  # Fixed: column is 'name', not 'campaign_name'
        assert summary['content_count'] == 3  # Fixed: column is 'content_count', not 'total_content'
        assert summary['selected_content_count'] == 1  # Fixed: column is 'selected_content_count', not 'selected_content'
        
        # Test content_performance view
        cursor.execute("SELECT * FROM content_performance WHERE campaign_id = ?", (campaign_id,))
        performance = cursor.fetchall()
        assert len(performance) == 3
        
        # Test user_activity_summary view
        cursor.execute("SELECT * FROM user_activity_summary WHERE id = ?", (user_id,))  # Fixed: column is 'id', not 'user_id'
        activity = cursor.fetchone()
        assert activity is not None
        assert activity['total_campaigns'] == 1
        assert activity['total_content_generated'] == 3  # Fixed: column is 'total_content_generated', not 'total_content'
    
    def test_database_constraints_and_integrity(self, db_connection):
        """Test database constraints and data integrity rules."""
        cursor = db_connection.cursor()
        
        # Test NOT NULL constraints
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO users (id, username, full_name, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('test-user', 'testuser', 'Test User', True,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            # Missing required email field
        
        # Test CHECK constraints
        with pytest.raises(sqlite3.IntegrityError):
            # Invalid creativity_level (should be 1-10)
            cursor.execute("""
                INSERT INTO campaigns (
                    id, user_id, name, campaign_type, status, creativity_level,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('test-campaign', 'test-user', 'Test Campaign', 'product', 'draft', 15,
                  datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Test foreign key constraints
        with pytest.raises(sqlite3.IntegrityError):
            # Reference non-existent user
            cursor.execute("""
                INSERT INTO campaigns (
                    id, user_id, name, campaign_type, status, creativity_level,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('test-campaign', 'non-existent-user', 'Test Campaign', 'product', 'draft', 5,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            db_connection.commit()  # Force commit to trigger foreign key constraint check
    
    def test_database_performance_indexes(self, db_connection):
        """Test database performance with indexes."""
        cursor = db_connection.cursor()
        
        # Test that indexes are being used for common queries
        cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?", ('test@example.com',))
        plan = cursor.fetchall()
        
        # Should use index for email lookup - extract actual text from Row objects
        plan_text = ' '.join([' '.join([str(col) for col in row]) for row in plan])
        assert 'idx_users_email' in plan_text or 'USING INDEX' in plan_text
        
        # Test campaign queries use indexes
        cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM campaigns WHERE user_id = ?", ('test-user',))
        plan = cursor.fetchall()
        plan_text = ' '.join([' '.join([str(col) for col in row]) for row in plan])
        assert 'idx_campaigns_user_id' in plan_text or 'USING INDEX' in plan_text
    
    def test_database_status_utility(self, test_db_path):
        """Test database status utility function."""
        # Test with our test database
        status = check_database_status(test_db_path)
        
        # The function returns True if database is healthy
        assert status is True, "Database status check should return True for valid database"
        
        # Verify database file exists
        assert os.path.exists(test_db_path), "Test database file should exist"
        
        # Verify database has content
        file_size = os.path.getsize(test_db_path)
        assert file_size > 1024, "Database should have meaningful content"  # At least 1KB


class TestAPIDatabaseCorrelation:
    """Test correlation between API structures and database operations."""
    
    def test_api_campaign_creation_database_persistence(self, db_connection):
        """Test that API campaign creation properly persists to database."""
        # This would typically be tested with actual API calls
        # For now, we simulate the API data structure
        
        api_campaign_request = {
            "business_description": "AI startup focused on marketing automation",
            "objective": "Launch new product campaign",
            "target_audience": "Small business owners",
            "campaign_type": "product",
            "creativity_level": 7,
            "business_website": "https://example.com",
            "uploaded_files": []
        }
        
        # Simulate API processing and database insertion
        cursor = db_connection.cursor()
        
        # Create user first
        user_id = 'api-test-user'
        cursor.execute("""
            INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, 'api@test.com', 'apiuser', 'API User', True,
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Transform API request to database format
        campaign_id = 'api-campaign-123'
        cursor.execute("""
            INSERT INTO campaigns (
                id, user_id, name, description, campaign_type, status,
                business_context, target_audience, objectives, creativity_level,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign_id, user_id, 'API Generated Campaign',
            api_campaign_request['business_description'],
            api_campaign_request['campaign_type'], 'draft',
            f'{{"website": "{api_campaign_request["business_website"]}"}}',
            api_campaign_request['target_audience'],
            api_campaign_request['objective'],
            api_campaign_request['creativity_level'],
            datetime.now().isoformat(), datetime.now().isoformat()
        ))
        
        db_connection.commit()
        
        # Verify data persistence
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        campaign = cursor.fetchone()
        
        assert campaign is not None
        assert campaign['campaign_type'] == api_campaign_request['campaign_type']
        assert campaign['creativity_level'] == api_campaign_request['creativity_level']
        assert campaign['target_audience'] == api_campaign_request['target_audience']
    
    def test_api_response_structure_matches_database_schema(self, db_connection):
        """Test that API response structures match database schema."""
        cursor = db_connection.cursor()
        
        # Create test data
        user_id = 'schema-test-user'
        campaign_id = 'schema-test-campaign'
        
        cursor.execute("""
            INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, 'schema@test.com', 'schemauser', 'Schema User', True,
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        cursor.execute("""
            INSERT INTO campaigns (
                id, user_id, name, description, campaign_type, status,
                business_context, target_audience, objectives, creativity_level,
                ai_analysis, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (campaign_id, user_id, 'Schema Test Campaign', 'Testing schema alignment',
              'brand', 'active', '{"company": "Test Corp"}', 'Developers',
              'Test objectives', 8, '{"confidence": 0.9}',
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        db_connection.commit()
        
        # Simulate API response generation
        cursor.execute("""
            SELECT c.*, u.username, u.email 
            FROM campaigns c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.id = ?
        """, (campaign_id,))
        
        campaign_data = cursor.fetchone()
        
        # Verify API response structure matches database fields
        expected_api_fields = [
            'id', 'name', 'description', 'campaign_type', 'status',
            'business_context', 'target_audience', 'objectives',
            'creativity_level', 'ai_analysis', 'created_at', 'updated_at'
        ]
        
        for field in expected_api_fields:
            assert field in campaign_data.keys(), f"Missing field {field} in database schema"


@pytest.mark.integration
class TestUserJourneyDatabase:
    """Test complete user journeys with database persistence."""
    
    def test_complete_campaign_creation_journey(self, db_connection):
        """Test complete user journey from registration to campaign creation."""
        cursor = db_connection.cursor()
        
        # Step 1: User registration
        user_data = {
            'id': 'journey-user-123',
            'email': 'journey@test.com',
            'username': 'journeyuser',
            'full_name': 'Journey Test User',
            'profile_data': '{"onboarding_completed": false}',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO users (id, email, username, full_name, profile_data, is_active, created_at, updated_at)
            VALUES (:id, :email, :username, :full_name, :profile_data, :is_active, :created_at, :updated_at)
        """, user_data)
        
        # Step 2: User session creation
        session_data = {
            'id': 'journey-session-123',
            'user_id': user_data['id'],
            'session_token': 'test-token-123',
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO user_sessions (id, user_id, session_token, expires_at, is_active, created_at, last_activity)
            VALUES (:id, :user_id, :session_token, :expires_at, :is_active, :created_at, :last_activity)
        """, session_data)
        
        # Step 3: Campaign creation
        campaign_data = {
            'id': 'journey-campaign-123',
            'user_id': user_data['id'],
            'name': 'Journey Test Campaign',
            'description': 'Complete user journey test',
            'campaign_type': 'product',
            'status': 'draft',
            'business_context': '{"company": "Journey Corp", "industry": "Technology"}',
            'target_audience': 'Tech enthusiasts',
            'objectives': 'Increase product awareness',
            'creativity_level': 6,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO campaigns (
                id, user_id, name, description, campaign_type, status,
                business_context, target_audience, objectives, creativity_level,
                created_at, updated_at
            ) VALUES (
                :id, :user_id, :name, :description, :campaign_type, :status,
                :business_context, :target_audience, :objectives, :creativity_level,
                :created_at, :updated_at
            )
        """, campaign_data)
        
        # Step 4: Content generation
        content_items = []
        for i in range(5):
            content_data = {
                'id': f'journey-content-{i}',
                'campaign_id': campaign_data['id'],
                'content_type': 'text_image',
                'platform': 'instagram',
                'content_data': f'{{"text": "Journey content {i}", "hashtags": ["#journey", "#test"]}}',
                'ai_metadata': '{"model": "gemini-2.0-flash", "generation_time": 2.5}',
                'user_rating': 3 + (i % 3),  # Valid range 1-5
                'is_selected': i < 2,  # Select first 2 items
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            cursor.execute("""
                INSERT INTO generated_content (
                    id, campaign_id, content_type, platform, content_data,
                    ai_metadata, user_rating, is_selected, created_at, updated_at
                ) VALUES (
                    :id, :campaign_id, :content_type, :platform, :content_data,
                    :ai_metadata, :user_rating, :is_selected, :created_at, :updated_at
                )
            """, content_data)
            
            content_items.append(content_data)
        
        db_connection.commit()
        
        # Verify complete journey data integrity
        cursor.execute("""
            SELECT 
                u.username, u.email,
                c.name as campaign_name, c.status,
                COUNT(gc.id) as total_content,
                SUM(CASE WHEN gc.is_selected THEN 1 ELSE 0 END) as selected_content,
                AVG(gc.user_rating) as avg_rating
            FROM users u
            JOIN campaigns c ON u.id = c.user_id
            JOIN generated_content gc ON c.id = gc.campaign_id
            WHERE u.id = ?
            GROUP BY u.id, c.id
        """, (user_data['id'],))
        
        journey_summary = cursor.fetchone()
        
        assert journey_summary is not None
        assert journey_summary['username'] == user_data['username']
        assert journey_summary['campaign_name'] == campaign_data['name']
        assert journey_summary['total_content'] == 5
        assert journey_summary['selected_content'] == 2
        assert journey_summary['avg_rating'] >= 3  # Updated for valid rating range
        
        # Verify session is active
        cursor.execute("SELECT is_active FROM user_sessions WHERE user_id = ?", (user_data['id'],))
        session = cursor.fetchone()
        assert session['is_active'] == 1  # SQLite stores boolean as integer


@pytest.mark.regression
class TestDatabaseRegression:
    """Regression tests for database functionality."""
    
    def test_schema_version_tracking(self, db_connection):
        """Test schema version tracking for migrations."""
        cursor = db_connection.cursor()
        
        cursor.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
        version = cursor.fetchone()
        
        assert version is not None
        assert version['version'] == '1.0.1'  # Updated to match current schema version
    
    def test_default_campaign_templates_exist(self, db_connection):
        """Test that default campaign templates are properly loaded."""
        cursor = db_connection.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM campaign_templates")
        template_count = cursor.fetchone()['count']
        
        assert template_count >= 3, "Default campaign templates should be loaded"
        
        # Test specific templates
        cursor.execute("SELECT name FROM campaign_templates ORDER BY name")
        templates = [row['name'] for row in cursor.fetchall()]
        
        expected_templates = ['Brand Awareness Campaign', 'Event Promotion Campaign', 'Product Launch Campaign']
        for template in expected_templates:
            assert template in templates, f"Missing default template: {template}"
    
    def test_database_constraints_not_regressed(self, db_connection):
        """Test that database constraints haven't been regressed."""
        cursor = db_connection.cursor()
        
        # Test email uniqueness constraint
        cursor.execute("""
            INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('regression-user-1', 'regression@test.com', 'regressionuser1', 'Regression User 1', True,
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('regression-user-2', 'regression@test.com', 'regressionuser2', 'Regression User 2', True,
                  datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Test creativity level constraint
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO campaigns (
                    id, user_id, name, campaign_type, status, creativity_level,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('regression-campaign', 'regression-user-1', 'Regression Campaign', 
                  'product', 'draft', 11,  # Invalid creativity level
                  datetime.now().isoformat(), datetime.now().isoformat())) 