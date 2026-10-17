"""
Quiz Attempt Repository
Handles persistence for QuizAttempt entities via the JSON store
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
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

    def get_recent_attempts(self, limit: int = 10, days: Optional[int] = None) -> List[QuizAttempt]:
        """
        Get recent quiz attempts, newest first

        Args:
            limit: Maximum number of attempts
            days: Include attempts from last N days
        """
        attempts = sorted(self.get_all(), key=lambda a: a.created_at, reverse=True)

        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            attempts = [a for a in attempts if a.created_at >= cutoff]

        return attempts[:limit]

    def get_attempts_by_mode(self, mode: str) -> List[QuizAttempt]:
        """Get attempts by quiz mode/type"""
        return self.filter_by(quiz_type=mode)

    def get_attempts_by_difficulty(self, difficulty: str) -> List[QuizAttempt]:
        """Get attempts by difficulty"""
        return self.filter_by(difficulty=difficulty)

    def get_attempts_by_topic(self, topic: str) -> List[QuizAttempt]:
        """Get attempts for a specific topic"""
        return self.filter_by(topic=topic) if topic else []

    def get_attempts_by_user(self, user_name: str, days: Optional[int] = None) -> List[QuizAttempt]:
        """
        Get all attempts by a user, oldest first

        Args:
            user_name: Name of the user
            days: Include attempts from last N days (optional)
        """
        attempts = sorted(
            self.filter_by(user_name=user_name),
            key=lambda a: a.created_at
        )
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            attempts = [a for a in attempts if a.created_at >= cutoff]
        return attempts

    def get_average_score(self) -> float:
        """Calculate average score across all attempts"""
        attempts = self.get_all()
        if not attempts:
            return 0.0
        return sum(a.score for a in attempts) / len(attempts)

    def get_average_score_by_mode(self, mode: str) -> float:
        """Calculate average score for a specific mode"""
        attempts = self.get_attempts_by_mode(mode)
        if not attempts:
            return 0.0
        return sum(a.score for a in attempts) / len(attempts)

    def get_statistics_by_mode(self) -> Dict[str, Dict]:
        """Get comprehensive statistics grouped by mode"""
        return self._statistics(lambda a: a.quiz_type)

    def get_statistics_by_difficulty(self) -> Dict[str, Dict]:
        """Get comprehensive statistics grouped by difficulty"""
        return self._statistics(lambda a: a.difficulty)

    def get_statistics_by_topic(self) -> Dict[str, Dict]:
        """Get statistics grouped by topic (count and average only)"""
        return self._statistics(lambda a: a.topic, include_min_max=False)

    def _statistics(self, key_fn, include_min_max: bool = True) -> Dict[str, Dict]:
        """Group attempts by key_fn and compute count/avg/min/max score"""
        groups = {}
        for attempt in self.get_all():
            key = key_fn(attempt)
            if key is None:
                continue
            groups.setdefault(key, []).append(attempt.score)

        stats = {}
        for key, scores in groups.items():
            stats[key] = {
                'count': len(scores),
                'average_score': round(sum(scores) / len(scores), 2),
            }
            if include_min_max:
                stats[key]['min_score'] = min(scores)
                stats[key]['max_score'] = max(scores)
        return stats

    def delete_sample_attempts(self) -> int:
        """Delete all sample data attempts (session_id starting with 'sample-')"""
        return self.store.delete_where(
            lambda r: str(r.get('session_id', '')).startswith('sample-')
        )
