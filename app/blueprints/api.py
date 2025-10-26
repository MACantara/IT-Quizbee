"""
API Blueprint
Handles API endpoints for AJAX requests and data export
"""

from flask import Blueprint, jsonify, request, session
from app.services import AnalyticsService, QuizService
from app.repositories import QuizAttemptRepository, QuizSessionRepository
from app.decorators.rate_limit import rate_limit
from app.decorators.logging import log_request, monitor_performance
from app.decorators.auth import require_admin

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Services will be initialized with repositories
analytics_service = None
quiz_service = None


def get_analytics_service():
    """Get or create analytics service instance"""
    global analytics_service
    if analytics_service is None:
        from models import db
        attempt_repo = QuizAttemptRepository(db.session)
        analytics_service = AnalyticsService(attempt_repo)
    return analytics_service


def get_quiz_service():
    """Get or create quiz service instance"""
    global quiz_service
    if quiz_service is None:
        from models import db
        session_repo = QuizSessionRepository(db.session)
        attempt_repo = QuizAttemptRepository(db.session)
        quiz_service = QuizService(session_repo, attempt_repo)
    return quiz_service


@api_bp.route('/statistics/overview', methods=['GET'])
@rate_limit(max_requests=30, window_seconds=60)
@log_request
def get_statistics_overview():
    """Get overview statistics"""
    days = request.args.get('days', 30, type=int)
    
    try:
        service = get_analytics_service()
        stats = service.get_dashboard_statistics(days=days)
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/statistics/mode-comparison', methods=['GET'])
@rate_limit(max_requests=30, window_seconds=60)
@log_request
def get_mode_comparison():
    """Get mode comparison statistics"""
    try:
        service = get_analytics_service()
        comparison = service.get_mode_comparison()
        
        return jsonify({
            'success': True,
            'data': comparison
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/statistics/difficulty', methods=['GET'])
@rate_limit(max_requests=30, window_seconds=60)
@log_request
def get_difficulty_analysis():
    """Get difficulty analysis"""
    try:
        service = get_analytics_service()
        analysis = service.get_difficulty_analysis()
        
        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/statistics/topic/<topic>', methods=['GET'])
@rate_limit(max_requests=30, window_seconds=60)
@log_request
def get_topic_performance(topic):
    """Get performance statistics for a specific topic"""
    try:
        service = get_analytics_service()
        performance = service.get_topic_performance(topic)
        
        return jsonify({
            'success': True,
            'data': performance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/statistics/user/<user_name>', methods=['GET'])
@rate_limit(max_requests=20, window_seconds=60)
@log_request
def get_user_performance(user_name):
    """Get performance statistics for a specific user"""
    days = request.args.get('days', 30, type=int)
    
    try:
        service = get_analytics_service()
        performance = service.get_user_performance(user_name, days)
        
        return jsonify({
            'success': True,
            'data': performance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/statistics/export', methods=['GET'])
@require_admin()
@rate_limit(max_requests=5, window_seconds=300)
@log_request
@monitor_performance
def export_statistics():
    """Export comprehensive statistics (admin only)"""
    format_type = request.args.get('format', 'json')
    
    try:
        service = get_analytics_service()
        data = service.export_statistics(format=format_type)
        
        return jsonify({
            'success': True,
            'format': format_type,
            'data': data
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/topics', methods=['GET'])
@rate_limit(max_requests=60, window_seconds=60)
def get_topics():
    """Get list of available topics"""
    try:
        service = get_quiz_service()
        topics = service.get_available_topics()
        
        return jsonify({
            'success': True,
            'data': topics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/topics/<topic>/subtopics', methods=['GET'])
@rate_limit(max_requests=60, window_seconds=60)
def get_subtopics(topic):
    """Get subtopics for a topic"""
    try:
        service = get_quiz_service()
        subtopics = service.get_subtopics(topic)
        
        return jsonify({
            'success': True,
            'data': subtopics
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/quiz/validate-session', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=60)
def validate_quiz_session():
    """Validate quiz session"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({
            'success': False,
            'error': 'No session ID provided'
        }), 400
    
    try:
        service = get_quiz_service()
        is_valid, error = service.validate_session(session_id)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'error': error
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/quiz/time-remaining', methods=['GET'])
@rate_limit(max_requests=60, window_seconds=60)
def get_time_remaining():
    """Get time remaining for current quiz session"""
    session_id = session.get('quiz_session_id')
    
    if not session_id:
        return jsonify({
            'success': False,
            'error': 'No active quiz session'
        }), 404
    
    try:
        from models import QuizSession
        quiz_session = QuizSession.query.get(session_id)
        
        if not quiz_session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        time_remaining = quiz_session.get_time_remaining()
        
        return jsonify({
            'success': True,
            'time_remaining': time_remaining,
            'expired': quiz_session.is_expired()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'IT Quizbee API',
        'version': '2.0.0'
    })


@api_bp.errorhandler(404)
def api_not_found(error):
    """API 404 handler"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@api_bp.errorhandler(500)
def api_server_error(error):
    """API 500 handler"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
