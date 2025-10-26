"""
Navigation Blueprint
Handles topic browsing and mode selection routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services import QuizService
from app.repositories import QuizSessionRepository, QuizAttemptRepository
from app.decorators.logging import log_request

navigation_bp = Blueprint('navigation', __name__)

# Service will be initialized with repositories
quiz_service = None


def get_quiz_service():
    """Get or create quiz service instance"""
    global quiz_service
    if quiz_service is None:
        from models import db
        session_repo = QuizSessionRepository(db.session)
        attempt_repo = QuizAttemptRepository(db.session)
        quiz_service = QuizService(session_repo, attempt_repo)
    return quiz_service


@navigation_bp.route('/')
@log_request
def index():
    """Landing page"""
    return render_template('index.html')


@navigation_bp.route('/topics')
@log_request
def topics():
    """Display available topics"""
    try:
        service = get_quiz_service()
        topics_list = service.get_available_topics()
        
        return render_template(
            'navigation/topics.html',
            topics=topics_list
        )
    except Exception as e:
        flash(f'Error loading topics: {str(e)}', 'error')
        return redirect(url_for('navigation.index'))


@navigation_bp.route('/topics/<topic>/subtopics')
@log_request
def subtopics(topic):
    """Display subtopics for a topic"""
    try:
        service = get_quiz_service()
        subtopics_list = service.get_subtopics(topic)
        
        # Get topic title from first item or use topic name
        topic_title = topic.replace('_', ' ').title()
        
        return render_template(
            'navigation/subtopics.html',
            topic=topic,
            topic_title=topic_title,
            subtopics=subtopics_list
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('navigation.topics'))
    except Exception as e:
        flash(f'Error loading subtopics: {str(e)}', 'error')
        return redirect(url_for('navigation.topics'))


@navigation_bp.route('/mode-selection')
@log_request
def mode_selection():
    """Mode selection page"""
    # Get topic and subtopic from query params
    topic = request.args.get('topic')
    subtopic = request.args.get('subtopic')
    
    if not topic or not subtopic:
        flash('Please select a topic and subtopic first.', 'warning')
        return redirect(url_for('navigation.topics'))
    
    # Store in session
    session['selected_topic'] = topic
    session['selected_subtopic'] = subtopic
    
    return render_template(
        'quiz/mode_selection.html',
        topic=topic,
        subtopic=subtopic
    )


@navigation_bp.route('/set-user-name', methods=['POST'])
def set_user_name():
    """Set user name in session"""
    user_name = request.form.get('user_name', '').strip()
    
    if user_name:
        session['user_name'] = user_name
        flash(f'Welcome, {user_name}!', 'success')
    
    # Redirect to previous page or topics
    next_page = request.form.get('next', url_for('navigation.topics'))
    return redirect(next_page)


@navigation_bp.route('/clear-session', methods=['POST'])
def clear_session():
    """Clear user session"""
    # Keep admin session if exists
    is_admin = session.get('is_admin')
    admin_username = session.get('admin_username')
    login_time = session.get('login_time')
    session_token = session.get('session_token')
    
    # Clear all session data
    session.clear()
    
    # Restore admin session
    if is_admin:
        session['is_admin'] = is_admin
        session['admin_username'] = admin_username
        session['login_time'] = login_time
        session['session_token'] = session_token
    
    flash('Session cleared.', 'info')
    return redirect(url_for('navigation.index'))


@navigation_bp.route('/about')
@log_request
def about():
    """About page"""
    return render_template('about.html')


@navigation_bp.route('/help')
@log_request
def help():
    """Help/FAQ page"""
    return render_template('help.html')
