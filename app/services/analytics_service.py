"""
Analytics Service Layer
Handles business logic for analytics and statistics
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.repositories.quiz_attempt_repository import QuizAttemptRepository
from app.events.event_manager import event_manager, Event, EventType


class AnalyticsService:
    """Service layer for analytics business logic"""
    
    def __init__(self, attempt_repo: QuizAttemptRepository):
        self.attempt_repo = attempt_repo
    
    def get_dashboard_statistics(self, days: int = 30) -> Dict:
        """
        Get comprehensive dashboard statistics
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with various statistics
        """
        # Trigger analytics event
        event_manager.notify(Event(
            EventType.ANALYTICS_REQUESTED,
            data={'type': 'dashboard', 'days': days}
        ))
        
        # Get recent attempts
        attempts = self.attempt_repo.get_recent_attempts(limit=1000, days=days)
        
        # Calculate statistics
        total_attempts = len(attempts)
        
        if total_attempts == 0:
            return self._empty_statistics()
        
        # Calculate averages
        total_score = sum(a.score for a in attempts)
        avg_score = total_score / total_attempts
        
        total_time = sum(a.time_taken for a in attempts if a.time_taken)
        attempts_with_time = sum(1 for a in attempts if a.time_taken)
        avg_time = total_time / attempts_with_time if attempts_with_time > 0 else 0
        
        # Get statistics by mode
        mode_stats = self.attempt_repo.get_statistics_by_mode()
        
        # Get statistics by difficulty
        difficulty_stats = self.attempt_repo.get_statistics_by_difficulty()
        
        # Get statistics by topic
        topic_stats = self.attempt_repo.get_statistics_by_topic()
        
        # Calculate pass rate
        passed_count = sum(1 for a in attempts if a.score >= 70)
        pass_rate = (passed_count / total_attempts * 100) if total_attempts > 0 else 0
        
        # Get top performers
        top_performers = self._get_top_performers(attempts)
        
        # Get recent activity
        recent_activity = self._get_recent_activity(attempts[:10])
        
        return {
            'overview': {
                'total_attempts': total_attempts,
                'average_score': round(avg_score, 2),
                'average_time': round(avg_time, 2),
                'pass_rate': round(pass_rate, 2),
                'time_period_days': days
            },
            'by_mode': mode_stats,
            'by_difficulty': difficulty_stats,
            'by_topic': topic_stats,
            'top_performers': top_performers,
            'recent_activity': recent_activity
        }
    
    def _empty_statistics(self) -> Dict:
        """Return empty statistics structure"""
        return {
            'overview': {
                'total_attempts': 0,
                'average_score': 0,
                'average_time': 0,
                'pass_rate': 0,
                'time_period_days': 0
            },
            'by_mode': {},
            'by_difficulty': {},
            'by_topic': {},
            'top_performers': [],
            'recent_activity': []
        }
    
    def _get_top_performers(self, attempts: List, limit: int = 10) -> List[Dict]:
        """
        Get top performers by average score
        
        Args:
            attempts: List of QuizAttempt objects
            limit: Maximum number of performers to return
            
        Returns:
            List of top performer dictionaries
        """
        # Group by user
        user_scores = defaultdict(list)
        for attempt in attempts:
            if attempt.user_name:
                user_scores[attempt.user_name].append(attempt.score)
        
        # Calculate averages
        performers = []
        for user_name, scores in user_scores.items():
            performers.append({
                'user_name': user_name,
                'average_score': round(sum(scores) / len(scores), 2),
                'total_attempts': len(scores),
                'best_score': max(scores)
            })
        
        # Sort by average score
        performers.sort(key=lambda x: x['average_score'], reverse=True)
        
        return performers[:limit]
    
    def _get_recent_activity(self, attempts: List) -> List[Dict]:
        """
        Format recent attempts for display
        
        Args:
            attempts: List of recent QuizAttempt objects
            
        Returns:
            List of formatted activity dictionaries
        """
        activity = []
        for attempt in attempts:
            activity.append({
                'user_name': attempt.user_name or 'Anonymous',
                'mode': attempt.quiz_type,
                'topic': attempt.topic,
                'subtopic': attempt.subtopic,
                'score': attempt.score,
                'timestamp': attempt.created_at.isoformat() if attempt.created_at else None
            })
        
        return activity
    
    def get_mode_comparison(self) -> Dict:
        """
        Compare statistics across quiz modes
        
        Returns:
            Dictionary with mode comparison data
        """
        mode_stats = self.attempt_repo.get_statistics_by_mode()
        
        comparison = {
            'elimination': mode_stats.get('elimination', {}),
            'finals': mode_stats.get('finals', {})
        }
        
        # Calculate additional metrics
        for mode, stats in comparison.items():
            if stats and stats.get('count', 0) > 0:
                stats['difficulty_rating'] = self._calculate_difficulty_rating(stats)
                stats['popularity'] = stats.get('count', 0)
        
        return comparison
    
    def _calculate_difficulty_rating(self, stats: Dict) -> str:
        """
        Calculate difficulty rating based on average score
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Difficulty rating string
        """
        avg_score = stats.get('avg_score', 0)
        
        if avg_score >= 80:
            return 'Easy'
        elif avg_score >= 60:
            return 'Medium'
        elif avg_score >= 40:
            return 'Hard'
        else:
            return 'Very Hard'
    
    def get_topic_performance(self, topic: Optional[str] = None) -> Dict:
        """
        Get performance statistics for topics
        
        Args:
            topic: Specific topic to analyze (None for all)
            
        Returns:
            Dictionary with topic performance data
        """
        if topic:
            # Get attempts for specific topic
            attempts = self.attempt_repo.get_attempts_by_topic(topic)
            
            if not attempts:
                return {'topic': topic, 'statistics': {}}
            
            stats = self._calculate_topic_stats(attempts)
            return {'topic': topic, 'statistics': stats}
        else:
            # Get all topics
            return self.attempt_repo.get_statistics_by_topic()
    
    def _calculate_topic_stats(self, attempts: List) -> Dict:
        """
        Calculate statistics for a list of attempts
        
        Args:
            attempts: List of QuizAttempt objects
            
        Returns:
            Statistics dictionary
        """
        if not attempts:
            return {}
        
        total_score = sum(a.score for a in attempts)
        total_correct = sum(a.correct_count for a in attempts)
        total_incorrect = sum(a.incorrect_count for a in attempts)
        
        return {
            'count': len(attempts),
            'avg_score': round(total_score / len(attempts), 2),
            'total_correct': total_correct,
            'total_incorrect': total_incorrect,
            'accuracy': round(
                total_correct / (total_correct + total_incorrect) * 100, 2
            ) if (total_correct + total_incorrect) > 0 else 0
        }
    
    def get_difficulty_analysis(self) -> Dict:
        """
        Analyze quiz performance by difficulty level
        
        Returns:
            Dictionary with difficulty analysis
        """
        difficulty_stats = self.attempt_repo.get_statistics_by_difficulty()
        
        # Sort by difficulty (easy -> medium -> hard)
        difficulty_order = ['easy', 'medium', 'hard']
        sorted_stats = {}
        
        for level in difficulty_order:
            if level in difficulty_stats:
                sorted_stats[level] = difficulty_stats[level]
        
        # Add any other difficulty levels
        for level, stats in difficulty_stats.items():
            if level not in sorted_stats:
                sorted_stats[level] = stats
        
        return sorted_stats
    
    def get_user_performance(self, user_name: str, days: int = 30) -> Dict:
        """
        Get performance statistics for a specific user
        
        Args:
            user_name: User name
            days: Number of days to look back
            
        Returns:
            Dictionary with user performance data
        """
        attempts = self.attempt_repo.get_attempts_by_user(user_name, days)
        
        if not attempts:
            return {
                'user_name': user_name,
                'total_attempts': 0,
                'statistics': {}
            }
        
        # Calculate statistics
        total_score = sum(a.score for a in attempts)
        avg_score = total_score / len(attempts)
        
        best_score = max(a.score for a in attempts)
        worst_score = min(a.score for a in attempts)
        
        # Get mode distribution
        mode_counts = defaultdict(int)
        for attempt in attempts:
            mode_counts[attempt.quiz_type] += 1
        
        # Get topic distribution
        topic_counts = defaultdict(int)
        for attempt in attempts:
            topic_counts[attempt.topic] += 1
        
        return {
            'user_name': user_name,
            'total_attempts': len(attempts),
            'statistics': {
                'average_score': round(avg_score, 2),
                'best_score': best_score,
                'worst_score': worst_score,
                'improvement': self._calculate_improvement(attempts),
                'mode_distribution': dict(mode_counts),
                'topic_distribution': dict(topic_counts)
            }
        }
    
    def _calculate_improvement(self, attempts: List) -> float:
        """
        Calculate improvement trend from first to last attempts
        
        Args:
            attempts: List of QuizAttempt objects (sorted by date)
            
        Returns:
            Improvement percentage
        """
        if len(attempts) < 2:
            return 0
        
        # Compare first 5 and last 5 attempts
        first_batch = attempts[:5]
        last_batch = attempts[-5:]
        
        avg_first = sum(a.score for a in first_batch) / len(first_batch)
        avg_last = sum(a.score for a in last_batch) / len(last_batch)
        
        improvement = avg_last - avg_first
        return round(improvement, 2)
    
    def export_statistics(self, format: str = 'json') -> Dict:
        """
        Export comprehensive statistics
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data dictionary
        """
        stats = self.get_dashboard_statistics(days=365)  # Full year
        
        if format == 'json':
            return stats
        elif format == 'csv':
            # Convert to CSV-friendly format
            return self._convert_to_csv_format(stats)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _convert_to_csv_format(self, stats: Dict) -> Dict:
        """
        Convert statistics to CSV-friendly format
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            CSV-friendly dictionary
        """
        # Flatten nested dictionaries
        csv_data = {
            'overview': stats.get('overview', {}),
            'mode_stats': [],
            'difficulty_stats': [],
            'topic_stats': []
        }
        
        # Convert mode stats
        for mode, data in stats.get('by_mode', {}).items():
            csv_data['mode_stats'].append({'mode': mode, **data})
        
        # Convert difficulty stats
        for difficulty, data in stats.get('by_difficulty', {}).items():
            csv_data['difficulty_stats'].append({'difficulty': difficulty, **data})
        
        # Convert topic stats
        for topic, data in stats.get('by_topic', {}).items():
            csv_data['topic_stats'].append({'topic': topic, **data})
        
        return csv_data
