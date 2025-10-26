"""
Quiz Session Repository
Handles all database operations for QuizSession entities
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc
from models import db, QuizSession
from .base_repository import BaseRepository


class QuizSessionRepository(BaseRepository[QuizSession]):
    """
    Repository for QuizSession database operations
    Implements Repository Pattern for data access abstraction
    """
    
    def __init__(self):
        super().__init__(QuizSession)
    
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
        Create a new quiz session
        
        Args:
            quiz_type: Type of quiz ('elimination' or 'finals')
            questions: List of questions
            topic: Topic name (optional)
            subtopic: Subtopic name (optional)
            difficulty: Difficulty level (optional)
            user_name: Name of quiz taker (optional)
            time_limit: Time limit in seconds (optional)
            ttl_seconds: Time-to-live in seconds
            **kwargs: Additional keyword arguments
            
        Returns:
            Created QuizSession instance
        """
        session = QuizSession(
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
        db.session.add(session)
        db.session.commit()
        return session
    
    def get_active_sessions(self) -> List[QuizSession]:
        """
        Get all active (non-expired) sessions
        
        Returns:
            List of active sessions
        """
        now = datetime.utcnow()
        return QuizSession.query.filter(
            QuizSession.expires_at > now,
            QuizSession.completed == False
        ).all()
    
    def get_expired_sessions(self) -> List[QuizSession]:
        """
        Get all expired sessions
        
        Returns:
            List of expired sessions
        """
        now = datetime.utcnow()
        return QuizSession.query.filter(
            QuizSession.expires_at <= now
        ).all()
    
    def get_completed_sessions(self, limit: Optional[int] = None) -> List[QuizSession]:
        """
        Get completed sessions
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of completed sessions
        """
        query = QuizSession.query.filter_by(completed=True).order_by(desc(QuizSession.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_sessions_by_type(self, quiz_type: str) -> List[QuizSession]:
        """
        Get sessions by type
        
        Args:
            quiz_type: Type of quiz ('elimination' or 'finals')
            
        Returns:
            List of sessions
        """
        return self.filter_by(quiz_type=quiz_type)
    
    def mark_completed(self, session_id: str) -> Optional[QuizSession]:
        """
        Mark session as completed
        
        Args:
            session_id: Session identifier
            
        Returns:
            Updated session or None
        """
        session = self.get_by_id(session_id)
        if session:
            session.mark_completed()
            db.session.commit()
        return session
    
    def cleanup_expired(self) -> int:
        """
        Delete all expired sessions
        
        Returns:
            Number of sessions deleted
        """
        expired = self.get_expired_sessions()
        count = len(expired)
        for session in expired:
            self.delete(session)
        return count
    
    def get_session_with_questions(self, session_id: str) -> Optional[dict]:
        """
        Get session with parsed questions
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with session data and questions
        """
        session = self.get_by_id(session_id)
        if session:
            return {
                'session': session,
                'questions': session.get_questions(),
                'is_expired': session.is_expired(),
                'quiz_type': session.quiz_type
            }
        return None
