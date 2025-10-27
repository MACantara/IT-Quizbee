"""
API Blueprint
Handles API endpoints for AJAX requests and data export
"""

from flask import Blueprint, jsonify, request, session
from app.services import AnalyticsService, QuizService
from app.services.question_analytics_service import QuestionAnalyticsService
from app.repositories import QuizAttemptRepository, QuizSessionRepository
from app.repositories.question_report_repository import QuestionReportRepository
from app.decorators.rate_limit import rate_limit
from app.decorators.logging import log_request, monitor_performance
from app.decorators.auth import require_admin

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Services will be initialized with repositories
analytics_service = None
quiz_service = None
question_analytics_service = None
question_report_repo = None


def get_analytics_service():
    """Get or create analytics service instance"""
    global analytics_service
    if analytics_service is None:
        attempt_repo = QuizAttemptRepository()
        analytics_service = AnalyticsService(attempt_repo)
    return analytics_service


def get_quiz_service():
    """Get or create quiz service instance"""
    global quiz_service
    if quiz_service is None:
        session_repo = QuizSessionRepository()
        attempt_repo = QuizAttemptRepository()
        quiz_service = QuizService(session_repo, attempt_repo)
    return quiz_service


def get_question_analytics_service():
    """Get or create question analytics service instance"""
    global question_analytics_service
    if question_analytics_service is None:
        question_analytics_service = QuestionAnalyticsService()
    return question_analytics_service


def get_question_report_repo():
    """Get or create question report repository instance"""
    global question_report_repo
    if question_report_repo is None:
        question_report_repo = QuestionReportRepository()
    return question_report_repo


@api_bp.route('/statistics/overview', methods=['GET'])
@rate_limit(max_requests=60, window_seconds=60)
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
@rate_limit(max_requests=60, window_seconds=60)
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
@rate_limit(max_requests=60, window_seconds=60)
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
@rate_limit(max_requests=60, window_seconds=60)
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
@rate_limit(max_requests=60, window_seconds=60)
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
@rate_limit(max_requests=60, window_seconds=60)
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
@rate_limit(max_requests=60, window_seconds=60)
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


# ===== QUESTION REPORTING ENDPOINTS =====

