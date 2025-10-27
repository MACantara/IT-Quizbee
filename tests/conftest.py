"""
Pytest configuration and shared fixtures for IT Quizbee tests.

This module provides shared fixtures for testing the new design pattern architecture.
Includes fixtures for app creation, database setup, and test clients.
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from models import db, QuizSession, QuizAttempt
from config import config, TestingConfig


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.rollback()
        db.drop_all()


@pytest.fixture
def test_user():
    """Test user credentials from config"""
    return {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }


@pytest.fixture
def admin_credentials():
    """Admin credentials from centralized config"""
    return {
        "username": TestingConfig.ADMIN_USERNAME,
        "password": TestingConfig.ADMIN_PASSWORD
    }


@pytest.fixture
def app_config():
    """Provide access to testing configuration"""
    return TestingConfig


@pytest.fixture
def sample_quiz_session(db_session):
    """Create a sample quiz session for testing"""
    session = QuizSession(
        quiz_type='elimination',
        questions=[{"id": 1, "question": "Test?", "options": ["A", "B", "C", "D"], "correct_answer": "A"}],
        topic='test_topic',
        subtopic='test_subtopic',
        difficulty='easy',
        user_name='Test User'
    )
    db_session.add(session)
    db_session.commit()
    return session


@pytest.fixture
def sample_quiz_attempt(db_session, sample_quiz_session):
    """Create a sample quiz attempt for testing"""
    attempt = QuizAttempt(
        session_id=sample_quiz_session.id,
        quiz_type='elimination',
        topic='test_topic',
        subtopic='test_subtopic',
        difficulty='easy',
        user_name='Test User',
        score=85.0,
        correct_count=8,
        incorrect_count=2,
        time_taken=300
    )
    db_session.add(attempt)
    db_session.commit()
    return attempt
