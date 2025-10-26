"""
Logging and Monitoring Decorators
Implements Decorator Pattern for request logging and performance monitoring
"""

from functools import wraps
from flask import request, g
from datetime import datetime
import logging
import time


def log_request(f):
    """
    Decorator to log all requests to a route
    
    Usage:
        @app.route('/api/data')
        @log_request
        def get_data():
            return jsonify(data)
    """
    logger = logging.getLogger('quiz.requests')
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log request details
        logger.info(
            f"{request.method} {request.path} - "
            f"IP: {request.remote_addr} - "
            f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
        )
        
        # Execute function
        response = f(*args, **kwargs)
        
        # Log response status
        if hasattr(response, 'status_code'):
            logger.info(f"Response: {response.status_code}")
        
        return response
    
    return decorated_function


def monitor_performance(f):
    """
    Decorator to monitor route performance
    Logs execution time
    
    Usage:
        @app.route('/expensive-operation')
        @monitor_performance
        def expensive_op():
            return result
    """
    logger = logging.getLogger('quiz.performance')
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Store in Flask g for access in other functions
        g.request_start_time = start_time
        
        # Execute function
        response = f(*args, **kwargs)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log performance
        logger.info(
            f"{request.method} {request.path} - "
            f"Duration: {duration:.3f}s"
        )
        
        # Warn if slow
        if duration > 1.0:
            logger.warning(
                f"Slow request detected: {request.path} took {duration:.3f}s"
            )
        
        return response
    
    return decorated_function


def log_errors(f):
    """
    Decorator to log errors and exceptions
    
    Usage:
        @app.route('/risky-operation')
        @log_errors
        def risky_op():
            return result
    """
    logger = logging.getLogger('quiz.errors')
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Log the error
            logger.error(
                f"Error in {request.path}: {str(e)}",
                exc_info=True
            )
            # Re-raise to let Flask handle it
            raise
    
    return decorated_function


def cache_result(timeout=300):
    """
    Simple caching decorator (in-memory)
    For production, use Redis or Memcached
    
    Args:
        timeout: Cache timeout in seconds
        
    Usage:
        @app.route('/api/stats')
        @cache_result(timeout=60)
        def get_stats():
            return expensive_computation()
    """
    from functools import lru_cache
    
    def decorator(f):
        # Use LRU cache for simple in-memory caching
        cached_func = lru_cache(maxsize=128)(f)
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For more sophisticated caching, implement TTL logic
            return cached_func(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def audit_log(action: str):
    """
    Decorator to log actions for audit trail
    
    Args:
        action: Description of action being logged
        
    Usage:
        @app.route('/admin/delete-user')
        @audit_log("User deletion")
        def delete_user():
            return result
    """
    logger = logging.getLogger('quiz.audit')
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Log action
            logger.info(
                f"AUDIT: {action} - "
                f"User: {request.remote_addr} - "
                f"Path: {request.path} - "
                f"Method: {request.method} - "
                f"Timestamp: {datetime.utcnow().isoformat()}"
            )
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def combine_decorators(*decorators):
    """
    Helper to combine multiple decorators
    
    Usage:
        common_decorators = combine_decorators(log_request, monitor_performance, log_errors)
        
        @app.route('/api/data')
        @common_decorators
        def get_data():
            return data
    """
    def decorator(f):
        for dec in reversed(decorators):
            f = dec(f)
        return f
    return decorator
