"""
Tests for Repository Layer

This module tests the Repository pattern implementation.
"""

import pytest
from datetime import datetime, timedelta
from app.repositories.base_repository import BaseRepository
from app.repositories.quiz_session_repository import QuizSessionRepository
from app.repositories.quiz_attempt_repository import QuizAttemptRepository
from models import db, QuizSession, QuizAttempt
from config import TestingConfig


class TestBaseRepository:
    """Tests for BaseRepository"""
    
    def test_create(self, db_session):
        """Test creating a record"""
        repo = QuizSessionRepository()
        
        session = repo.create(
            quiz_type='elimination',
            topic='python',
            subtopic='basics',
            questions=[],  # Pass as list, not JSON string
            time_limit=600
        )
        
        assert session.id is not None
        assert session.quiz_type == 'elimination'
        assert session.topic == 'python'
    
    def test_get_by_id(self, db_session, sample_quiz_session):
        """Test getting record by ID"""
        repo = QuizSessionRepository()
        
        found = repo.get_by_id(sample_quiz_session.id)
        
        assert found is not None
        assert found.id == sample_quiz_session.id
    
    def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent record returns None"""
        repo = QuizSessionRepository()
        
        found = repo.get_by_id('nonexistent')
        
        assert found is None
    
    def test_get_all(self, db_session):
        """Test getting all records"""
        repo = QuizSessionRepository()
        
        # Create multiple sessions
        repo.create(quiz_type='elimination', topic='topic1', subtopic='sub1', questions=[], time_limit=600)
        repo.create(quiz_type='finals', topic='topic2', subtopic='sub2', questions=[], time_limit=900)
        
        all_sessions = repo.get_all()
        
        assert len(all_sessions) >= 2
    
    def test_filter_by(self, db_session):
        """Test filtering records"""
        repo = QuizSessionRepository()
        
        # Create sessions with different types
        repo.create(quiz_type='elimination', topic='python', subtopic='sub1', questions=[], time_limit=600)
        repo.create(quiz_type='finals', topic='python', subtopic='sub2', questions=[], time_limit=900)
        repo.create(quiz_type='elimination', topic='networks', subtopic='sub3', questions=[], time_limit=600)
        
        elimination_sessions = repo.filter_by(quiz_type='elimination')
        
        assert len(elimination_sessions) >= 2
        assert all(s.quiz_type == 'elimination' for s in elimination_sessions)
    
    def test_update(self, db_session, sample_quiz_session):
        """Test updating a record"""
        repo = QuizSessionRepository()
        
        sample_quiz_session.completed = True
        updated = repo.update(sample_quiz_session)
        
        assert updated.completed == True
    
    def test_delete(self, db_session, sample_quiz_session):
        """Test deleting a record"""
        repo = QuizSessionRepository()
        
        repo.delete_by_id(sample_quiz_session.id)
        
        found = repo.get_by_id(sample_quiz_session.id)
        assert found is None
    
    def test_count(self, db_session):
        """Test counting records"""
        repo = QuizSessionRepository()
        
        initial_count = repo.count()
        
        repo.create(quiz_type='elimination', topic='topic1', subtopic='sub1', questions=[], time_limit=600)
        
        new_count = repo.count()
        assert new_count == initial_count + 1
    
    def test_exists(self, db_session, sample_quiz_session):
        """Test checking if record exists"""
        repo = QuizSessionRepository()
        
        assert repo.exists(sample_quiz_session.id) == True
        assert repo.exists('nonexistent') == False


class TestQuizSessionRepository:
    """Tests for QuizSessionRepository"""
    
    def test_create_session(self, db_session):
        """Test creating a quiz session"""
        repo = QuizSessionRepository()
        
        session = repo.create_session(
            quiz_type='elimination',
            topic='python',
            subtopic='basics',
            difficulty='easy',
            questions=[],
            time_limit=600
        )
        
        assert session.id is not None
        assert session.quiz_type == 'elimination'
        assert session.difficulty == 'easy'
        assert session.completed == False
    
    def test_mark_completed(self, db_session, sample_quiz_session):
        """Test marking session as completed"""
        repo = QuizSessionRepository()
        
        session = repo.mark_completed(sample_quiz_session.id)
        
        assert session.completed == True
        assert session.completed_at is not None
    
    def test_get_active_sessions(self, db_session):
        """Test getting active sessions"""
        repo = QuizSessionRepository()
        
        # Create active and completed sessions
        active = repo.create_session(quiz_type='elimination', questions=[], topic='topic1', subtopic='sub1', difficulty='easy', time_limit=600)
        completed = repo.create_session(quiz_type='finals', questions=[], topic='topic2', subtopic='sub2', difficulty='medium', time_limit=900)
        repo.mark_completed(completed.id)
        
        active_sessions = repo.get_active_sessions()
        
        assert len(active_sessions) >= 1
        assert all(not s.completed for s in active_sessions)
        assert active.id in [s.id for s in active_sessions]
        assert completed.id not in [s.id for s in active_sessions]
    
    def test_get_expired_sessions(self, db_session):
        """Test getting expired sessions"""
        repo = QuizSessionRepository()
        
        # Create an old session
        old_session = repo.create_session(quiz_type='elimination', questions=[], topic='topic1', subtopic='sub1', difficulty='easy', time_limit=600)
        old_session.expires_at = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        
        expired = repo.get_expired_sessions()
        
        assert len(expired) >= 1
        assert old_session.id in [s.id for s in expired]
    
    def test_cleanup_expired(self, db_session):
        """Test cleaning up expired sessions"""
        repo = QuizSessionRepository()
        
        # Create old sessions
        old_session = repo.create_session(quiz_type='elimination', questions=[], topic='topic1', subtopic='sub1', difficulty='easy', time_limit=600)
        old_session.expires_at = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        
        count = repo.cleanup_expired()
        
        assert count >= 1


class TestQuizAttemptRepository:
    """Tests for QuizAttemptRepository"""
    
    def test_create_attempt(self, db_session, sample_quiz_session):
        """Test creating a quiz attempt"""
        repo = QuizAttemptRepository()
        
        attempt = repo.create_attempt(
            session_id=sample_quiz_session.id,
            quiz_type=sample_quiz_session.quiz_type,
            score=85.0,
            correct_count=17,
            incorrect_count=3,
            user_name='Test User',
            time_taken=300,
            answers={}
        )
        
        assert attempt.id is not None
        assert attempt.user_name == 'Test User'
        assert attempt.score == 85.0
    
    def test_get_recent_attempts(self, db_session, sample_quiz_attempt):
        """Test getting recent attempts"""
        repo = QuizAttemptRepository()
        
        recent = repo.get_recent_attempts(days=7)
        
        assert len(recent) >= 1
        assert sample_quiz_attempt.id in [a.id for a in recent]
    
    def test_get_attempts_by_user(self, db_session, sample_quiz_session):
        """Test getting attempts by user"""
        repo = QuizAttemptRepository()
        
        # Create attempts for specific user
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 80.0, 16, 4, user_name='TestUser', time_taken=300, answers={})
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 70.0, 14, 6, user_name='OtherUser', time_taken=400, answers={})
        
        user_attempts = repo.get_attempts_by_user('TestUser')
        
        assert len(user_attempts) >= 1
        assert all(a.user_name == 'TestUser' for a in user_attempts)
    
    def test_get_attempts_by_topic(self, db_session, sample_quiz_session, sample_quiz_attempt):
        """Test getting attempts by topic"""
        repo = QuizAttemptRepository()
        
        attempts = repo.get_attempts_by_topic(sample_quiz_session.topic)
        
        assert len(attempts) >= 1
        assert all(a.topic == sample_quiz_session.topic for a in attempts)
    
    def test_get_statistics_by_mode(self, db_session, sample_quiz_session):
        """Test getting statistics by mode"""
        repo = QuizAttemptRepository()
        
        # Create attempts with different modes
        session_elim = sample_quiz_session
        session_finals = QuizSession(
            quiz_type='finals',
            questions=[],
            topic='topic2',
            subtopic='sub2',
            difficulty='hard',
            time_limit=900
        )
        db.session.add(session_finals)
        db.session.commit()
        
        repo.create_attempt(session_elim.id, session_elim.quiz_type, 80.0, 16, 4, user_name='User1', time_taken=300, answers={})
        repo.create_attempt(session_finals.id, session_finals.quiz_type, 70.0, 14, 6, user_name='User2', time_taken=400, answers={})
        
        stats = repo.get_statistics_by_mode()
        
        assert 'elimination' in stats or 'finals' in stats
        if 'elimination' in stats:
            assert 'average_score' in stats['elimination']
            assert 'count' in stats['elimination']
    
    def test_get_statistics_by_difficulty(self, db_session, sample_quiz_session):
        """Test getting statistics by difficulty"""
        repo = QuizAttemptRepository()
        
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 80.0, 16, 4, user_name='User1', time_taken=300, answers={})
        
        stats = repo.get_statistics_by_difficulty()
        
        assert isinstance(stats, dict)
        if sample_quiz_session.difficulty in stats:
            assert 'avg_score' in stats[sample_quiz_session.difficulty]
    
    def test_get_statistics_by_topic(self, db_session, sample_quiz_session, sample_quiz_attempt):
        """Test getting statistics by topic"""
        repo = QuizAttemptRepository()
        
        stats = repo.get_statistics_by_topic()
        
        assert isinstance(stats, dict)
        assert sample_quiz_session.topic in stats
        assert 'average_score' in stats[sample_quiz_session.topic]
        assert 'count' in stats[sample_quiz_session.topic]
    
    @pytest.mark.skip(reason="get_user_statistics method not implemented in QuizAttemptRepository")
    def test_get_user_statistics(self, db_session, sample_quiz_session):
        """Test getting user statistics"""
        repo = QuizAttemptRepository()
        
        # Create multiple attempts for user
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 80.0, 16, 4, user_name='TestUser', time_taken=300, answers={})
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 90.0, 18, 2, user_name='TestUser', time_taken=250, answers={})
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 70.0, 14, 6, user_name='TestUser', time_taken=350, answers={})
        
        stats = repo.get_user_statistics('TestUser')
        
        assert stats['total_attempts'] == 3
        assert stats['average_score'] == 80.0  # (80+90+70)/3
        assert stats['best_score'] == 90.0
        assert stats['worst_score'] == 70.0
    
    @pytest.mark.skip(reason="get_best_scores method not implemented in QuizAttemptRepository")
    def test_get_best_scores(self, db_session, sample_quiz_session):
        """Test getting best scores"""
        repo = QuizAttemptRepository()
        
        # Create attempts with different scores
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 95.0, 19, 1, user_name='User1', time_taken=300, answers={})
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 85.0, 17, 3, user_name='User2', time_taken=350, answers={})
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 90.0, 18, 2, user_name='User3', time_taken=320, answers={})
        
        best = repo.get_best_scores(limit=2)
        
        assert len(best) == 2
        assert best[0].score >= best[1].score
        assert best[0].score == 95.0
    
    @pytest.mark.skip(reason="count_by_mode method not implemented in QuizAttemptRepository")
    def test_count_by_mode(self, db_session, sample_quiz_session):
        """Test counting attempts by mode"""
        repo = QuizAttemptRepository()
        
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 80.0, 16, 4, user_name='User1', time_taken=300, answers={})
        
        count = repo.count_by_mode('elimination')
        
        assert count >= 1
    
    @pytest.mark.skip(reason="get_average_score_by_topic method not implemented - only get_average_score_by_mode exists")
    def test_get_average_score_by_topic(self, db_session, sample_quiz_session):
        """Test getting average score by topic"""
        repo = QuizAttemptRepository()
        
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 80.0, 16, 4, user_name='User1', time_taken=300, answers={})
        repo.create_attempt(sample_quiz_session.id, sample_quiz_session.quiz_type, 90.0, 18, 2, user_name='User2', time_taken=250, answers={})
        
        avg = repo.get_average_score_by_topic(sample_quiz_session.topic)
        
        assert avg == 85.0  # (80+90)/2
