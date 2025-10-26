"""
Tests for Service Layer - Quiz Service

This module tests the QuizService business logic layer.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from app.services.quiz_service import QuizService
from app.repositories.quiz_session_repository import QuizSessionRepository
from app.repositories.quiz_attempt_repository import QuizAttemptRepository


class TestQuizService:
    """Tests for QuizService"""
    
    @pytest.fixture
    def mock_session_repo(self):
        """Mock session repository"""
        return Mock(spec=QuizSessionRepository)
    
    @pytest.fixture
    def mock_attempt_repo(self):
        """Mock attempt repository"""
        return Mock(spec=QuizAttemptRepository)
    
    @pytest.fixture
    def quiz_service(self, mock_session_repo, mock_attempt_repo):
        """Create quiz service with mocked repositories"""
        return QuizService(mock_session_repo, mock_attempt_repo)
    
    def test_calculate_score_all_correct(self, quiz_service):
        """Test score calculation with all correct answers"""
        questions = [
            {"id": "1", "question": "Q1?", "correct_answer": "A", "options": ["A", "B", "C", "D"]},
            {"id": "2", "question": "Q2?", "correct_answer": "B", "options": ["A", "B", "C", "D"]},
            {"id": "3", "question": "Q3?", "correct_answer": "C", "options": ["A", "B", "C", "D"]},
        ]
        answers = {"1": "A", "2": "B", "3": "C"}
        
        result = quiz_service.calculate_score(questions, answers, 'elimination')
        
        assert result['score'] == 100.0
        assert result['correct_count'] == 3
        assert result['incorrect_count'] == 0
        assert result['passed'] == True
    
    def test_calculate_score_some_correct(self, quiz_service):
        """Test score calculation with some correct answers"""
        questions = [
            {"id": "1", "question": "Q1?", "correct_answer": "A", "options": ["A", "B", "C", "D"]},
            {"id": "2", "question": "Q2?", "correct_answer": "B", "options": ["A", "B", "C", "D"]},
            {"id": "3", "question": "Q3?", "correct_answer": "C", "options": ["A", "B", "C", "D"]},
            {"id": "4", "question": "Q4?", "correct_answer": "D", "options": ["A", "B", "C", "D"]},
        ]
        answers = {"1": "A", "2": "B", "3": "A", "4": "A"}  # 2 correct, 2 incorrect
        
        result = quiz_service.calculate_score(questions, answers, 'elimination')
        
        assert result['score'] == 50.0
        assert result['correct_count'] == 2
        assert result['incorrect_count'] == 2
        assert result['passed'] == False  # 50% < 70% pass threshold
    
    def test_calculate_score_no_answers(self, quiz_service):
        """Test score calculation with no answers"""
        questions = [
            {"id": "1", "question": "Q1?", "correct_answer": "A", "options": ["A", "B", "C", "D"]},
            {"id": "2", "question": "Q2?", "correct_answer": "B", "options": ["A", "B", "C", "D"]},
        ]
        answers = {}
        
        result = quiz_service.calculate_score(questions, answers, 'elimination')
        
        assert result['score'] == 0.0
        assert result['correct_count'] == 0
        assert result['incorrect_count'] == 2
    
    def test_passing_criteria_elimination(self, quiz_service):
        """Test passing criteria for elimination mode (70%)"""
        assert quiz_service._check_passing_criteria(70.0, 'elimination') == True
        assert quiz_service._check_passing_criteria(69.9, 'elimination') == False
        assert quiz_service._check_passing_criteria(100.0, 'elimination') == True
    
    def test_passing_criteria_finals(self, quiz_service):
        """Test passing criteria for finals mode (80%)"""
        assert quiz_service._check_passing_criteria(80.0, 'finals') == True
        assert quiz_service._check_passing_criteria(79.9, 'finals') == False
        assert quiz_service._check_passing_criteria(100.0, 'finals') == True
    
    def test_validate_session_not_found(self, quiz_service, mock_session_repo):
        """Test session validation when session doesn't exist"""
        mock_session_repo.get_by_id.return_value = None
        
        is_valid, error = quiz_service.validate_session('nonexistent')
        
        assert is_valid == False
        assert error == "Session not found"
    
    def test_validate_session_already_completed(self, quiz_service, mock_session_repo):
        """Test session validation when already completed"""
        mock_session = Mock()
        mock_session.completed = True
        mock_session_repo.get_by_id.return_value = mock_session
        
        is_valid, error = quiz_service.validate_session('session123')
        
        assert is_valid == False
        assert error == "Quiz already submitted"
    
    def test_validate_session_expired(self, quiz_service, mock_session_repo):
        """Test session validation when expired"""
        mock_session = Mock()
        mock_session.completed = False
        mock_session.is_expired.return_value = True
        mock_session_repo.get_by_id.return_value = mock_session
        
        is_valid, error = quiz_service.validate_session('session123')
        
        assert is_valid == False
        assert error == "Quiz session has expired"
    
    def test_validate_session_valid(self, quiz_service, mock_session_repo):
        """Test session validation when valid"""
        mock_session = Mock()
        mock_session.completed = False
        mock_session.is_expired.return_value = False
        mock_session_repo.get_by_id.return_value = mock_session
        
        is_valid, error = quiz_service.validate_session('session123')
        
        assert is_valid == True
        assert error is None
    
    @patch('app.services.quiz_service.event_manager')
    def test_submit_quiz_triggers_events(self, mock_event_manager, quiz_service, mock_session_repo, mock_attempt_repo):
        """Test that submitting quiz triggers appropriate events"""
        # Setup mock session
        mock_session = Mock()
        mock_session.id = 'session123'
        mock_session.completed = False
        mock_session.is_expired.return_value = False
        mock_session.quiz_type = 'elimination'
        mock_session.topic = 'test_topic'
        mock_session.subtopic = 'test_subtopic'
        mock_session.questions_json = json.dumps([
            {"id": "1", "question": "Q1?", "correct_answer": "A", "options": ["A", "B", "C", "D"]}
        ])
        mock_session_repo.get_by_id.return_value = mock_session
        
        # Setup mock attempt
        mock_attempt = Mock()
        mock_attempt.id = 'attempt123'
        mock_attempt_repo.create_attempt.return_value = mock_attempt
        
        # Submit quiz
        result = quiz_service.submit_quiz(
            session_id='session123',
            answers={'1': 'A'},
            user_name='Test User',
            time_taken=300
        )
        
        # Verify events were triggered
        assert mock_event_manager.notify.call_count >= 1  # At least QUIZ_COMPLETED event
    
    def test_submit_quiz_invalid_session(self, quiz_service, mock_session_repo):
        """Test submitting quiz with invalid session raises error"""
        mock_session_repo.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Session not found"):
            quiz_service.submit_quiz('invalid', {}, 'User')
    
    def test_submit_quiz_already_completed(self, quiz_service, mock_session_repo):
        """Test submitting already completed quiz raises error"""
        mock_session = Mock()
        mock_session.completed = True
        mock_session_repo.get_by_id.return_value = mock_session
        
        with pytest.raises(ValueError, match="already submitted"):
            quiz_service.submit_quiz('session123', {}, 'User')
    
    def test_submit_quiz_expired(self, quiz_service, mock_session_repo):
        """Test submitting expired quiz raises error"""
        mock_session = Mock()
        mock_session.completed = False
        mock_session.is_expired.return_value = True
        mock_session_repo.get_by_id.return_value = mock_session
        
        with pytest.raises(ValueError, match="expired"):
            quiz_service.submit_quiz('session123', {}, 'User')
    
    def test_get_available_topics(self, quiz_service):
        """Test getting available topics from data directory"""
        topics = quiz_service.get_available_topics()
        
        # Should return a list
        assert isinstance(topics, list)
        
        # Each topic should have required fields
        if topics:
            assert 'title' in topics[0] or 'topic_name' in topics[0]
    
    def test_load_questions_invalid_topic(self, quiz_service):
        """Test loading questions with invalid topic raises error"""
        with pytest.raises(ValueError, match="not found"):
            quiz_service.load_questions('nonexistent_topic', 'nonexistent_subtopic', 10)
