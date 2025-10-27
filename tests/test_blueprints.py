"""
Integration Tests for Flask Blueprints

This module tests the blueprint integration and routing.
"""

import pytest
from flask import url_for
from config import TestingConfig


class TestNavigationBlueprint:
    """Tests for navigation blueprint"""
    
    def test_index_route(self, client):
        """Test index page loads"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'IT Quizbee' in response.data or b'Welcome' in response.data
    
    def test_topics_route(self, client):
        """Test topics page loads"""
        response = client.get('/topics')
        
        assert response.status_code == 200
    
    def test_subtopics_route(self, client):
        """Test subtopics page loads"""
        response = client.get('/subtopics/it_basics')
        
        assert response.status_code == 200
    
    def test_mode_selection_route(self, client):
        """Test mode selection page loads"""
        response = client.get('/mode_selection/it_basics/computer_basics')
        
        assert response.status_code == 200
    
    def test_set_user_name(self, client):
        """Test setting user name in session"""
        response = client.post('/set_user_name', data={'user_name': 'Test User'})
        
        assert response.status_code == 302  # Redirect
        
        with client.session_transaction() as sess:
            assert sess.get('user_name') == 'Test User'
    
    def test_clear_session(self, client):
        """Test clearing session"""
        # Set some session data
        with client.session_transaction() as sess:
            sess['user_name'] = 'Test'
            sess['some_data'] = 'data'
        
        response = client.get('/clear_session')
        
        assert response.status_code == 302
        with client.session_transaction() as sess:
            assert 'user_name' not in sess


class TestQuizBlueprint:
    """Tests for quiz blueprint"""
    
    def test_elimination_mode_route(self, client):
        """Test elimination mode quiz route"""
        response = client.post('/quiz/elimination', data={
            'topic': 'it_basics',
            'subtopic': 'computer_basics',
            'difficulty': 'easy'
        })
        
        # Should redirect to quiz page or show quiz
        assert response.status_code in [200, 302]
    
    def test_finals_mode_route(self, client):
        """Test finals mode quiz route"""
        response = client.post('/quiz/finals', data={
            'topic': 'it_basics',
            'subtopic': 'computer_basics',
            'difficulty': 'easy'
        })
        
        assert response.status_code in [200, 302]
    
    def test_submit_quiz_invalid_session(self, client):
        """Test submitting quiz with invalid session"""
        response = client.post('/quiz/submit_quiz/invalid_session', data={})
        
        # Should redirect or show error
        assert response.status_code in [302, 400, 404]
    
    def test_validate_session_invalid(self, client):
        """Test session validation endpoint"""
        response = client.get('/quiz/validate_session/invalid_session')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert data['valid'] == False
    
    def test_results_route(self, client):
        """Test results page route"""
        response = client.get('/quiz/results/some_attempt_id')
        
        # Should load results page or redirect
        assert response.status_code in [200, 302, 404]


class TestAdminBlueprint:
    """Tests for admin blueprint"""
    
    def test_login_page(self, client):
        """Test admin login page loads"""
        response = client.get('/admin/login')
        
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'admin' in response.data.lower()
    
    def test_login_post_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/admin/login', data={
            'username': 'wrong_user',
            'password': 'wrong_pass'
        })
        
        # Should redirect back or show error
        assert response.status_code in [200, 302]
    
    def test_login_post_valid_credentials(self, client, admin_credentials):
        """Test login with valid credentials from config"""
        response = client.post('/admin/login', data={
            'username': admin_credentials['username'],
            'password': admin_credentials['password']
        }, follow_redirects=False)
        
        # Should redirect to dashboard
        assert response.status_code == 302
    
    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/admin/dashboard')
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/admin/login' in response.location
    
    def test_logout(self, client):
        """Test admin logout"""
        # Login first
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
        
        response = client.get('/admin/logout')
        
        assert response.status_code == 302
        with client.session_transaction() as sess:
            assert 'admin_authenticated' not in sess


class TestAPIBlueprint:
    """Tests for API blueprint"""
    
    def test_api_health_check(self, client):
        """Test API health check endpoint"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert 'status' in data
    
    def test_api_topics(self, client):
        """Test API topics endpoint"""
        response = client.get('/api/topics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_api_statistics_overview(self, client):
        """Test API statistics overview endpoint"""
        response = client.get('/api/statistics/overview')
        
        # May require auth or return empty stats
        assert response.status_code in [200, 401, 403]
    
    def test_api_statistics_mode_comparison(self, client):
        """Test API mode comparison endpoint"""
        response = client.get('/api/statistics/mode-comparison')
        
        assert response.status_code in [200, 401, 403]
    
    def test_api_statistics_topic(self, client):
        """Test API topic statistics endpoint"""
        response = client.get('/api/statistics/topic')
        
        assert response.status_code in [200, 401, 403]
    
    def test_api_validate_session(self, client):
        """Test API session validation"""
        response = client.get('/api/validate-session/invalid_session')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'valid' in data
        assert data['valid'] == False


class TestBlueprintIntegration:
    """Integration tests for blueprint interactions"""
    
    def test_blueprint_url_prefixes(self, app):
        """Test that blueprints have correct URL prefixes"""
        with app.test_request_context():
            # Navigation blueprint (no prefix)
            assert url_for('navigation.index') == '/'
            assert url_for('navigation.topics') == '/topics'
            
            # Quiz blueprint (/quiz prefix)
            assert '/quiz/' in url_for('quiz.elimination_mode')
            
            # Admin blueprint (/admin prefix)
            assert '/admin/' in url_for('admin.login')
            
            # API blueprint (/api prefix)
            assert '/api/' in url_for('api.health')
    
    def test_error_handlers_registered(self, client):
        """Test that error handlers are registered"""
        # Try to access non-existent route
        response = client.get('/nonexistent/route/here')
        
        # Should return 404
        assert response.status_code == 404
    
    def test_all_blueprints_registered(self, app):
        """Test that all blueprints are registered"""
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        assert 'navigation' in blueprint_names
        assert 'quiz' in blueprint_names
        assert 'admin' in blueprint_names
        assert 'api' in blueprint_names
    
    def test_cross_blueprint_navigation(self, client):
        """Test navigation between blueprints"""
        # Start at index
        response = client.get('/')
        assert response.status_code == 200
        
        # Navigate to topics
        response = client.get('/topics')
        assert response.status_code == 200
        
        # Navigate to admin login
        response = client.get('/admin/login')
        assert response.status_code == 200
        
        # Check API endpoint
        response = client.get('/api/health')
        assert response.status_code == 200
