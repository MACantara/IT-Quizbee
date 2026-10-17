"""
Quiz Session Repository
Stores the active quiz session in the user's Flask session (server-side
filesystem sessions, already configured). Sessions expire with the
browser session, so no sweeping is needed.
"""

from typing import Optional
from flask import session as flask_session
from models import QuizSession

SESSION_KEY = 'quiz_session'


class QuizSessionRepository:
    """
    Repository for quiz session operations backed by flask.session.
    There is at most one active quiz session per browser session.
    """

    def create_session(
        self,
        quiz_type: str,
        questions: list = None,
        topic: str = None,
        subtopic: str = None,
        difficulty: str = None,
        user_name: str = None,
        time_limit: int = None,
        ttl_seconds: int = 7200,
        **kwargs
    ) -> QuizSession:
        """
        Create a new quiz session (replaces any current one)

        Returns:
            Created QuizSession instance
        """
        quiz_session = QuizSession(
            quiz_type=quiz_type,
            questions=questions or [],
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            user_name=user_name,
            time_limit=time_limit,
            ttl_seconds=ttl_seconds,
            **kwargs
        )
        flask_session[SESSION_KEY] = quiz_session.to_dict()
        return quiz_session

    def get_current(self) -> Optional[QuizSession]:
        """Return the current browser's quiz session, or None"""
        data = flask_session.get(SESSION_KEY)
        return QuizSession.from_dict(data) if data else None

    def get_by_id(self, id: str) -> Optional[QuizSession]:
        """Return the current quiz session if its ID matches"""
        quiz_session = self.get_current()
        if quiz_session and quiz_session.id == id:
            return quiz_session
        return None

    def mark_completed(self, session_id: str) -> Optional[QuizSession]:
        """
        Mark session as completed

        Returns:
            Updated session or None
        """
        quiz_session = self.get_by_id(session_id)
        if quiz_session:
            quiz_session.mark_completed()
            flask_session[SESSION_KEY] = quiz_session.to_dict()
        return quiz_session

    def delete_by_id(self, id: str) -> bool:
        """Remove the current quiz session if its ID matches"""
        quiz_session = self.get_current()
        if quiz_session and quiz_session.id == id:
            flask_session.pop(SESSION_KEY, None)
            return True
        return False

    def delete(self, entity: QuizSession) -> bool:
        """Remove the given quiz session"""
        return self.delete_by_id(entity.id)

    def exists(self, id: str) -> bool:
        """Check if the current quiz session has the given ID"""
        return self.get_by_id(id) is not None
