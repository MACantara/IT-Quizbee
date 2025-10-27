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


class QuestionReport(db.Model):
    """
    Stores user-reported questions for improvement
    Helps identify problematic questions and track feedback
    """
    __tablename__ = 'question_reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Question identification
    question_id = db.Column(db.String(100), nullable=False)  # ID from question file
    topic = db.Column(db.String(100))  # Topic name
    subtopic = db.Column(db.String(100))  # Subtopic name
    quiz_type = db.Column(db.String(20))  # 'elimination' or 'finals'
    difficulty = db.Column(db.String(20))  # Difficulty level
    
    # Report details
    report_type = db.Column(db.String(50), nullable=False)  # Type of issue
    reason = db.Column(Text)  # Detailed explanation
    user_name = db.Column(db.String(100))  # Reporter name
    
    # Question content (snapshot at time of report)
    question_text = db.Column(Text)  # The actual question
    question_data_json = db.Column(Text)  # Full question data as JSON
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, resolved, dismissed
    admin_notes = db.Column(Text)  # Admin notes on the report
    reviewed_by = db.Column(db.String(100))  # Admin who reviewed
    reviewed_at = db.Column(db.DateTime)  # When reviewed
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __init__(self, question_id, report_type, reason=None, user_name=None,
                 topic=None, subtopic=None, quiz_type=None, difficulty=None,
                 question_text=None, question_data=None, **kwargs):
        """
        Initialize a new question report
        
        Args:
            question_id: ID of the question being reported
            report_type: Type of issue (incorrect_answer, unclear_question, typo, etc.)
            reason: Detailed explanation from user
            user_name: Name of the reporter
            topic: Topic name
            subtopic: Subtopic name
            quiz_type: Type of quiz
            difficulty: Difficulty level
            question_text: The question text
            question_data: Full question data dictionary
            **kwargs: Additional fields
        """
        self.id = str(uuid.uuid4())
        self.question_id = question_id
        self.report_type = report_type
        self.reason = reason
        self.user_name = user_name
        self.topic = topic
        self.subtopic = subtopic
        self.quiz_type = quiz_type
        self.difficulty = difficulty
        self.question_text = question_text
        self.question_data_json = json.dumps(question_data, ensure_ascii=False) if question_data else None
        self.status = 'pending'
        self.created_at = datetime.utcnow()
        
        # Set any additional keyword arguments
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_question_data(self):
        """Retrieve question data from JSON storage"""
        return json.loads(self.question_data_json) if self.question_data_json else {}
    
    def mark_reviewed(self, admin_name, notes=None, status='reviewed'):
        """Mark report as reviewed"""
        self.status = status
        self.reviewed_by = admin_name
        self.reviewed_at = datetime.utcnow()
        if notes:
            self.admin_notes = notes
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'topic': self.topic,
            'subtopic': self.subtopic,
            'quiz_type': self.quiz_type,
            'difficulty': self.difficulty,
            'report_type': self.report_type,
            'reason': self.reason,
            'user_name': self.user_name or 'Anonymous',
            'question_text': self.question_text,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat()
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