"""
Database models for IT-Quizbee using Flask-SQLAlchemy
Stores quiz sessions and results in MySQL
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text
import json
import uuid

db = SQLAlchemy()


class QuizSession(db.Model):
    """
    Stores active quiz sessions (elimination and finals modes)
    Replaces Flask session storage with database storage
    """
    __tablename__ = 'quiz_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_type = db.Column(db.String(20), nullable=False)  # 'elimination' or 'finals'
    questions_json = db.Column(Text, nullable=False)  # JSON string of questions
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    
    # Relationships
    attempts = db.relationship('QuizAttempt', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, session_type, questions, ttl_seconds=7200):
        """
        Initialize a new quiz session
        
        Args:
            session_type: 'elimination' or 'finals'
            questions: List of question dictionaries
            ttl_seconds: Time-to-live for session (default: 2 hours)
        """
        self.id = str(uuid.uuid4())
        self.session_type = session_type
        self.questions_json = json.dumps(questions, ensure_ascii=False)
        self.created_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self.completed = False
    
    def get_questions(self):
        """Retrieve questions from JSON storage"""
        return json.loads(self.questions_json)
    
    def is_expired(self):
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def mark_completed(self):
        """Mark session as completed"""
        self.completed = True
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_type': self.session_type,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'completed': self.completed,
            'question_count': len(self.get_questions())
        }


class QuizAttempt(db.Model):
    """
    Stores individual quiz submission results
    Used for analytics and result tracking
    """
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('quiz_sessions.id'), nullable=False)
    
    # Quiz metadata
    user_name = db.Column(db.String(100))  # Name of the quiz taker
    topic_id = db.Column(db.String(100))
    subtopic_id = db.Column(db.String(100))
    quiz_mode = db.Column(db.String(20))  # 'elimination', 'finals', 'review'
    difficulty = db.Column(db.String(20))  # 'easy', 'average', 'difficult' (for finals)
    
    # Results
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    score_percentage = db.Column(db.Float, nullable=False)
    
    # Detailed answers
    answers_json = db.Column(Text, nullable=False)  # JSON string of answer details
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __init__(self, session_id, quiz_mode, total_questions, correct_answers, answers, 
                 topic_id=None, subtopic_id=None, difficulty=None, user_name=None):
        """
        Initialize a new quiz attempt result
        
        Args:
            session_id: ID of the quiz session
            quiz_mode: 'elimination', 'finals', or 'review'
            total_questions: Total number of questions
            correct_answers: Number of correct answers
            answers: List of answer details (with questions, user answers, correct answers, etc.)
            topic_id: Topic ID (optional, for review mode)
            subtopic_id: Subtopic ID (optional, for review mode)
            difficulty: Difficulty level (optional, for finals mode)
            user_name: Name of the quiz taker (optional)
        """
        self.id = str(uuid.uuid4())
        self.session_id = session_id
        self.quiz_mode = quiz_mode
        self.user_name = user_name
        self.topic_id = topic_id
        self.subtopic_id = subtopic_id
        self.difficulty = difficulty
        self.total_questions = total_questions
        self.correct_answers = correct_answers
        self.score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        self.answers_json = json.dumps(answers, ensure_ascii=False)
        self.created_at = datetime.utcnow()
        self.completed_at = datetime.utcnow()
    
    def get_answers(self):
        """Retrieve answer details from JSON storage"""
        return json.loads(self.answers_json)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'quiz_mode': self.quiz_mode,
            'user_name': self.user_name,
            'topic_id': self.topic_id,
            'subtopic_id': self.subtopic_id,
            'difficulty': self.difficulty,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'score_percentage': round(self.score_percentage, 2),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat()
        }


def init_db(app):
    """
    Initialize database with Flask app
    Creates tables if they don't exist
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        db.create_all()