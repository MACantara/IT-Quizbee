"""
Domain entities for IT-Quizbee
Quiz sessions live in the user's Flask session; attempts and reports are
persisted as JSON files (see app/repositories/json_store.py).

Models:
    - QuizSession: Active quiz sessions with metadata (topic, difficulty, user)
    - QuizAttempt: Quiz submission results with scoring and analytics data
    - QuestionReport: User-reported question issues for admin review
"""

from datetime import datetime, timedelta
import json
import uuid


def _parse_dt(value):
    """Parse an ISO timestamp, pass through datetimes and None."""
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


class QuizSession:
    """
    An active quiz session (elimination or finals).
    Serialized into the user's Flask session by QuizSessionRepository.
    """

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
        self.questions = questions or []
        self.topic = topic
        self.subtopic = subtopic
        self.difficulty = difficulty
        self.user_name = user_name
        self.time_limit = time_limit
        self.created_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self.completed = False
        self.completed_at = None

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def questions_json(self):
        """Questions as a JSON string (kept for existing callers)."""
        return json.dumps(self.questions, ensure_ascii=False)

    def get_questions(self):
        """Retrieve questions"""
        return self.questions or []

    def is_expired(self):
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at

    def get_time_remaining(self):
        """Seconds until expiry (0 if already expired)"""
        remaining = (self.expires_at - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))

    def mark_completed(self):
        """Mark session as completed"""
        self.completed = True
        self.completed_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary (serializable into Flask session)"""
        return {
            'id': self.id,
            'quiz_type': self.quiz_type,
            'questions': self.questions,
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

    @classmethod
    def from_dict(cls, data):
        """Rebuild a QuizSession from its serialized dictionary"""
        session = cls(
            quiz_type=data.get('quiz_type'),
            questions=data.get('questions', []),
            topic=data.get('topic'),
            subtopic=data.get('subtopic'),
            difficulty=data.get('difficulty'),
            user_name=data.get('user_name'),
            time_limit=data.get('time_limit')
        )
        session.id = data.get('id', session.id)
        session.created_at = _parse_dt(data.get('created_at')) or session.created_at
        session.expires_at = _parse_dt(data.get('expires_at')) or session.expires_at
        session.completed_at = _parse_dt(data.get('completed_at'))
        session.completed = data.get('completed', False)
        return session


class QuizAttempt:
    """
    A quiz submission result, persisted to the attempts JSON store.
    Used for analytics and result tracking.
    """

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
        self.answers = answers
        self.created_at = datetime.utcnow()
        self.completed_at = datetime.utcnow()

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def total_questions(self):
        """Calculate total questions from correct and incorrect counts"""
        return self.correct_count + self.incorrect_count

    @property
    def answers_json(self):
        """Answers as a JSON string (kept for existing callers)."""
        return json.dumps(self.answers, ensure_ascii=False) if self.answers else None

    def get_answers(self):
        """Retrieve answer details"""
        return self.answers or []

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
            'answers': self.answers,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a QuizAttempt from its serialized dictionary"""
        attempt = cls(
            session_id=data.get('session_id'),
            quiz_type=data.get('quiz_type'),
            score=data.get('score', 0),
            correct_count=data.get('correct_count', 0),
            incorrect_count=data.get('incorrect_count', 0),
            topic=data.get('topic'),
            subtopic=data.get('subtopic'),
            difficulty=data.get('difficulty'),
            user_name=data.get('user_name'),
            time_taken=data.get('time_taken'),
            answers=data.get('answers')
        )
        attempt.id = data.get('id', attempt.id)
        attempt.created_at = _parse_dt(data.get('created_at')) or attempt.created_at
        attempt.completed_at = _parse_dt(data.get('completed_at'))
        return attempt


class QuestionReport:
    """
    A user-reported question issue, persisted to the reports JSON store.
    Helps identify problematic questions and track feedback.
    """

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
        self.question_data = question_data
        self.status = 'pending'
        self.admin_notes = None
        self.reviewed_by = None
        self.reviewed_at = None
        self.created_at = datetime.utcnow()

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_question_data(self):
        """Retrieve question data"""
        return self.question_data or {}

    @property
    def question_data_json(self):
        """Question data as a JSON string (kept for existing callers)."""
        return json.dumps(self.question_data, ensure_ascii=False) if self.question_data else None

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
            'question_data': self.question_data,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a QuestionReport from its serialized dictionary"""
        report = cls(
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
        report.id = data.get('id', report.id)
        report.status = data.get('status', 'pending')
        report.admin_notes = data.get('admin_notes')
        report.reviewed_by = data.get('reviewed_by')
        report.reviewed_at = _parse_dt(data.get('reviewed_at'))
        report.created_at = _parse_dt(data.get('created_at')) or report.created_at
        return report
