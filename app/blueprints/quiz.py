"""
Quiz Blueprint
Handles quiz-related routes (elimination, finals, submission)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.services import QuizService
from app.repositories import QuizSessionRepository, QuizAttemptRepository
from app.decorators.logging import log_request, monitor_performance
from app.decorators.rate_limit import per_user_rate_limit
from app.utils import handle_error, error_response, success_response, NotFoundError, ValidationError
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
                            100,  # Load many to sample from
                            mode='elimination',
                            difficulty='medium'
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
        session['quiz_topic'] = topic
        session['quiz_subtopic'] = subtopic
        session['quiz_difficulty'] = difficulty
        
        return render_template(
            'quiz/elimination_mode.html',
            questions=questions,
            mode='elimination',
            topic=topic,
            subtopic=subtopic
        )
    except ValueError as e:
        return handle_error(e, "Error creating elimination quiz")
    except Exception as e:
        return handle_error(e, "An unexpected error occurred")


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
                    # Load questions from each difficulty level
                    for diff in ['easy', 'average', 'difficult']:
                        try:
                            questions = service.load_questions(
                                topic_name, 
                                subtopic_data['id'], 
                                20,  # Load some from each difficulty
                                mode='finals',
                                difficulty=diff
                            )
                            # Tag with difficulty
                            for q in questions:
                                q['difficulty'] = diff
                            all_questions.extend(questions)
                        except (ValueError, FileNotFoundError):
                            # Skip if questions file doesn't exist
                            continue
            
            # Randomly sample 30 questions (10 from each difficulty if possible)
            import random
            easy_qs = [q for q in all_questions if q.get('difficulty') == 'easy']
            avg_qs = [q for q in all_questions if q.get('difficulty') == 'average']
            diff_qs = [q for q in all_questions if q.get('difficulty') == 'difficult']
            
            questions = []
            questions.extend(random.sample(easy_qs, min(10, len(easy_qs))))
            questions.extend(random.sample(avg_qs, min(10, len(avg_qs))))
            questions.extend(random.sample(diff_qs, min(10, len(diff_qs))))
            
            # If we don't have enough, fill from all questions
            if len(questions) < num_questions:
                remaining = [q for q in all_questions if q not in questions]
                questions.extend(random.sample(remaining, min(num_questions - len(questions), len(remaining))))
            
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
        session['quiz_topic'] = topic
        session['quiz_subtopic'] = subtopic
        session['quiz_difficulty'] = difficulty
        
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
        return handle_error(e, "Error creating finals quiz")
    except Exception as e:
        return handle_error(e, "An unexpected error occurred")


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
        raise NotFoundError('No active quiz session found.')
    
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
        
        # Store quiz metadata for results page
        session['last_quiz_topic'] = session.get('quiz_topic')
        session['last_quiz_subtopic'] = session.get('quiz_subtopic')
        session['last_quiz_difficulty'] = session.get('quiz_difficulty')
        session['last_quiz_mode'] = quiz_type
        
        # Clear quiz session
        session.pop('quiz_session_id', None)
        session.pop('quiz_type', None)
        session.pop('quiz_start_time', None)
        session.pop('quiz_topic', None)
        session.pop('quiz_subtopic', None)
        session.pop('quiz_difficulty', None)
        
        return redirect(url_for('quiz.results'))
        
    except (ValueError, NotFoundError) as e:
        return handle_error(e, "Error submitting quiz")
    except Exception as e:
        return handle_error(e, "An unexpected error occurred")


@quiz_bp.route('/results')
@log_request
def results():
    """Display quiz results"""
    try:
        results = session.get('last_quiz_results')
        
        if not results:
            raise NotFoundError('No quiz results found.')
        
        # Get quiz metadata
        topic = session.get('last_quiz_topic')
        subtopic = session.get('last_quiz_subtopic')
        difficulty = session.get('last_quiz_difficulty', 'medium')
        mode = session.get('last_quiz_mode', 'elimination')
        
        return render_template(
            'quiz/results.html',
            results=results,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            mode=mode
        )
    except NotFoundError as e:
        return handle_error(e, "No quiz results available")
    except Exception as e:
        return handle_error(e, "Error loading results")


@quiz_bp.route('/review/<attempt_id>')
@log_request
def review(attempt_id):
    """Review a completed quiz"""
    try:
        # Get attempt from database
        from models import QuizAttempt, db
        
        attempt = QuizAttempt.query.get(attempt_id)
        
        if not attempt:
            raise NotFoundError('Quiz attempt not found.')
        
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
            except ValueError as e:
                raise NotFoundError('Could not load quiz questions.')
        
        raise NotFoundError('Quiz session not found.')
        
    except NotFoundError as e:
        return handle_error(e, "Quiz attempt not available")
    except Exception as e:
        return handle_error(e, "Error loading quiz review")


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