@api_bp.route('/questions/report', methods=['POST'])
@rate_limit(max_requests=60, window_seconds=60)
@log_request
def submit_question_report():
    """
    Submit a question report
    
    POST data:
    {
        "question_id": "string",
        "report_type": "incorrect_answer|unclear_question|typo|outdated|other",
        "reason": "string",
        "user_name": "string",
        "topic": "string",
        "subtopic": "string",
        "quiz_type": "string",
        "difficulty": "string",
        "question_text": "string",
        "question_data": {...}
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('question_id'):
            return jsonify({
                'success': False,
                'error': 'Question ID is required'
            }), 400
        
        if not data.get('report_type'):
            return jsonify({
                'success': False,
                'error': 'Report type is required'
            }), 400
        
        # Create report
        repo = get_question_report_repo()
        report = repo.create(
            question_id=data.get('question_id'),
            report_type=data.get('report_type'),
            reason=data.get('reason'),
            user_name=data.get('user_name'),
            topic=data.get('topic'),
            subtopic=data.get('subtopic'),
            quiz_type=data.get('quiz_type'),
            difficulty=data.get('difficulty'),
            question_text=data.get('question_text'),
            question_data=data.get('question_data')
        )
        
        return jsonify({
            'success': True,
            'message': 'Question report submitted successfully',
            'report_id': report.id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to submit report: {str(e)}'
        }), 500


@api_bp.route('/questions/reports', methods=['GET'])
@require_admin()
@rate_limit(max_requests=60, window_seconds=60)
@log_request
def get_question_reports():
    """
    Get all question reports (admin only)
    
    Query params:
    - status: Filter by status (pending, reviewed, resolved, dismissed)
    - limit: Maximum number of reports to return
    """
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', type=int)
        
        repo = get_question_report_repo()
        reports = repo.get_all(status=status, limit=limit)
        
        return jsonify({
            'success': True,
            'reports': [report.to_dict() for report in reports],
            'count': len(reports)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve reports: {str(e)}'
        }), 500


@api_bp.route('/questions/reports/pending-count', methods=['GET'])
@require_admin()
@rate_limit(max_requests=60, window_seconds=60)
def get_pending_reports_count():
    """Get count of pending question reports"""
    try:
        repo = get_question_report_repo()
        count = repo.get_pending_count()
        
        return jsonify({
            'success': True,
            'count': count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get pending count: {str(e)}'
        }), 500


@api_bp.route('/questions/reports/<report_id>', methods=['PATCH'])
@require_admin()
@rate_limit(max_requests=60, window_seconds=60)
@log_request
def update_question_report(report_id):
    """
    Update a question report status (admin only)
    
    PATCH data:
    {
        "status": "reviewed|resolved|dismissed",
        "admin_name": "string",
        "notes": "string"
    }
    """
    try:
        data = request.get_json()
        
        status = data.get('status')
        admin_name = data.get('admin_name') or session.get('admin_username', 'Admin')
        notes = data.get('notes')
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400
        
        if status not in ['reviewed', 'resolved', 'dismissed']:
            return jsonify({
                'success': False,
                'error': 'Invalid status value'
            }), 400
        
        repo = get_question_report_repo()
        report = repo.update_status(report_id, status, admin_name, notes)
        
        if not report:
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Report updated successfully',
            'report': report.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update report: {str(e)}'
        }), 500


@api_bp.route('/questions/reports/<report_id>', methods=['DELETE'])
@require_admin()
@rate_limit(max_requests=60, window_seconds=60)
@log_request
def delete_question_report(report_id):
    """Delete a question report (admin only)"""
    try:
        repo = get_question_report_repo()
        deleted = repo.delete(report_id)
        
        if not deleted:
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Report deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete report: {str(e)}'
        }), 500


@api_bp.route('/questions/analytics', methods=['GET'])
@require_admin()
@rate_limit(max_requests=60, window_seconds=60)
@log_request
def get_question_analytics():
    """
    Get question-level analytics (admin only)
    
    Query params:
    - limit: Maximum number of questions per category (default 20)
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        service = get_question_analytics_service()
        analytics = service.get_question_statistics(limit=limit)
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve analytics: {str(e)}'
        }), 500


@api_bp.route('/questions/<question_id>/details', methods=['GET'])
@require_admin()
@rate_limit(max_requests=60, window_seconds=60)
def get_question_details(question_id):
    """Get detailed analytics for a specific question"""
    try:
        service = get_question_analytics_service()
        details = service.get_question_details(question_id)
        
        if not details:
            return jsonify({
                'success': False,
                'error': 'Question not found or no data available'
            }), 404
        
        return jsonify({
            'success': True,
            'details': details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve question details: {str(e)}'
        }), 500


@api_bp.route('/questions/improvement-insights', methods=['GET'])
@require_admin()
@rate_limit(max_requests=60, window_seconds=60)
@log_request
def get_improvement_insights():
    """
    Get questions needing improvement with detailed recommendations
    
    Query params:
    - limit: Maximum number of questions (default 20)
    - max_success_rate: Threshold for success rate (default 60)
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        max_success_rate = request.args.get('max_success_rate', 60, type=int)
        
        service = get_question_analytics_service()
        questions = service.get_questions_needing_improvement(
            limit=limit,
            max_success_rate=max_success_rate
        )
        
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve improvement insights: {str(e)}'
        }), 500


@api_bp.route('/questions/<question_id>/answer-pattern', methods=['GET'])
@require_admin()
@rate_limit(max_requests=60, window_seconds=60)
def get_answer_pattern(question_id):
    """Get answer pattern analysis for a specific question"""
    try:
        service = get_question_analytics_service()
        pattern = service.get_answer_pattern_analysis(question_id)
        
        if not pattern or not pattern.get('question_info'):
            return jsonify({
                'success': False,
                'error': 'Question not found or no data available'
            }), 404
        
        return jsonify({
            'success': True,
            'pattern': pattern
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve answer pattern: {str(e)}'
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
