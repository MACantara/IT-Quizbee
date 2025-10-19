"""
Analytics and reporting endpoints for IT-Quizbee
Provides insights into quiz attempts and student performance
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from models import db, QuizAttempt, QuizSession

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/summary', methods=['GET'])
def get_summary():
    """
    Get overall quiz statistics
    
    Returns:
        - Total attempts
        - Average score
        - Most popular mode
        - Average time to complete
    """
    try:
        total_attempts = QuizAttempt.query.count()
        
        if total_attempts == 0:
            return jsonify({
                'total_attempts': 0,
                'average_score': 0,
                'message': 'No quiz attempts yet'
            }), 200
        
        # Calculate average score
        avg_score = db.session.query(
            func.avg(QuizAttempt.score_percentage)
        ).scalar() or 0
        
        # Get most common mode
        mode_stats = db.session.query(
            QuizAttempt.quiz_mode,
            func.count(QuizAttempt.id).label('count')
        ).group_by(QuizAttempt.quiz_mode).order_by(desc(func.count(QuizAttempt.id))).all()
        
        most_popular_mode = mode_stats[0][0] if mode_stats else None
        
        # Calculate average session duration
        sessions = QuizSession.query.filter(
            QuizSession.completed == True
        ).all()
        
        total_duration = 0
        completed_sessions = 0
        for session in sessions:
            if session.completed_at or session.expires_at:
                duration = (session.expires_at - session.created_at).total_seconds()
                total_duration += duration
                completed_sessions += 1
        
        avg_duration = (total_duration / completed_sessions) if completed_sessions > 0 else 0
        
        return jsonify({
            'total_attempts': total_attempts,
            'average_score': round(avg_score, 2),
            'most_popular_mode': most_popular_mode,
            'average_duration_seconds': int(avg_duration),
            'completed_sessions': completed_sessions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/by-mode', methods=['GET'])
def get_stats_by_mode():
    """
    Get statistics grouped by quiz mode
    
    Returns:
        - Breakdown by elimination, finals, review
        - Count, average score, min/max scores
    """
    try:
        modes = QuizAttempt.query.distinct(QuizAttempt.quiz_mode).all()
        mode_names = set([attempt.quiz_mode for attempt in modes])
        
        stats = {}
        for mode in mode_names:
            attempts = QuizAttempt.query.filter_by(quiz_mode=mode).all()
            scores = [a.score_percentage for a in attempts]
            
            stats[mode] = {
                'count': len(attempts),
                'average_score': round(sum(scores) / len(scores), 2) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'total_questions_answered': sum([a.total_questions for a in attempts])
            }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/by-difficulty', methods=['GET'])
def get_stats_by_difficulty():
    """
    Get statistics grouped by difficulty level (finals mode)
    
    Returns:
        - Breakdown by easy, average, difficult
    """
    try:
        difficulties = QuizAttempt.query.filter(
            QuizAttempt.difficulty != None
        ).distinct(QuizAttempt.difficulty).all()
        
        difficulty_names = set([
            attempt.difficulty for attempt in difficulties
            if attempt.difficulty
        ])
        
        stats = {}
        for difficulty in difficulty_names:
            attempts = QuizAttempt.query.filter_by(difficulty=difficulty).all()
            scores = [a.score_percentage for a in attempts]
            
            stats[difficulty] = {
                'count': len(attempts),
                'average_score': round(sum(scores) / len(scores), 2) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0
            }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/by-topic', methods=['GET'])
def get_stats_by_topic():
    """
    Get statistics grouped by topic (review mode)
    
    Returns:
        - Breakdown by each topic
    """
    try:
        topics = QuizAttempt.query.filter(
            QuizAttempt.topic_id != None
        ).distinct(QuizAttempt.topic_id).all()
        
        topic_ids = set([
            attempt.topic_id for attempt in topics
            if attempt.topic_id
        ])
        
        stats = {}
        for topic_id in topic_ids:
            attempts = QuizAttempt.query.filter_by(topic_id=topic_id).all()
            scores = [a.score_percentage for a in attempts]
            
            stats[topic_id] = {
                'count': len(attempts),
                'average_score': round(sum(scores) / len(scores), 2) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0
            }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/recent-attempts', methods=['GET'])
def get_recent_attempts():
    """
    Get recent quiz attempts with optional filtering
    
    Query Parameters:
        - limit: Number of attempts (default: 10, max: 100)
        - days: Include attempts from last N days (default: 7)
        - mode: Filter by quiz mode (optional)
    
    Returns:
        - List of recent attempts with scores and timestamps
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        days = int(request.args.get('days', 7))
        mode = request.args.get('mode')
        
        # Calculate date range
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = QuizAttempt.query.filter(
            QuizAttempt.created_at >= since_date
        )
        
        if mode:
            query = query.filter_by(quiz_mode=mode)
        
        # Get results ordered by most recent
        attempts = query.order_by(desc(QuizAttempt.created_at)).limit(limit).all()
        
        result = [
            {
                'id': attempt.id,
                'quiz_mode': attempt.quiz_mode,
                'score': attempt.score_percentage,
                'correct': attempt.correct_answers,
                'total': attempt.total_questions,
                'difficulty': attempt.difficulty,
                'created_at': attempt.created_at.isoformat()
            }
            for attempt in attempts
        ]
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/attempt/<attempt_id>', methods=['GET'])
def get_attempt_details(attempt_id):
    """
    Get detailed information about a specific quiz attempt
    
    Args:
        attempt_id: ID of the quiz attempt
    
    Returns:
        - Complete attempt details including all answers
    """
    try:
        attempt = QuizAttempt.query.get(attempt_id)
        
        if not attempt:
            return jsonify({'error': 'Attempt not found'}), 404
        
        return jsonify({
            'id': attempt.id,
            'session_id': attempt.session_id,
            'quiz_mode': attempt.quiz_mode,
            'topic_id': attempt.topic_id,
            'subtopic_id': attempt.subtopic_id,
            'difficulty': attempt.difficulty,
            'total_questions': attempt.total_questions,
            'correct_answers': attempt.correct_answers,
            'score_percentage': attempt.score_percentage,
            'answers': attempt.get_answers(),
            'created_at': attempt.created_at.isoformat(),
            'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/performance-trend', methods=['GET'])
def get_performance_trend():
    """
    Get performance trend over time
    
    Query Parameters:
        - days: Number of days to include (default: 30)
        - interval: Grouping interval - 'day', 'week', 'month' (default: 'day')
    
    Returns:
        - Average scores grouped by time interval
    """
    try:
        days = int(request.args.get('days', 30))
        interval = request.args.get('interval', 'day').lower()
        
        if interval not in ['day', 'week', 'month']:
            return jsonify({'error': 'Invalid interval. Use day, week, or month'}), 400
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        attempts = QuizAttempt.query.filter(
            QuizAttempt.created_at >= since_date
        ).order_by(QuizAttempt.created_at).all()
        
        if not attempts:
            return jsonify({'message': 'No attempts in specified period'}), 200
        
        # Group by interval
        trend_data = {}
        
        for attempt in attempts:
            if interval == 'day':
                key = attempt.created_at.date().isoformat()
            elif interval == 'week':
                week_start = attempt.created_at - timedelta(days=attempt.created_at.weekday())
                key = week_start.date().isoformat()
            else:  # month
                key = attempt.created_at.strftime('%Y-%m')
            
            if key not in trend_data:
                trend_data[key] = {'scores': [], 'count': 0}
            
            trend_data[key]['scores'].append(attempt.score_percentage)
            trend_data[key]['count'] += 1
        
        # Calculate averages
        result = [
            {
                'period': key,
                'average_score': round(sum(data['scores']) / len(data['scores']), 2),
                'attempts': data['count']
            }
            for key, data in sorted(trend_data.items())
        ]
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
