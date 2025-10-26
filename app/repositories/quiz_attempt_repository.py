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
        quiz_type: str = None,
        score: float = None,
        correct_count: int = None,
        incorrect_count: int = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        difficulty: Optional[str] = None,
        user_name: Optional[str] = None,
        time_taken: Optional[int] = None,
        answers: Optional[list] = None,
        # Backward compatibility parameters
        quiz_mode: str = None,
        total_questions: int = None,
        correct_answers: int = None,
        topic_id: Optional[str] = None,
        subtopic_id: Optional[str] = None,
        **kwargs
    ) -> QuizAttempt:
        """
        Create a new quiz attempt
        
        Args:
            session_id: Associated session ID
            quiz_type: Type of quiz ('elimination', 'finals', 'review')
            score: Score as percentage (0-100)
            correct_count: Number of correct answers
            incorrect_count: Number of incorrect answers
            topic: Topic name (optional)
            subtopic: Subtopic name (optional)
            difficulty: Difficulty level (optional)
            user_name: Name of quiz taker (optional)
            time_taken: Time taken in seconds (optional)
            answers: List of answer details (optional)
            
            # Backward compatibility:
            quiz_mode: Deprecated, use quiz_type instead
            total_questions: Deprecated, calculated from correct_count + incorrect_count
            correct_answers: Deprecated, use correct_count instead
            topic_id: Deprecated, use topic instead
            subtopic_id: Deprecated, use subtopic instead
            **kwargs: Additional keyword arguments
            
        Returns:
            Created QuizAttempt instance
        """
        # Backward compatibility handling
        if quiz_mode and not quiz_type:
            quiz_type = quiz_mode
        
        if correct_answers is not None and correct_count is None:
            correct_count = correct_answers
        
        if topic_id and not topic:
            topic = topic_id
        
        if subtopic_id and not subtopic:
            subtopic = subtopic_id
        
        # Calculate score and incorrect_count if needed
        if score is None and total_questions and correct_count is not None:
            score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        if incorrect_count is None and total_questions and correct_count is not None:
            incorrect_count = total_questions - correct_count
        
        # Ensure we have required values
        if correct_count is None:
            correct_count = 0
        if incorrect_count is None:
            incorrect_count = 0
        if score is None:
            total = correct_count + incorrect_count
            score = (correct_count / total * 100) if total > 0 else 0
        
        attempt = QuizAttempt(
            session_id=session_id,
            quiz_type=quiz_type,
            score=score,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            user_name=user_name,
            time_taken=time_taken,
            answers=answers,
            **kwargs
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
        Get attempts by quiz mode/type
        
        Args:
            mode: Quiz mode filter
            
        Returns:
            List of attempts
        """
        return self.filter_by(quiz_type=mode)
    
    def get_attempts_by_difficulty(self, difficulty: str) -> List[QuizAttempt]:
        """
        Get attempts by difficulty
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            List of attempts
        """
        return self.filter_by(difficulty=difficulty)
    
    def get_attempts_by_topic(self, topic_id: str = None, topic: str = None) -> List[QuizAttempt]:
        """
        Get attempts for a specific topic
        
        Args:
            topic_id: Deprecated, use topic instead
            topic: Topic name
            
        Returns:
            List of attempts
        """
        # Backward compatibility
        if topic_id and not topic:
            topic = topic_id
        return self.filter_by(topic=topic) if topic else []
    
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
        avg = db.session.query(func.avg(QuizAttempt.score)).scalar()
        return float(avg) if avg else 0.0
    
    def get_average_score_by_mode(self, mode: str) -> float:
        """
        Calculate average score for a specific mode
        
        Args:
            mode: Quiz mode
            
        Returns:
            Average score percentage
        """
        avg = db.session.query(func.avg(QuizAttempt.score)).filter_by(
            quiz_type=mode
        ).scalar()
        return float(avg) if avg else 0.0
    
    def get_statistics_by_mode(self) -> Dict[str, Dict]:
        """
        Get comprehensive statistics grouped by mode
        
        Returns:
            Dictionary with statistics per mode
        """
        results = db.session.query(
            QuizAttempt.quiz_type,
            func.count(QuizAttempt.id).label('count'),
            func.avg(QuizAttempt.score).label('avg_score'),
            func.min(QuizAttempt.score).label('min_score'),
            func.max(QuizAttempt.score).label('max_score')
        ).group_by(QuizAttempt.quiz_type).all()
        
        stats = {}
        for row in results:
            stats[row.quiz_type] = {
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
            func.avg(QuizAttempt.score).label('avg_score'),
            func.min(QuizAttempt.score).label('min_score'),
            func.max(QuizAttempt.score).label('max_score')
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
            QuizAttempt.topic,
            func.count(QuizAttempt.id).label('count'),
            func.avg(QuizAttempt.score).label('avg_score')
        ).filter(QuizAttempt.topic.isnot(None)).group_by(
            QuizAttempt.topic
        ).all()
        
        stats = {}
        for row in results:
            if row.topic:
                stats[row.topic] = {
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
