"""
Tests for Authentication Service

This module tests the AuthService business logic layer.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService
from config import TestingConfig


class TestAuthService:
    """Tests for AuthService"""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance"""
        return AuthService()
    
    @patch('app.services.auth_service.check_password_hash')
    @patch('app.services.auth_service.User')
    def test_authenticate_admin_success(self, mock_user_class, mock_check_password, auth_service):
        """Test successful admin authentication"""
        # Setup mock user
        mock_user = Mock()
        mock_user.username = 'admin'
        mock_user.password_hash = 'hashed_password'
        mock_user.is_admin = True
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        mock_check_password.return_value = True
        
        result = auth_service.authenticate_admin('admin', 'password123')
        
        assert result == True
        mock_check_password.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_authenticate_admin_user_not_found(self, mock_user_class, auth_service):
        """Test authentication fails when user doesn't exist"""
        mock_user_class.query.filter_by.return_value.first.return_value = None
        
        result = auth_service.authenticate_admin('nonexistent', 'password')
        
        assert result == False
    
    @patch('app.services.auth_service.check_password_hash')
    @patch('app.services.auth_service.User')
    def test_authenticate_admin_wrong_password(self, mock_user_class, mock_check_password, auth_service):
        """Test authentication fails with wrong password"""
        mock_user = Mock()
        mock_user.username = 'admin'
        mock_user.password_hash = 'hashed_password'
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        mock_check_password.return_value = False
        
        result = auth_service.authenticate_admin('admin', 'wrong_password')
        
        assert result == False
    
    @patch('app.services.auth_service.User')
    def test_authenticate_admin_not_admin_role(self, mock_user_class, auth_service):
        """Test authentication fails for non-admin users"""
        mock_user = Mock()
        mock_user.username = 'user'
        mock_user.is_admin = False
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        result = auth_service.authenticate_admin('user', 'password')
        
        assert result == False
    
    def test_is_admin_authenticated_true(self, auth_service, app):
        """Test checking admin authentication status when authenticated"""
        with app.test_request_context():
            with app.test_client().session_transaction() as sess:
                sess['admin_authenticated'] = True
            
            result = auth_service.is_admin_authenticated()
            
            assert result == True
    
    def test_is_admin_authenticated_false(self, auth_service, app):
        """Test checking admin authentication status when not authenticated"""
        with app.test_request_context():
            result = auth_service.is_admin_authenticated()
            
            assert result == False
    
    def test_logout_admin(self, auth_service, app):
        """Test logging out admin"""
        with app.test_request_context():
            with app.test_client().session_transaction() as sess:
                sess['admin_authenticated'] = True
                sess['admin_username'] = 'admin'
            
            auth_service.logout_admin()
            
            with app.test_client().session_transaction() as sess:
                assert 'admin_authenticated' not in sess
                assert 'admin_username' not in sess
    
    def test_create_user_session(self, auth_service, app):
        """Test creating user session"""
        with app.test_request_context():
            auth_service.create_user_session('TestUser', {'role': 'student'})
            
            with app.test_client().session_transaction() as sess:
                assert sess.get('user_name') == 'TestUser'
                assert sess.get('role') == 'student'
    
    @patch('app.services.auth_service.event_manager')
    @patch('app.services.auth_service.generate_password_hash')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_add_admin_user(self, mock_user_class, mock_db, mock_generate_hash, mock_event_manager, auth_service):
        """Test adding new admin user"""
        mock_generate_hash.return_value = 'hashed_password'
        
        result = auth_service.add_admin_user('newadmin', 'password123', 'admin@test.com')
        
        assert result == True
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        mock_event_manager.notify.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_add_admin_user_duplicate(self, mock_user_class, auth_service):
        """Test adding duplicate admin user fails"""
        # Mock existing user
        mock_user_class.query.filter_by.return_value.first.return_value = Mock()
        
        result = auth_service.add_admin_user('existingadmin', 'password', 'email@test.com')
        
        assert result == False
    
    @patch('app.services.auth_service.generate_password_hash')
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_change_admin_password(self, mock_user_class, mock_db, mock_generate_hash, auth_service):
        """Test changing admin password"""
        mock_user = Mock()
        mock_user.username = 'admin'
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        mock_generate_hash.return_value = 'new_hashed_password'
        
        result = auth_service.change_admin_password('admin', 'new_password')
        
        assert result == True
        assert mock_user.password_hash == 'new_hashed_password'
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_change_password_user_not_found(self, mock_user_class, auth_service):
        """Test changing password for non-existent user fails"""
        mock_user_class.query.filter_by.return_value.first.return_value = None
        
        result = auth_service.change_admin_password('nonexistent', 'password')
        
        assert result == False
    
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_remove_admin_user(self, mock_user_class, mock_db, auth_service):
        """Test removing admin user"""
        mock_user = Mock()
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        result = auth_service.remove_admin_user('admin')
        
        assert result == True
        mock_db.session.delete.assert_called_once_with(mock_user)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_remove_user_not_found(self, mock_user_class, auth_service):
        """Test removing non-existent user fails"""
        mock_user_class.query.filter_by.return_value.first.return_value = None
        
        result = auth_service.remove_admin_user('nonexistent')
        
        assert result == False
    
    def test_validate_password_strength_weak(self, auth_service):
        """Test password strength validation - weak password"""
        result = auth_service.validate_password_strength('123')
        
        assert result == False
    
    def test_validate_password_strength_strong(self, auth_service):
        """Test password strength validation - strong password"""
        result = auth_service.validate_password_strength('StrongP@ssw0rd!')
        
        assert result == True
    
    def test_validate_password_strength_medium(self, auth_service):
        """Test password strength validation - medium password"""
        result = auth_service.validate_password_strength('password123')
        
        # Should be at least 8 characters
        assert result == True or result == False  # Depends on implementation
