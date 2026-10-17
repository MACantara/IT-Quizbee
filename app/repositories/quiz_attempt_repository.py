"""
Quiz Attempt Repository
Handles persistence for QuizAttempt entities via the JSON store
"""

from typing import Optional
from models import QuizAttempt
from .base_repository import BaseRepository


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    """
    Repository for QuizAttempt persistence
    Implements Repository Pattern for data access abstraction
    """

    def __init__(self):
        super().__init__('attempts.json', QuizAttempt)

    def create_attempt(
        self,
        session_id: str,
        quiz_type: str,
        score: float,
        correct_count: int,
        incorrect_count: int,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        difficulty: Optional[str] = None,
        user_name: Optional[str] = None,
        time_taken: Optional[int] = None,
        answers: Optional[list] = None,
        **kwargs
    ) -> QuizAttempt:
        """
        Create a new quiz attempt

        Returns:
            Created QuizAttempt instance
        """
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
        self.store.upsert(attempt.to_dict())
        return attempt

    def delete_sample_attempts(self) -> int:
        """Delete all sample data attempts (session_id starting with 'sample-')"""
        return self.store.delete_where(
            lambda r: str(r.get('session_id', '')).startswith('sample-')
        )
