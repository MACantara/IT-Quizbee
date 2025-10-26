"""
Error Handling Utilities
Provides consistent error responses across the application
"""

from flask import jsonify, render_template, request
from typing import Tuple, Union
import logging

logger = logging.getLogger('quiz.errors')


class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message: str, status_code: int = 400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert error to dictionary"""
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(APIError):
    """Raised when validation fails"""
    def __init__(self, message: str, payload=None):
        super().__init__(message, status_code=400, payload=payload)


class NotFoundError(APIError):
    """Raised when resource is not found"""
    def __init__(self, message: str, payload=None):
        super().__init__(message, status_code=404, payload=payload)


class AuthenticationError(APIError):
    """Raised when authentication fails"""
    def __init__(self, message: str, payload=None):
        super().__init__(message, status_code=401, payload=payload)


class AuthorizationError(APIError):
    """Raised when user lacks permissions"""
    def __init__(self, message: str, payload=None):
        super().__init__(message, status_code=403, payload=payload)


class ServerError(APIError):
    """Raised for internal server errors"""
    def __init__(self, message: str = "Internal server error", payload=None):
        super().__init__(message, status_code=500, payload=payload)


def handle_error(error: Exception, default_message: str = "An error occurred") -> Tuple[Union[dict, str], int]:
    """
    Handle errors and return appropriate response
    
    Args:
        error: The exception that occurred
        default_message: Default error message if none provided
        
    Returns:
        Tuple of (response, status_code)
    """
    # Log the error
    logger.error(f"Error occurred: {str(error)}", exc_info=True)
    
    # Determine if this is an API request
    is_api_request = (
        request.path.startswith('/api/') or 
        request.headers.get('Accept') == 'application/json' or
        request.headers.get('Content-Type') == 'application/json' or
        request.args.get('format') == 'json'
    )
    
    # Handle custom API errors
    if isinstance(error, APIError):
        if is_api_request:
            return jsonify(error.to_dict()), error.status_code
        else:
            return render_template(
                'error.html',
                error_message=error.message,
                status_code=error.status_code
            ), error.status_code
    
    # Handle validation errors
    if isinstance(error, ValueError):
        status_code = 400
        message = str(error) or default_message
        
        if is_api_request:
            return jsonify({
                'success': False,
                'error': message,
                'status_code': status_code
            }), status_code
        else:
            return render_template(
                'error.html',
                error_message=message,
                status_code=status_code
            ), status_code
    
    # Handle file not found errors
    if isinstance(error, FileNotFoundError):
        status_code = 404
        message = "Resource not found"
        
        if is_api_request:
            return jsonify({
                'success': False,
                'error': message,
                'status_code': status_code
            }), status_code
        else:
            return render_template(
                'error.html',
                error_message=message,
                status_code=status_code
            ), status_code
    
    # Handle generic exceptions
    status_code = 500
    message = str(error) if str(error) else default_message
    
    if is_api_request:
        return jsonify({
            'success': False,
            'error': message,
            'status_code': status_code
        }), status_code
    else:
        return render_template(
            'error.html',
            error_message=message,
            status_code=status_code
        ), status_code


def error_response(
    message: str,
    status_code: int = 400,
    **kwargs
) -> Tuple[Union[dict, str], int]:
    """
    Create an error response (JSON or HTML based on request context)
    
    Args:
        message: Error message
        status_code: HTTP status code
        **kwargs: Additional data to include in response
        
    Returns:
        Tuple of (response, status_code)
    """
    # Determine if this is an API request
    is_api_request = (
        request.path.startswith('/api/') or 
        request.headers.get('Accept') == 'application/json' or
        request.headers.get('Content-Type') == 'application/json' or
        request.args.get('format') == 'json'
    )
    
    if is_api_request:
        response_data = {
            'success': False,
            'error': message,
            'status_code': status_code
        }
        response_data.update(kwargs)
        return jsonify(response_data), status_code
    else:
        return render_template(
            'error.html',
            error_message=message,
            status_code=status_code,
            **kwargs
        ), status_code


def success_response(
    data=None,
    message: str = None,
    status_code: int = 200,
    **kwargs
) -> Tuple[dict, int]:
    """
    Create a success response for API endpoints
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        **kwargs: Additional data to include in response
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response_data = {
        'success': True,
        'status_code': status_code
    }
    
    if data is not None:
        response_data['data'] = data
    
    if message is not None:
        response_data['message'] = message
    
    response_data.update(kwargs)
    
    return jsonify(response_data), status_code
