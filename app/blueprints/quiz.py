"""
Quiz Blueprint
Handles quiz-related routes (elimination, finals, submission)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.services import QuizService
from app.repositories import QuizSessionRepository, QuizAttemptRepository
from app.decorators.logging import log_request, monitor_performance
from app.decorators.rate_limit import per_user_rate_limit
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

# Service will be initialized with repositories
quiz_service = None


def get_quiz_service():
    """Get or create quiz service instance"""
    global quiz_service
    if quiz_service is None:
        session_repo = QuizSessionRepository()
        attempt_repo = QuizAttemptRepository()
        quiz_service = QuizService(session_repo, attempt_repo)
    return quiz_service


@quiz_bp.route('/elimination', methods=['GET', 'POST'])
@log_request
@monitor_performance
def elimination_mode():
    """Elimination mode quiz"""
    # Get parameters from form (POST) or use defaults for full mode (GET)
    if request.method == 'POST':
        topic = request.form.get('topic')
        subtopic = request.form.get('subtopic')
        difficulty = request.form.get('difficulty', 'medium')
        user_name = request.form.get('user_name', '').strip() or 'Anonymous'
        num_questions = 10  # Review mode: 10 questions per subtopic
    else:
        # For GET requests (full elimination mode): 100 questions from all topics
        topic = None
        subtopic = None
        difficulty = 'medium'
        user_name = session.get('user_name', 'Anonymous')
        num_questions = 100
    
    try:
        service = get_quiz_service()
        
        # For full mode, load questions from all topics
        if topic is None:
            # Load questions from all topics/subtopics
            all_questions = []
            topics = service.get_available_topics()
            
            for topic_data in topics:
                topic_name = topic_data['topic_id']
                subtopics = service.get_subtopics(topic_name)
                
                for subtopic_data in subtopics:
                    try:
                        questions = service.load_questions(
                            topic_name, 
                            subtopic_data['id'], 
                            100  # Load many to sample from
                        )
                        all_questions.extend(questions)
                    except (ValueError, FileNotFoundError):
                        # Skip if questions file doesn't exist
                        continue
            
            # Randomly sample 100 questions
            import random
            questions = random.sample(all_questions, min(num_questions, len(all_questions)))
            
            # Create session with aggregated questions
            session_id = service.session_repo.create_session(
                session_type='elimination',
                questions=questions
            ).id
        else:
            # Review mode: use service method
            session_id, questions = service.create_elimination_quiz(
                topic, subtopic, difficulty, user_name
            )
        
        # Store in session
        session['quiz_session_id'] = session_id
        session['quiz_type'] = 'elimination'
        session['quiz_start_time'] = datetime.now().isoformat()
        
        return render_template(
            'quiz/elimination_mode.html',
            questions=questions,
            mode='elimination',
            topic=topic,
            subtopic=subtopic
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('navigation.topics'))


@quiz_bp.route('/finals', methods=['GET', 'POST'])
@log_request
@monitor_performance
def finals_mode():
    """Finals mode quiz"""
    # Get parameters from form (POST) or use defaults for full mode (GET)
    if request.method == 'POST':
        topic = request.form.get('topic')
        subtopic = request.form.get('subtopic')
        difficulty = request.form.get('difficulty', 'hard')
        user_name = request.form.get('user_name', '').strip() or 'Anonymous'
        num_questions = 10  # Review mode: 10 questions per subtopic
    else:
        # For GET requests (full finals mode): 30 questions from all topics
        topic = None
        subtopic = None
        difficulty = 'mixed'  # Mix of easy, average, and difficult
        user_name = session.get('user_name', 'Anonymous')
        num_questions = 30
    
    try:
        service = get_quiz_service()
        
        # For full mode, load questions from all topics
        if topic is None:
            # Load questions from all topics/subtopics
            all_questions = []
            topics = service.get_available_topics()
            
            for topic_data in topics:
                topic_name = topic_data['topic_id']
                subtopics = service.get_subtopics(topic_name)
                
                for subtopic_data in subtopics:
                    try:
                        questions = service.load_questions(
                            topic_name, 
                            subtopic_data['id'], 
                            50  # Load many to sample from
                        )
                        all_questions.extend(questions)
                    except (ValueError, FileNotFoundError):
                        # Skip if questions file doesn't exist
                        continue
            
            # Randomly sample 30 questions
            import random
            questions = random.sample(all_questions, min(num_questions, len(all_questions)))
            
            # Assign mixed difficulties (10 easy, 10 average, 10 difficult)
            for i, q in enumerate(questions):
                if i < 10:
                    q['difficulty'] = 'easy'
                elif i < 20:
                    q['difficulty'] = 'average'
                else:
                    q['difficulty'] = 'difficult'
            
            # Create session with aggregated questions
            session_id = service.session_repo.create_session(
                session_type='finals',
                questions=questions
            ).id
        else:
            # Review mode: use service method
            session_id, questions = service.create_finals_quiz(
                topic, subtopic, difficulty, user_name
            )
        
        # Store in session
        session['quiz_session_id'] = session_id
        session['quiz_type'] = 'finals'
        session['quiz_start_time'] = datetime.now().isoformat()
        
        # Convert questions to JSON for JavaScript
        import json
        questions_json = json.dumps([{
            'id': q.get('id'),
            'question': q.get('question'),
            'correct_answer': q.get('correct_answer'),
            'difficulty': q.get('difficulty', 'average'),
            'topic': q.get('topic_name', ''),
            'subtopic': q.get('subtopic_name', '')
        } for q in questions])
        
        return render_template(
            'quiz/finals_mode.html',
            questions=questions,
            questions_json=questions_json,
            mode='finals',
            topic=topic,
            subtopic=subtopic
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('navigation.topics'))


@quiz_bp.route('/submit', methods=['POST'])
@per_user_rate_limit(max_requests=10, window_seconds=60)
@log_request
@monitor_performance
def submit_quiz():
    """Submit quiz answers"""
    session_id = session.get('quiz_session_id')
    quiz_type = session.get('quiz_type')
    start_time_str = session.get('quiz_start_time')
    
    if not session_id:
        flash('No active quiz session found.', 'error')
        return redirect(url_for('navigation.topics'))
    
    # Get user name from session or form
    user_name = session.get('user_name', 'Anonymous')
    
    # Calculate time taken
    time_taken = None
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        time_taken = int((datetime.now() - start_time).total_seconds())
    
    # Get answers from form
    answers = {}
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            answers[question_id] = value
    
    try:
        service = get_quiz_service()
        result = service.submit_quiz(
            session_id,
            answers,
            user_name,
            time_taken
        )
        
        # Store results in session
        session['last_quiz_results'] = result
        session['last_attempt_id'] = result['attempt_id']
        
        # Clear quiz session
        session.pop('quiz_session_id', None)
        session.pop('quiz_type', None)
        session.pop('quiz_start_time', None)
        
        return redirect(url_for('quiz.results'))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('navigation.topics'))


@quiz_bp.route('/results')
@log_request
def results():
    """Display quiz results"""
    results = session.get('last_quiz_results')
    
    if not results:
        flash('No quiz results found.', 'warning')
        return redirect(url_for('navigation.topics'))
    
    return render_template('quiz/results.html', results=results)


@quiz_bp.route('/review/<attempt_id>')
@log_request
def review(attempt_id):
    """Review a completed quiz"""
    # Get attempt from database
    from models import QuizAttempt, db
    
    attempt = QuizAttempt.query.get(attempt_id)
    
    if not attempt:
        flash('Quiz attempt not found.', 'error')
        return redirect(url_for('navigation.topics'))
    
    # Get session to retrieve questions
    if attempt.session_id:
        service = get_quiz_service()
        try:
            questions = service.get_session_questions(attempt.session_id)
            
            # Reconstruct results (simplified version)
            results = {
                'score': attempt.score,
                'correct_count': attempt.correct_count,
                'incorrect_count': attempt.incorrect_count,
                'total_questions': attempt.correct_count + attempt.incorrect_count,
                'passed': attempt.score >= 70,
                'results': questions  # Note: This won't have user answers
            }
            
            return render_template('quiz/results.html', results=results, review_mode=True)
        except ValueError:
            flash('Could not load quiz questions.', 'error')
    
    return redirect(url_for('navigation.topics'))


@quiz_bp.route('/validate-session', methods=['POST'])
def validate_session():
    """API endpoint to validate quiz session"""
    session_id = request.json.get('session_id')
    
    if not session_id:
        return jsonify({'valid': False, 'error': 'No session ID provided'}), 400
    
    try:
        service = get_quiz_service()
        is_valid, error = service.validate_session(session_id)
        
        return jsonify({
            'valid': is_valid,
            'error': error
        })
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500


@quiz_bp.route('/cleanup-expired', methods=['POST'])
def cleanup_expired():
    """API endpoint to cleanup expired sessions (admin only)"""
    # This should be protected with admin authentication
    # For now, it's a maintenance endpoint
    
    try:
        service = get_quiz_service()
        count = service.cleanup_expired_sessions()
        
        return jsonify({
            'success': True,
            'cleaned_up': count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
