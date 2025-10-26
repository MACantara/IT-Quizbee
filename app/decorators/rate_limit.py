"""
Rate Limiting Decorator
Implements Decorator Pattern for rate limiting API requests
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import logging


class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, use Redis or similar
    """
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.logger = logging.getLogger(__name__)
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Unique identifier (e.g., IP address)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if allowed, False if rate limit exceeded
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            self.logger.warning(f"Rate limit exceeded for {key}")
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    def clear_all(self):
        """Clear all rate limit data"""
        self.requests.clear()


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(max_requests=60, window_seconds=60):
    """
    Decorator to add rate limiting to routes
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        
    Usage:
        @app.route('/api/data')
        @rate_limit(max_requests=10, window_seconds=60)
        def get_data():
            return jsonify(data)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as key
            key = request.remote_addr
            
            if not _rate_limiter.is_allowed(key, max_requests, window_seconds):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window_seconds} seconds'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def per_user_rate_limit(max_requests=100, window_seconds=3600):
    """
    Rate limit based on user session/ID
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        
    Usage:
        @app.route('/api/submit')
        @per_user_rate_limit(max_requests=5, window_seconds=60)
        def submit_quiz():
            return jsonify(result)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use session ID or user identifier
            user_id = request.cookies.get('quiz_session_id', request.remote_addr)
            
            if not _rate_limiter.is_allowed(f"user_{user_id}", max_requests, window_seconds):
                return jsonify({
                    'error': 'Too many requests',
                    'message': 'Please slow down and try again later'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
