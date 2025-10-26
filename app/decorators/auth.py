"""
Authentication Decorators
Implements Decorator Pattern for adding authentication logic
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify


def admin_required(f):
    """
    Decorator to protect admin routes
    Requires active admin session
    
    Usage:
        @app.route('/admin')
        @admin_required
        def admin_page():
            return "Admin content"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            # Check if it's an API request
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            # Redirect to login for web pages
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def require_admin():
    """
    Decorator factory for analytics endpoints
    Returns 401 for API endpoints if not authenticated
    
    Usage:
        @analytics_bp.route('/summary')
        @require_admin()
        def get_summary():
            return jsonify(data)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return jsonify({'error': 'Unauthorized', 'message': 'Admin access required'}), 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def optional_auth(f):
    """
    Decorator that allows both authenticated and non-authenticated access
    Adds 'is_authenticated' to kwargs
    
    Usage:
        @app.route('/content')
        @optional_auth
        def content(is_authenticated=False):
            if is_authenticated:
                return "Premium content"
            return "Basic content"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        kwargs['is_authenticated'] = bool(session.get('admin_logged_in'))
        return f(*args, **kwargs)
    return decorated_function
