"""
Tests for Decorators

This module tests the Decorator pattern implementation.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, session, request
from app.decorators.auth import admin_required, require_admin, optional_auth
from app.decorators.rate_limit import RateLimiter, rate_limit, per_user_rate_limit
from app.decorators.logging import log_request, monitor_performance, log_errors, cache_result, audit_log


class TestAuthDecorators:
    """Tests for authentication decorators"""
    
    @pytest.fixture
    def app_context(self, app):
        """Create app context for testing"""
        with app.test_request_context():
            yield
    
    def test_admin_required_not_authenticated(self, client):
        """Test admin_required redirects when not authenticated"""
        from app.blueprints.admin import admin_bp
        
        response = client.get('/admin/dashboard')
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/admin/login' in response.location
    
    def test_admin_required_authenticated(self, client, admin_credentials):
        """Test admin_required allows access when authenticated"""
        # Login first
        client.post('/admin/login', data=admin_credentials, follow_redirects=True)
        
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
        
        response = client.get('/admin/dashboard')
        
        # Should allow access
        assert response.status_code == 200
    
    def test_require_admin_decorator_function(self, app):
        """Test require_admin decorator as function"""
        @require_admin()
        def protected_view():
            return "Protected content"
        
        with app.test_request_context():
            with pytest.raises(Exception):  # Should raise redirect or abort
                protected_view()
    
    def test_optional_auth_no_session(self, app):
        """Test optional_auth with no session"""
        @optional_auth
        def view_func():
            return "Content"
        
        with app.test_request_context():
            result = view_func()
            assert result == "Content"


class TestRateLimitDecorators:
    """Tests for rate limiting decorators"""
    
    def test_rate_limiter_allows_under_limit(self):
        """Test rate limiter allows requests under limit"""
        limiter = RateLimiter(max_requests=5, window=60)
        
        for _ in range(5):
            assert limiter.is_allowed('test_key') == True
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit"""
        limiter = RateLimiter(max_requests=3, window=60)
        
        # Make 3 requests (allowed)
        for _ in range(3):
            assert limiter.is_allowed('test_key') == True
        
        # 4th request should be blocked
        assert limiter.is_allowed('test_key') == False
    
    def test_rate_limiter_reset_after_window(self):
        """Test rate limiter resets after time window"""
        limiter = RateLimiter(max_requests=2, window=1)  # 1 second window
        
        # Make 2 requests
        assert limiter.is_allowed('test_key') == True
        assert limiter.is_allowed('test_key') == True
        
        # Should be blocked
        assert limiter.is_allowed('test_key') == False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.is_allowed('test_key') == True
    
    def test_rate_limiter_different_keys(self):
        """Test rate limiter handles different keys separately"""
        limiter = RateLimiter(max_requests=2, window=60)
        
        # Key 1
        assert limiter.is_allowed('key1') == True
        assert limiter.is_allowed('key1') == True
        assert limiter.is_allowed('key1') == False
        
        # Key 2 should still be allowed
        assert limiter.is_allowed('key2') == True
        assert limiter.is_allowed('key2') == True
    
    def test_rate_limit_decorator(self, app):
        """Test rate_limit decorator"""
        @rate_limit(max_requests=3, window=60, key_func=lambda: 'test')
        def limited_view():
            return "Success"
        
        with app.test_request_context():
            # First 3 should succeed
            for _ in range(3):
                result = limited_view()
                assert result == "Success"
            
            # 4th should fail
            with pytest.raises(Exception):  # Should raise rate limit error
                limited_view()
    
    def test_per_user_rate_limit(self, app):
        """Test per_user_rate_limit decorator"""
        @per_user_rate_limit(max_requests=2, window=60)
        def user_limited_view():
            return "Success"
        
        with app.test_request_context():
            with app.test_client().session_transaction() as sess:
                sess['user_id'] = 'test_user'
            
            # First 2 should succeed
            result1 = user_limited_view()
            result2 = user_limited_view()
            assert result1 == "Success"
            assert result2 == "Success"


class TestLoggingDecorators:
    """Tests for logging decorators"""
    
    @patch('app.decorators.logging.current_app')
    def test_log_request_decorator(self, mock_app, app):
        """Test log_request decorator logs requests"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        @log_request
        def test_view():
            return "Response"
        
        with app.test_request_context('/test', method='GET'):
            result = test_view()
        
        assert result == "Response"
        mock_logger.info.assert_called()
    
    @patch('app.decorators.logging.current_app')
    def test_monitor_performance_decorator(self, mock_app, app):
        """Test monitor_performance decorator tracks execution time"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        @monitor_performance(threshold=0.1)
        def slow_view():
            time.sleep(0.15)
            return "Done"
        
        with app.test_request_context():
            result = slow_view()
        
        assert result == "Done"
        # Should log warning for slow request
        mock_logger.warning.assert_called()
    
    @patch('app.decorators.logging.current_app')
    def test_log_errors_decorator_success(self, mock_app, app):
        """Test log_errors decorator on successful execution"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        @log_errors
        def successful_view():
            return "Success"
        
        with app.test_request_context():
            result = successful_view()
        
        assert result == "Success"
        mock_logger.error.assert_not_called()
    
    @patch('app.decorators.logging.current_app')
    def test_log_errors_decorator_failure(self, mock_app, app):
        """Test log_errors decorator logs errors"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        @log_errors
        def failing_view():
            raise ValueError("Test error")
        
        with app.test_request_context():
            with pytest.raises(ValueError):
                failing_view()
        
        mock_logger.error.assert_called()
    
    def test_cache_result_decorator(self, app):
        """Test cache_result decorator caches function results"""
        call_count = [0]
        
        @cache_result(timeout=60)
        def expensive_operation(x):
            call_count[0] += 1
            return x * 2
        
        # First call
        result1 = expensive_operation(5)
        assert result1 == 10
        assert call_count[0] == 1
        
        # Second call should use cache
        result2 = expensive_operation(5)
        assert result2 == 10
        assert call_count[0] == 1  # Not incremented
        
        # Different argument should call function
        result3 = expensive_operation(10)
        assert result3 == 20
        assert call_count[0] == 2
    
    @patch('app.decorators.logging.current_app')
    def test_audit_log_decorator(self, mock_app, app):
        """Test audit_log decorator logs actions"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        @audit_log(action='test_action')
        def audited_view(data):
            return f"Processed {data}"
        
        with app.test_request_context():
            with app.test_client().session_transaction() as sess:
                sess['user_id'] = 'test_user'
            
            result = audited_view("test_data")
        
        assert "Processed test_data" in result
        mock_logger.info.assert_called()
        
        # Check that audit log contains action name
        call_args = mock_logger.info.call_args[0][0]
        assert 'test_action' in call_args


class TestDecoratorCombinations:
    """Tests for combining multiple decorators"""
    
    @patch('app.decorators.logging.current_app')
    def test_combined_decorators(self, mock_app, app):
        """Test combining multiple decorators"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        @log_request
        @log_errors
        @monitor_performance()
        def multi_decorated_view():
            return "Success"
        
        with app.test_request_context():
            result = multi_decorated_view()
        
        assert result == "Success"
        assert mock_logger.info.called
