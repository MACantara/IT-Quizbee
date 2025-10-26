"""
Authentication Service Layer
Handles business logic for authentication and authorization
"""

import hashlib
import secrets
from typing import Optional, Tuple, Dict
from datetime import datetime, timedelta

from flask import session
from app.events.event_manager import event_manager, Event, EventType


class AuthService:
    """Service layer for authentication business logic"""
    
    def __init__(self):
        # In production, these should be in database with hashed passwords
        self.admin_credentials = {
            'admin': self._hash_password('admin123'),  # Default admin
        }
        self.session_timeout = timedelta(hours=2)
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_admin(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate admin user
        
        Args:
            username: Admin username
            password: Admin password
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if username exists
        if username not in self.admin_credentials:
            return False, "Invalid username or password"
        
        # Verify password
        hashed_password = self._hash_password(password)
        if hashed_password != self.admin_credentials[username]:
            return False, "Invalid username or password"
        
        # Create session
        self._create_admin_session(username)
        
        # Trigger event
        event_manager.notify(Event(
            EventType.USER_LOGGED_IN,
            data={
                'username': username,
                'role': 'admin',
                'timestamp': datetime.now().isoformat()
            }
        ))
        
        return True, None
    
    def _create_admin_session(self, username: str):
        """
        Create admin session
        
        Args:
            username: Admin username
        """
        session['is_admin'] = True
        session['admin_username'] = username
        session['login_time'] = datetime.now().isoformat()
        session['session_token'] = secrets.token_urlsafe(32)
    
    def logout_admin(self):
        """Logout admin user"""
        username = session.get('admin_username', 'Unknown')
        
        # Clear session
        session.pop('is_admin', None)
        session.pop('admin_username', None)
        session.pop('login_time', None)
        session.pop('session_token', None)
        
        # Trigger event
        event_manager.notify(Event(
            EventType.USER_LOGGED_OUT,
            data={
                'username': username,
                'role': 'admin',
                'timestamp': datetime.now().isoformat()
            }
        ))
    
    def is_admin_authenticated(self) -> bool:
        """
        Check if current user is authenticated as admin
        
        Returns:
            True if authenticated, False otherwise
        """
        if not session.get('is_admin'):
            return False
        
        # Check session timeout
        login_time_str = session.get('login_time')
        if not login_time_str:
            return False
        
        login_time = datetime.fromisoformat(login_time_str)
        if datetime.now() - login_time > self.session_timeout:
            # Session expired
            self.logout_admin()
            return False
        
        return True
    
    def get_admin_info(self) -> Optional[Dict]:
        """
        Get current admin user info
        
        Returns:
            Admin info dictionary or None
        """
        if not self.is_admin_authenticated():
            return None
        
        login_time_str = session.get('login_time')
        login_time = datetime.fromisoformat(login_time_str) if login_time_str else None
        
        return {
            'username': session.get('admin_username'),
            'role': 'admin',
            'login_time': login_time.isoformat() if login_time else None,
            'session_duration': str(datetime.now() - login_time) if login_time else None
        }
    
    def create_user_session(self, user_name: str) -> Dict:
        """
        Create session for quiz user (not admin)
        
        Args:
            user_name: User name
            
        Returns:
            Session info dictionary
        """
        session_token = secrets.token_urlsafe(16)
        
        session['user_name'] = user_name
        session['user_session_token'] = session_token
        session['user_session_start'] = datetime.now().isoformat()
        
        return {
            'user_name': user_name,
            'session_token': session_token,
            'session_start': session['user_session_start']
        }
    
    def get_current_user(self) -> Optional[str]:
        """
        Get current quiz user name
        
        Returns:
            User name or None
        """
        return session.get('user_name')
    
    def clear_user_session(self):
        """Clear quiz user session"""
        session.pop('user_name', None)
        session.pop('user_session_token', None)
        session.pop('user_session_start', None)
    
    def validate_session_token(self, token: str, token_type: str = 'admin') -> bool:
        """
        Validate session token
        
        Args:
            token: Session token
            token_type: 'admin' or 'user'
            
        Returns:
            True if valid, False otherwise
        """
        if token_type == 'admin':
            return session.get('session_token') == token
        elif token_type == 'user':
            return session.get('user_session_token') == token
        return False
    
    def add_admin_user(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Add new admin user
        
        Args:
            username: New admin username
            password: New admin password
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate username
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if username in self.admin_credentials:
            return False, "Username already exists"
        
        # Validate password
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Hash and store password
        self.admin_credentials[username] = self._hash_password(password)
        
        return True, None
    
    def change_admin_password(
        self, 
        username: str, 
        old_password: str, 
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change admin password
        
        Args:
            username: Admin username
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, error_message)
        """
        # Verify old password
        success, error = self.authenticate_admin(username, old_password)
        if not success:
            return False, "Current password is incorrect"
        
        # Validate new password
        if not new_password or len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        if old_password == new_password:
            return False, "New password must be different from old password"
        
        # Update password
        self.admin_credentials[username] = self._hash_password(new_password)
        
        return True, None
    
    def remove_admin_user(self, username: str) -> Tuple[bool, Optional[str]]:
        """
        Remove admin user
        
        Args:
            username: Admin username to remove
            
        Returns:
            Tuple of (success, error_message)
        """
        if username not in self.admin_credentials:
            return False, "Username not found"
        
        if username == 'admin':
            return False, "Cannot remove default admin user"
        
        del self.admin_credentials[username]
        return True, None
    
    def get_all_admins(self) -> list:
        """
        Get list of all admin usernames
        
        Returns:
            List of admin usernames
        """
        return list(self.admin_credentials.keys())
