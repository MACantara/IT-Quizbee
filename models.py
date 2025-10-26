"""
Database models for IT-Quizbee using Flask-SQLAlchemy
Stores quiz sessions and results in MySQL

Models:
    - QuizSession: Active quiz sessions with metadata (topic, difficulty, user)
    - QuizAttempt: Quiz submission results with scoring and analytics data

Updated to support the new repository pattern and service layer architecture.
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
    quiz_type = db.Column(db.String(20), nullable=False)  # 'elimination' or 'finals'
    questions_json = db.Column(Text, nullable=False)  # JSON string of questions
    
    # Quiz metadata
    topic = db.Column(db.String(100))  # Topic name
    subtopic = db.Column(db.String(100))  # Subtopic name
    difficulty = db.Column(db.String(20))  # Difficulty level: 'easy', 'average', 'difficult'
    user_name = db.Column(db.String(100))  # Name of the quiz taker
    time_limit = db.Column(db.Integer)  # Time limit in seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)  # When quiz was completed
    
    # Status
    completed = db.Column(db.Boolean, default=False)
    
    # Relationships
    attempts = db.relationship('QuizAttempt', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, quiz_type, questions, topic=None, subtopic=None, difficulty=None, 
                 user_name=None, time_limit=None, ttl_seconds=7200, **kwargs):
        """
        Initialize a new quiz session
        
        Args:
            quiz_type: 'elimination' or 'finals'
            questions: List of question dictionaries
            topic: Topic name (optional)
            subtopic: Subtopic name (optional)
            difficulty: Difficulty level (optional)
            user_name: Name of the quiz taker (optional)
            time_limit: Time limit in seconds (optional)
            ttl_seconds: Time-to-live for session (default: 2 hours)
            **kwargs: Additional fields for flexibility
        """
        self.id = str(uuid.uuid4())
        self.quiz_type = quiz_type
        self.questions_json = json.dumps(questions, ensure_ascii=False)
        self.topic = topic
        self.subtopic = subtopic
        self.difficulty = difficulty
        self.user_name = user_name
        self.time_limit = time_limit
        self.created_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self.completed = False
        self.completed_at = None
        
        # Set any additional keyword arguments
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_questions(self):
        """Retrieve questions from JSON storage"""
        return json.loads(self.questions_json) if self.questions_json else []
    
    def is_expired(self):
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def mark_completed(self):
        """Mark session as completed"""
        self.completed = True
        self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'quiz_type': self.quiz_type,
            'topic': self.topic,
            'subtopic': self.subtopic,
            'difficulty': self.difficulty,
            'user_name': self.user_name,
            'time_limit': self.time_limit,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
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
    quiz_type = db.Column(db.String(50))  # 'elimination', 'finals', 'review'
    topic = db.Column(db.String(100))  # Topic name
    subtopic = db.Column(db.String(100))  # Subtopic name
    difficulty = db.Column(db.String(20))  # 'easy', 'average', 'difficult'
    user_name = db.Column(db.String(100))  # Name of the quiz taker
    
    # Results
    score = db.Column(db.Float, nullable=False)  # Score as percentage (0-100)
    correct_count = db.Column(db.Integer, nullable=False)  # Number of correct answers
    incorrect_count = db.Column(db.Integer, nullable=False)  # Number of incorrect answers
    time_taken = db.Column(db.Integer)  # Time taken in seconds
    
    # Detailed answers (optional, for review functionality)
    answers_json = db.Column(Text)  # JSON string of answer details
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __init__(self, session_id, quiz_type, score, correct_count, incorrect_count,
                 topic=None, subtopic=None, difficulty=None, user_name=None, 
                 time_taken=None, answers=None, **kwargs):
        """
        Initialize a new quiz attempt result
        
        Args:
            session_id: ID of the quiz session
            quiz_type: 'elimination', 'finals', or 'review'
            score: Score as percentage (0-100)
            correct_count: Number of correct answers
            incorrect_count: Number of incorrect answers
            topic: Topic name (optional)
            subtopic: Subtopic name (optional)
            difficulty: Difficulty level (optional)
            user_name: Name of the quiz taker (optional)
            time_taken: Time taken in seconds (optional)
            answers: List of answer details (optional, for review)
            **kwargs: Additional fields for flexibility
        """
        self.id = str(uuid.uuid4())
        self.session_id = session_id
        self.quiz_type = quiz_type
        self.topic = topic
        self.subtopic = subtopic
        self.difficulty = difficulty
        self.user_name = user_name
        self.score = score
        self.correct_count = correct_count
        self.incorrect_count = incorrect_count
        self.time_taken = time_taken
        self.answers_json = json.dumps(answers, ensure_ascii=False) if answers else None
        self.created_at = datetime.utcnow()
        self.completed_at = datetime.utcnow()
        
        # Set any additional keyword arguments
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def total_questions(self):
        """Calculate total questions from correct and incorrect counts"""
        return self.correct_count + self.incorrect_count
    
    @property
    def score_percentage(self):
        """Alias for score field for backward compatibility"""
        return self.score
    
    def get_answers(self):
        """Retrieve answer details from JSON storage"""
        return json.loads(self.answers_json) if self.answers_json else []
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'quiz_type': self.quiz_type,
            'topic': self.topic,
            'subtopic': self.subtopic,
            'difficulty': self.difficulty,
            'user_name': self.user_name,
            'score': round(self.score, 2),
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
            'total_questions': self.total_questions,
            'time_taken': self.time_taken,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
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