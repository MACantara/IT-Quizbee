"""
Tests for Service Layer - Analytics Service

This module tests the AnalyticsService business logic layer.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from app.services.analytics_service import AnalyticsService
from app.repositories.quiz_attempt_repository import QuizAttemptRepository
from config import TestingConfig


class TestAnalyticsService:
    """Tests for AnalyticsService"""
    
    @pytest.fixture
    def mock_attempt_repo(self):
        """Mock attempt repository"""
        return Mock(spec=QuizAttemptRepository)
    
    @pytest.fixture
    def analytics_service(self, mock_attempt_repo):
        """Create analytics service with mocked repository"""
        return AnalyticsService(mock_attempt_repo)
    
    @pytest.fixture
    def sample_attempts(self):
        """Create sample quiz attempts"""
        attempts = []
        for i in range(10):
            attempt = Mock()
            attempt.score = 70 + (i * 3)  # Scores from 70 to 97
            attempt.time_taken = 300 + (i * 10)
            attempt.quiz_type = 'elimination' if i % 2 == 0 else 'finals'
            attempt.difficulty = 'easy' if i < 3 else 'medium' if i < 7 else 'hard'
            attempt.topic = 'python' if i < 5 else 'networks'
            attempt.subtopic = f'subtopic_{i}'
            attempt.user_name = f'User{i % 3}'  # 3 different users
            attempt.correct_count = 7 + i
            attempt.incorrect_count = 3
            attempt.created_at = datetime.now() - timedelta(days=i)
            attempts.append(attempt)
        return attempts
    
    def test_get_dashboard_statistics_empty(self, analytics_service, mock_attempt_repo):
        """Test dashboard statistics with no attempts"""
        mock_attempt_repo.get_recent_attempts.return_value = []
        mock_attempt_repo.get_statistics_by_mode.return_value = {}
        mock_attempt_repo.get_statistics_by_difficulty.return_value = {}
        mock_attempt_repo.get_statistics_by_topic.return_value = {}
        
        stats = analytics_service.get_dashboard_statistics(days=30)
        
        assert stats['overview']['total_attempts'] == 0
        assert stats['overview']['average_score'] == 0
        assert stats['overview']['pass_rate'] == 0
    
    def test_get_dashboard_statistics_with_data(self, analytics_service, mock_attempt_repo, sample_attempts):
        """Test dashboard statistics with sample data"""
        mock_attempt_repo.get_recent_attempts.return_value = sample_attempts
        mock_attempt_repo.get_statistics_by_mode.return_value = {
            'elimination': {'count': 5, 'avg_score': 75.0},
            'finals': {'count': 5, 'avg_score': 85.0}
        }
        mock_attempt_repo.get_statistics_by_difficulty.return_value = {
            'easy': {'count': 3, 'avg_score': 70.0},
            'medium': {'count': 4, 'avg_score': 78.0},
            'hard': {'count': 3, 'avg_score': 90.0}
        }
        mock_attempt_repo.get_statistics_by_topic.return_value = {
            'python': {'count': 5, 'avg_score': 76.0},
            'networks': {'count': 5, 'avg_score': 84.0}
        }
        
        stats = analytics_service.get_dashboard_statistics(days=30)
        
        assert stats['overview']['total_attempts'] == 10
        assert stats['overview']['average_score'] > 0
        assert stats['overview']['pass_rate'] > 0
        assert 'by_mode' in stats
        assert 'by_difficulty' in stats
        assert 'by_topic' in stats
    
    def test_get_mode_comparison(self, analytics_service, mock_attempt_repo):
        """Test mode comparison statistics"""
        mock_attempt_repo.get_statistics_by_mode.return_value = {
            'elimination': {'count': 50, 'avg_score': 75.0},
            'finals': {'count': 30, 'avg_score': 65.0}
        }
        
        comparison = analytics_service.get_mode_comparison()
        
        assert 'elimination' in comparison
        assert 'finals' in comparison
        assert comparison['elimination']['difficulty_rating'] == 'Medium'  # avg 75 is >=60 and <80, so 'Medium'
        assert comparison['finals']['difficulty_rating'] == 'Medium'  # avg 65
    
    def test_calculate_difficulty_rating(self, analytics_service):
        """Test difficulty rating calculation"""
        assert analytics_service._calculate_difficulty_rating({'avg_score': 85}) == 'Easy'
        assert analytics_service._calculate_difficulty_rating({'avg_score': 70}) == 'Medium'
        assert analytics_service._calculate_difficulty_rating({'avg_score': 50}) == 'Hard'
        assert analytics_service._calculate_difficulty_rating({'avg_score': 30}) == 'Very Hard'
    
    def test_get_topic_performance_specific(self, analytics_service, mock_attempt_repo):
        """Test getting performance for specific topic"""
        mock_attempts = [Mock(score=80, correct_count=8, incorrect_count=2) for _ in range(5)]
        mock_attempt_repo.get_attempts_by_topic.return_value = mock_attempts
        
        result = analytics_service.get_topic_performance('python')
        
        assert result['topic'] == 'python'
        assert 'statistics' in result
        mock_attempt_repo.get_attempts_by_topic.assert_called_once_with('python')
    
    def test_get_topic_performance_all(self, analytics_service, mock_attempt_repo):
        """Test getting performance for all topics"""
        mock_attempt_repo.get_statistics_by_topic.return_value = {
            'python': {'count': 10, 'avg_score': 75.0},
            'networks': {'count': 8, 'avg_score': 82.0}
        }
        
        result = analytics_service.get_topic_performance(topic=None)
        
        assert 'python' in result
        assert 'networks' in result
    
    def test_get_difficulty_analysis(self, analytics_service, mock_attempt_repo):
        """Test difficulty analysis with proper ordering"""
        mock_attempt_repo.get_statistics_by_difficulty.return_value = {
            'hard': {'count': 10, 'avg_score': 65.0},
            'easy': {'count': 20, 'avg_score': 85.0},
            'medium': {'count': 15, 'avg_score': 75.0}
        }
        
        result = analytics_service.get_difficulty_analysis()
        
        # Should be ordered: easy, medium, hard
        keys = list(result.keys())
        assert keys == ['easy', 'medium', 'hard']
    
    def test_get_user_performance_no_attempts(self, analytics_service, mock_attempt_repo):
        """Test user performance with no attempts"""
        mock_attempt_repo.get_attempts_by_user.return_value = []
        
        result = analytics_service.get_user_performance('NonexistentUser', days=30)
        
        assert result['user_name'] == 'NonexistentUser'
        assert result['total_attempts'] == 0
        assert result['statistics'] == {}
    
    def test_get_user_performance_with_data(self, analytics_service, mock_attempt_repo, sample_attempts):
        """Test user performance with sample data"""
        user_attempts = [a for a in sample_attempts if a.user_name == 'User0']
        mock_attempt_repo.get_attempts_by_user.return_value = user_attempts
        
        result = analytics_service.get_user_performance('User0', days=30)
        
        assert result['user_name'] == 'User0'
        assert result['total_attempts'] == len(user_attempts)
        assert 'average_score' in result['statistics']
        assert 'best_score' in result['statistics']
        assert 'worst_score' in result['statistics']
    
    def test_calculate_improvement(self, analytics_service):
        """Test improvement calculation"""
        # Create attempts with improving scores
        attempts = []
        for i in range(10):
            attempt = Mock()
            attempt.score = 50 + (i * 5)  # Improving from 50 to 95
            attempts.append(attempt)
        
        improvement = analytics_service._calculate_improvement(attempts)
        
        # Should show positive improvement
        assert improvement > 0
    
    def test_export_statistics_json(self, analytics_service, mock_attempt_repo):
        """Test exporting statistics in JSON format"""
        mock_attempt_repo.get_recent_attempts.return_value = []
        mock_attempt_repo.get_statistics_by_mode.return_value = {}
        mock_attempt_repo.get_statistics_by_difficulty.return_value = {}
        mock_attempt_repo.get_statistics_by_topic.return_value = {}
        
        result = analytics_service.export_statistics(format='json')
        
        assert isinstance(result, dict)
        assert 'overview' in result
    
    def test_export_statistics_csv(self, analytics_service, mock_attempt_repo):
        """Test exporting statistics in CSV format"""
        mock_attempt_repo.get_recent_attempts.return_value = []
        mock_attempt_repo.get_statistics_by_mode.return_value = {}
        mock_attempt_repo.get_statistics_by_difficulty.return_value = {}
        mock_attempt_repo.get_statistics_by_topic.return_value = {}
        
        result = analytics_service.export_statistics(format='csv')
        
        assert isinstance(result, dict)
        assert 'overview' in result
        assert 'mode_stats' in result
        assert 'difficulty_stats' in result
        assert 'topic_stats' in result
    
    def test_export_statistics_invalid_format(self, analytics_service, mock_attempt_repo):
        """Test exporting with invalid format raises error"""
        # Configure mock to return empty list to avoid len() error
        mock_attempt_repo.get_recent_attempts.return_value = []
        
        with pytest.raises(ValueError, match="Unsupported format"):
            analytics_service.export_statistics(format='xml')
    
    def test_get_top_performers(self, analytics_service, sample_attempts):
        """Test getting top performers"""
        performers = analytics_service._get_top_performers(sample_attempts, limit=3)
        
        assert len(performers) <= 3
        assert all('user_name' in p for p in performers)
        assert all('average_score' in p for p in performers)
        assert all('total_attempts' in p for p in performers)
        
        # Should be sorted by average score (descending)
        if len(performers) > 1:
            assert performers[0]['average_score'] >= performers[1]['average_score']
    
    def test_get_recent_activity(self, analytics_service, sample_attempts):
        """Test formatting recent activity"""
        activity = analytics_service._get_recent_activity(sample_attempts[:5])
        
        assert len(activity) == 5
        assert all('user_name' in a for a in activity)
        assert all('mode' in a for a in activity)
        assert all('score' in a for a in activity)
        assert all('timestamp' in a for a in activity)
