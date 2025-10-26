"""
Quiz Attempt Repository
Handles all database operations for QuizAttempt entities
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from models import db, QuizAttempt
from .base_repository import BaseRepository


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    """
    Repository for QuizAttempt database operations
    Implements Repository Pattern for data access abstraction
    """
    
    def __init__(self):
        super().__init__(QuizAttempt)
    
    def create_attempt(
        self,
        session_id: str,
        quiz_mode: str,
        total_questions: int,
        correct_answers: int,
        answers: list,
        topic_id: Optional[str] = None,
        subtopic_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> QuizAttempt:
        """
        Create a new quiz attempt
        
        Args:
            session_id: Associated session ID
            quiz_mode: Mode of quiz
            total_questions: Total number of questions
            correct_answers: Number of correct answers
            answers: List of answer details
            topic_id: Topic identifier (optional)
            subtopic_id: Subtopic identifier (optional)
            difficulty: Difficulty level (optional)
            user_name: Name of quiz taker (optional)
            
        Returns:
            Created QuizAttempt instance
        """
        attempt = QuizAttempt(
            session_id=session_id,
            quiz_mode=quiz_mode,
            total_questions=total_questions,
            correct_answers=correct_answers,
            answers=answers,
            topic_id=topic_id,
            subtopic_id=subtopic_id,
            difficulty=difficulty,
            user_name=user_name
        )
        db.session.add(attempt)
        db.session.commit()
        return attempt
    
    def get_recent_attempts(self, limit: int = 10, days: Optional[int] = None) -> List[QuizAttempt]:
        """
        Get recent quiz attempts
        
        Args:
            limit: Maximum number of attempts
            days: Include attempts from last N days
            
        Returns:
            List of recent attempts
        """
        query = QuizAttempt.query.order_by(desc(QuizAttempt.created_at))
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(QuizAttempt.created_at >= cutoff_date)
        
        return query.limit(limit).all()
    
    def get_attempts_by_mode(self, mode: str) -> List[QuizAttempt]:
        """
        Get attempts by quiz mode
        
        Args:
            mode: Quiz mode filter
            
        Returns:
            List of attempts
        """
        return self.filter_by(quiz_mode=mode)
    
    def get_attempts_by_difficulty(self, difficulty: str) -> List[QuizAttempt]:
        """
        Get attempts by difficulty
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            List of attempts
        """
        return self.filter_by(difficulty=difficulty)
    
    def get_attempts_by_topic(self, topic_id: str) -> List[QuizAttempt]:
        """
        Get attempts for a specific topic
        
        Args:
            topic_id: Topic identifier
            
        Returns:
            List of attempts
        """
        return self.filter_by(topic_id=topic_id)
    
    def get_attempts_by_user(self, user_name: str) -> List[QuizAttempt]:
        """
        Get all attempts by a user
        
        Args:
            user_name: Name of the user
            
        Returns:
            List of user's attempts
        """
        return self.filter_by(user_name=user_name)
    
    def get_average_score(self) -> float:
        """
        Calculate average score across all attempts
        
        Returns:
            Average score percentage
        """
        avg = db.session.query(func.avg(QuizAttempt.score_percentage)).scalar()
        return float(avg) if avg else 0.0
    
    def get_average_score_by_mode(self, mode: str) -> float:
        """
        Calculate average score for a specific mode
        
        Args:
            mode: Quiz mode
            
        Returns:
            Average score percentage
        """
        avg = db.session.query(func.avg(QuizAttempt.score_percentage)).filter_by(
            quiz_mode=mode
        ).scalar()
        return float(avg) if avg else 0.0
    
    def get_statistics_by_mode(self) -> Dict[str, Dict]:
        """
        Get comprehensive statistics grouped by mode
        
        Returns:
            Dictionary with statistics per mode
        """
        results = db.session.query(
            QuizAttempt.quiz_mode,
            func.count(QuizAttempt.id).label('count'),
            func.avg(QuizAttempt.score_percentage).label('avg_score'),
            func.min(QuizAttempt.score_percentage).label('min_score'),
            func.max(QuizAttempt.score_percentage).label('max_score')
        ).group_by(QuizAttempt.quiz_mode).all()
        
        stats = {}
        for row in results:
            stats[row.quiz_mode] = {
                'count': row.count,
                'average_score': float(row.avg_score) if row.avg_score else 0.0,
                'min_score': float(row.min_score) if row.min_score else 0.0,
                'max_score': float(row.max_score) if row.max_score else 0.0
            }
        
        return stats
    
    def get_statistics_by_difficulty(self) -> Dict[str, Dict]:
        """
        Get comprehensive statistics grouped by difficulty
        
        Returns:
            Dictionary with statistics per difficulty level
        """
        results = db.session.query(
            QuizAttempt.difficulty,
            func.count(QuizAttempt.id).label('count'),
            func.avg(QuizAttempt.score_percentage).label('avg_score'),
            func.min(QuizAttempt.score_percentage).label('min_score'),
            func.max(QuizAttempt.score_percentage).label('max_score')
        ).filter(QuizAttempt.difficulty.isnot(None)).group_by(
            QuizAttempt.difficulty
        ).all()
        
        stats = {}
        for row in results:
            stats[row.difficulty] = {
                'count': row.count,
                'average_score': float(row.avg_score) if row.avg_score else 0.0,
                'min_score': float(row.min_score) if row.min_score else 0.0,
                'max_score': float(row.max_score) if row.max_score else 0.0
            }
        
        return stats
    
    def get_statistics_by_topic(self) -> Dict[str, Dict]:
        """
        Get comprehensive statistics grouped by topic
        
        Returns:
            Dictionary with statistics per topic
        """
        results = db.session.query(
            QuizAttempt.topic_id,
            func.count(QuizAttempt.id).label('count'),
            func.avg(QuizAttempt.score_percentage).label('avg_score')
        ).filter(QuizAttempt.topic_id.isnot(None)).group_by(
            QuizAttempt.topic_id
        ).all()
        
        stats = {}
        for row in results:
            if row.topic_id:
                stats[row.topic_id] = {
                    'count': row.count,
                    'average_score': float(row.avg_score) if row.avg_score else 0.0
                }
        
        return stats
    
    def delete_sample_attempts(self) -> int:
        """
        Delete all sample data attempts
        
        Returns:
            Number of attempts deleted
        """
        count = QuizAttempt.query.filter(
            QuizAttempt.session_id.like('sample-%')
        ).delete(synchronize_session=False)
        db.session.commit()
        return count
