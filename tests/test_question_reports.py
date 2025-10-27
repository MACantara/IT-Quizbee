"""
Tests for Question Report Repository and API Endpoints

This module tests:
- QuestionReportRepository CRUD operations
- Question report API endpoints
- Report submission functionality
- Report status management
"""

import pytest
import json
from datetime import datetime, timedelta
from models import QuestionReport, QuizAttempt
from app.repositories.question_report_repository import QuestionReportRepository
from config import TestingConfig


class TestQuestionReportRepository:
    """Tests for QuestionReportRepository"""
    
    @pytest.fixture
    def repo(self):
        """Create repository instance"""
        return QuestionReportRepository()
    
    @pytest.fixture
    def sample_report_data(self):
        """Sample report data for testing"""
        return {
            'question_id': 'test_q_001',
            'report_type': 'incorrect_answer',
            'reason': 'The answer provided is incorrect',
            'user_name': 'Test User',
            'topic': 'Python',
            'subtopic': 'Basics',
            'quiz_type': 'elimination',
            'difficulty': 'easy',
            'question_text': 'What is Python?',
            'question_data': {'question': 'What is Python?', 'options': ['A', 'B', 'C', 'D']}
        }
    
    def test_create_report(self, db_session, repo, sample_report_data):
        """Test creating a new question report"""
        report = repo.create(**sample_report_data)
        
        assert report.id is not None
        assert report.question_id == 'test_q_001'
        assert report.report_type == 'incorrect_answer'
        assert report.reason == 'The answer provided is incorrect'
        assert report.user_name == 'Test User'
        assert report.topic == 'Python'
        assert report.subtopic == 'Basics'
        assert report.quiz_type == 'elimination'
        assert report.difficulty == 'easy'
        assert report.question_text == 'What is Python?'
        assert report.status == 'pending'
        assert report.created_at is not None
    
    def test_create_report_minimal(self, db_session, repo):
        """Test creating a report with only required fields"""
        report = repo.create(
            question_id='test_q_002',
            report_type='unclear_question'
        )
        
        assert report.id is not None
        assert report.question_id == 'test_q_002'
        assert report.report_type == 'unclear_question'
        assert report.reason is None
        assert report.user_name is None
        assert report.status == 'pending'
    
    def test_get_by_id(self, db_session, repo, sample_report_data):
        """Test getting a report by ID"""
        created = repo.create(**sample_report_data)
        
        found = repo.get_by_id(created.id)
        
        assert found is not None
        assert found.id == created.id
        assert found.question_id == 'test_q_001'
    
    def test_get_by_id_not_found(self, db_session, repo):
        """Test getting non-existent report returns None"""
        found = repo.get_by_id('nonexistent-id')
        
        assert found is None
    
    def test_get_all_reports(self, db_session, repo, sample_report_data):
        """Test getting all reports"""
        # Create multiple reports
        repo.create(**sample_report_data)
        
        data2 = sample_report_data.copy()
        data2['question_id'] = 'test_q_002'
        repo.create(**data2)
        
        data3 = sample_report_data.copy()
        data3['question_id'] = 'test_q_003'
        repo.create(**data3)
        
        reports = repo.get_all()
        
        assert len(reports) >= 3
        assert all(isinstance(r, QuestionReport) for r in reports)
    
    def test_get_all_with_status_filter(self, db_session, repo, sample_report_data):
        """Test getting reports filtered by status"""
        # Create pending report
        report1 = repo.create(**sample_report_data)
        
        # Create and update another to reviewed
        data2 = sample_report_data.copy()
        data2['question_id'] = 'test_q_002'
        report2 = repo.create(**data2)
        repo.update_status(report2.id, 'reviewed', 'Admin', 'Reviewed')
        
        # Get only pending
        pending = repo.get_all(status='pending')
        assert any(r.id == report1.id for r in pending)
        assert not any(r.id == report2.id and r.status == 'reviewed' for r in pending)
        
        # Get only reviewed
        reviewed = repo.get_all(status='reviewed')
        assert any(r.id == report2.id for r in reviewed)
    
    def test_get_all_with_limit(self, db_session, repo, sample_report_data):
        """Test getting reports with limit"""
        # Create multiple reports
        for i in range(5):
            data = sample_report_data.copy()
            data['question_id'] = f'test_q_{i:03d}'
            repo.create(**data)
        
        reports = repo.get_all(limit=3)
        
        assert len(reports) <= 3
    
    def test_get_by_question_id(self, db_session, repo, sample_report_data):
        """Test getting all reports for a specific question"""
        question_id = 'test_q_multi'
        
        # Create multiple reports for same question
        for i in range(3):
            data = sample_report_data.copy()
            data['question_id'] = question_id
            data['report_type'] = ['incorrect_answer', 'unclear_question', 'typo'][i]
            repo.create(**data)
        
        # Create report for different question
        other_data = sample_report_data.copy()
        other_data['question_id'] = 'test_q_other'
        repo.create(**other_data)
        
        reports = repo.get_by_question_id(question_id)
        
        assert len(reports) == 3
        assert all(r.question_id == question_id for r in reports)
    
    def test_get_pending_count(self, db_session, repo, sample_report_data):
        """Test getting count of pending reports"""
        initial_count = repo.get_pending_count()
        
        # Create pending reports
        repo.create(**sample_report_data)
        
        data2 = sample_report_data.copy()
        data2['question_id'] = 'test_q_002'
        repo.create(**data2)
        
        # Create and resolve one
        data3 = sample_report_data.copy()
        data3['question_id'] = 'test_q_003'
        report3 = repo.create(**data3)
        repo.update_status(report3.id, 'resolved', 'Admin')
        
        pending_count = repo.get_pending_count()
        
        assert pending_count == initial_count + 2
    
    def test_get_most_reported_questions(self, db_session, repo, sample_report_data):
        """Test getting questions with most reports"""
        # Create multiple reports for question 1
        for i in range(5):
            data = sample_report_data.copy()
            data['question_id'] = 'test_q_001'
            repo.create(**data)
        
        # Create fewer reports for question 2
        for i in range(2):
            data = sample_report_data.copy()
            data['question_id'] = 'test_q_002'
            repo.create(**data)
        
        results = repo.get_most_reported_questions(limit=2)
        
        assert len(results) > 0
        # First result should be question with most reports
        assert results[0].question_id == 'test_q_001'
        assert results[0].report_count == 5
    
    def test_get_reports_by_type(self, db_session, repo, sample_report_data):
        """Test getting report count grouped by type"""
        # Create reports of different types
        types = ['incorrect_answer', 'unclear_question', 'typo', 'incorrect_answer']
        for report_type in types:
            data = sample_report_data.copy()
            data['report_type'] = report_type
            repo.create(**data)
        
        results = repo.get_reports_by_type()
        
        assert isinstance(results, dict)
        assert results.get('incorrect_answer', 0) >= 2
        assert results.get('unclear_question', 0) >= 1
        assert results.get('typo', 0) >= 1
    
    def test_update_status(self, db_session, repo, sample_report_data):
        """Test updating report status"""
        report = repo.create(**sample_report_data)
        
        assert report.status == 'pending'
        assert report.reviewed_by is None
        assert report.reviewed_at is None
        
        updated = repo.update_status(
            report.id,
            'resolved',
            'Test Admin',
            'Issue fixed'
        )
        
        assert updated.status == 'resolved'
        assert updated.reviewed_by == 'Test Admin'
        assert updated.admin_notes == 'Issue fixed'
        assert updated.reviewed_at is not None
    
    def test_update_status_not_found(self, db_session, repo):
        """Test updating non-existent report returns None"""
        result = repo.update_status('nonexistent', 'resolved')
        
        assert result is None
    
    def test_update_status_transitions(self, db_session, repo, sample_report_data):
        """Test different status transitions"""
        # Test pending -> reviewed
        report1 = repo.create(**sample_report_data)
        updated1 = repo.update_status(report1.id, 'reviewed', 'Admin1')
        assert updated1.status == 'reviewed'
        
        # Test pending -> resolved
        data2 = sample_report_data.copy()
        data2['question_id'] = 'test_q_002'
        report2 = repo.create(**data2)
        updated2 = repo.update_status(report2.id, 'resolved', 'Admin2')
        assert updated2.status == 'resolved'
        
        # Test pending -> dismissed
        data3 = sample_report_data.copy()
        data3['question_id'] = 'test_q_003'
        report3 = repo.create(**data3)
        updated3 = repo.update_status(report3.id, 'dismissed', 'Admin3', 'Not an issue')
        assert updated3.status == 'dismissed'
        assert updated3.admin_notes == 'Not an issue'
    
    def test_delete_report(self, db_session, repo, sample_report_data):
        """Test deleting a report"""
        report = repo.create(**sample_report_data)
        report_id = report.id
        
        # Verify it exists
        found = repo.get_by_id(report_id)
        assert found is not None
        
        # Delete it
        result = repo.delete(report_id)
        assert result is True
        
        # Verify it's gone
        not_found = repo.get_by_id(report_id)
        assert not_found is None
    
    def test_delete_nonexistent_report(self, db_session, repo):
        """Test deleting non-existent report returns False"""
        result = repo.delete('nonexistent-id')
        
        assert result is False


class TestQuestionReportAPI:
    """Tests for Question Report API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, app, db_session):
        """Setup test environment"""
        self.client = client
        self.app = app
        self.db = db_session
    
    @pytest.fixture
    def sample_report_payload(self):
        """Sample report payload for API tests"""
        return {
            'question_id': 'api_test_q_001',
            'report_type': 'incorrect_answer',
            'reason': 'The correct answer should be B, not A',
            'user_name': 'API Test User',
            'topic': 'Python',
            'subtopic': 'Data Types',
            'quiz_type': 'elimination',
            'difficulty': 'medium',
            'question_text': 'What is a list in Python?',
            'question_data': {
                'question': 'What is a list in Python?',
                'options': ['Tuple', 'List', 'Dict', 'Set'],
                'correct_answer': 1
            }
        }
    
    def test_submit_question_report(self, db_session, sample_report_payload):
        """Test POST /api/questions/report endpoint"""
        response = self.client.post(
            '/api/questions/report',
            data=json.dumps(sample_report_payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'report_id' in data
        assert 'message' in data
        
        # Verify report was created in database
        repo = QuestionReportRepository()
        report = repo.get_by_id(data['report_id'])
        assert report is not None
        assert report.question_id == 'api_test_q_001'
        assert report.report_type == 'incorrect_answer'
    
    def test_submit_report_minimal(self, db_session):
        """Test submitting report with only required fields"""
        payload = {
            'question_id': 'api_test_q_002',
            'report_type': 'typo'
        }
        
        response = self.client.post(
            '/api/questions/report',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_submit_report_missing_question_id(self, db_session):
        """Test submitting report without question_id"""
        payload = {
            'report_type': 'incorrect_answer',
            'reason': 'Missing question ID'
        }
        
        response = self.client.post(
            '/api/questions/report',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Question ID is required' in data['error']
    
    def test_submit_report_missing_report_type(self, db_session):
        """Test submitting report without report_type"""
        payload = {
            'question_id': 'test_q_003',
            'reason': 'Missing report type'
        }
        
        response = self.client.post(
            '/api/questions/report',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Report type is required' in data['error']
    
    def test_submit_report_all_types(self, db_session):
        """Test submitting reports with all valid types"""
        report_types = ['incorrect_answer', 'unclear_question', 'typo', 'outdated', 'other']
        
        for report_type in report_types:
            payload = {
                'question_id': f'test_q_{report_type}',
                'report_type': report_type
            }
            
            response = self.client.post(
                '/api/questions/report',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_get_question_reports_admin(self, db_session, admin_credentials):
        """Test GET /api/questions/reports endpoint (admin only)"""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        # Create some reports
        repo = QuestionReportRepository()
        repo.create(question_id='test_1', report_type='typo')
        repo.create(question_id='test_2', report_type='unclear_question')
        
        response = self.client.get('/api/questions/reports')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'reports' in data
        assert 'count' in data
        assert isinstance(data['reports'], list)
    
    def test_get_reports_requires_admin(self, db_session):
        """Test that getting reports requires admin authentication"""
        response = self.client.get('/api/questions/reports')
        
        # API endpoints return 401 for unauthorized access
        assert response.status_code == 401
    
    def test_get_reports_with_status_filter(self, db_session, admin_credentials):
        """Test getting reports filtered by status"""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        # Create reports with different statuses
        repo = QuestionReportRepository()
        report1 = repo.create(question_id='test_1', report_type='typo')
        report2 = repo.create(question_id='test_2', report_type='unclear_question')
        repo.update_status(report2.id, 'resolved', 'Admin')
        
        # Get pending reports
        response = self.client.get('/api/questions/reports?status=pending')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # All should be pending
        for report in data['reports']:
            assert report['status'] == 'pending'
    
    def test_get_reports_with_limit(self, db_session, admin_credentials):
        """Test getting reports with limit parameter"""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        # Create multiple reports
        repo = QuestionReportRepository()
        for i in range(10):
            repo.create(question_id=f'test_{i}', report_type='typo')
        
        response = self.client.get('/api/questions/reports?limit=5')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data['reports']) <= 5
    
    def test_get_pending_reports_count(self, db_session, admin_credentials):
        """Test GET /api/questions/reports/pending-count endpoint"""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        # Create pending reports
        repo = QuestionReportRepository()
        repo.create(question_id='test_1', report_type='typo')
        repo.create(question_id='test_2', report_type='unclear_question')
        
        response = self.client.get('/api/questions/reports/pending-count')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'count' in data
        assert data['count'] >= 2
    
    def test_pending_count_requires_admin(self, db_session):
        """Test that pending count requires admin authentication"""
        response = self.client.get('/api/questions/reports/pending-count')
        
        # API endpoints return 401 for unauthorized access
        assert response.status_code == 401
    
    def test_update_report_status(self, db_session, admin_credentials):
        """Test PATCH /api/questions/reports/<id> endpoint"""
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        # Create a report
        repo = QuestionReportRepository()
        report = repo.create(question_id='test_update', report_type='typo')
        
        # Update its status
        payload = {
            'status': 'resolved',
            'admin_name': 'Test Admin',
            'notes': 'Fixed the typo'
        }
        
        response = self.client.patch(
            f'/api/questions/reports/{report.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['report']['status'] == 'resolved'
        assert data['report']['reviewed_by'] == 'Test Admin'
        assert data['report']['admin_notes'] == 'Fixed the typo'
    
    def test_update_report_requires_admin(self, db_session):
        """Test that updating report requires admin authentication"""
        repo = QuestionReportRepository()
        report = repo.create(question_id='test', report_type='typo')
        
        payload = {'status': 'resolved'}
        
        response = self.client.patch(
            f'/api/questions/reports/{report.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # API endpoints return 401 for unauthorized access
        assert response.status_code == 401
    
    def test_update_report_missing_status(self, db_session, admin_credentials):
        """Test updating report without status"""
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        repo = QuestionReportRepository()
        report = repo.create(question_id='test', report_type='typo')
        
        payload = {'notes': 'Some notes'}
        
        response = self.client.patch(
            f'/api/questions/reports/{report.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Status is required' in data['error']
    
    def test_update_report_invalid_status(self, db_session, admin_credentials):
        """Test updating report with invalid status"""
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        repo = QuestionReportRepository()
        report = repo.create(question_id='test', report_type='typo')
        
        payload = {'status': 'invalid_status'}
        
        response = self.client.patch(
            f'/api/questions/reports/{report.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid status value' in data['error']
    
    def test_update_nonexistent_report(self, db_session, admin_credentials):
        """Test updating non-existent report"""
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        payload = {'status': 'resolved'}
        
        response = self.client.patch(
            '/api/questions/reports/nonexistent-id',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_delete_report(self, db_session, admin_credentials):
        """Test DELETE /api/questions/reports/<id> endpoint"""
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        # Create a report
        repo = QuestionReportRepository()
        report = repo.create(question_id='test_delete', report_type='typo')
        report_id = report.id
        
        # Delete it
        response = self.client.delete(f'/api/questions/reports/{report_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify it's deleted
        deleted_report = repo.get_by_id(report_id)
        assert deleted_report is None
    
    def test_delete_report_requires_admin(self, db_session):
        """Test that deleting report requires admin authentication"""
        repo = QuestionReportRepository()
        report = repo.create(question_id='test', report_type='typo')
        
        response = self.client.delete(f'/api/questions/reports/{report.id}')
        
        # API endpoints return 401 for unauthorized access
        assert response.status_code == 401
    
    def test_delete_nonexistent_report(self, db_session, admin_credentials):
        """Test deleting non-existent report"""
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_username'] = admin_credentials['username']
        
        response = self.client.delete('/api/questions/reports/nonexistent-id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_api_rate_limiting(self, db_session):
        """Test API rate limiting on report submission"""
        # Clear rate limiter to ensure clean state
        from app.decorators.rate_limit import _rate_limiter
        _rate_limiter.clear_all()
        
        payload = {
            'question_id': 'rate_limit_test',
            'report_type': 'typo'
        }
        
        responses = []
        # Try to submit many reports quickly (limit is 10/minute)
        for i in range(15):
            response = self.client.post(
                '/api/questions/report',
                data=json.dumps(payload),
                content_type='application/json'
            )
            responses.append(response.status_code)
        
        # First 10 should succeed, rest should be rate limited
        assert responses.count(200) == 10
        assert responses.count(429) == 5


class TestReportModalIntegration:
    """Tests for report modal integration with quiz results"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, app, db_session):
        """Setup test environment"""
        self.client = client
        self.app = app
        self.db = db_session
    
    def test_report_modal_in_results_page(self, db_session):
        """Test that report modal is included in results page"""
        # This would be an E2E test with Playwright
        # For now, we verify the modal exists in the template
        
        # Create a quiz attempt
        from app.services.quiz_service import QuizService
        from app.repositories import QuizSessionRepository, QuizAttemptRepository
        
        session_repo = QuizSessionRepository()
        attempt_repo = QuizAttemptRepository()
        quiz_service = QuizService(session_repo, attempt_repo)
        
        # Create session with required parameters (returns tuple of session_id and questions)
        session_id, questions = quiz_service.create_elimination_quiz(
            topic='computer_architecture',
            subtopic='cpu_architecture',
            difficulty='medium',
            user_name='Test User'
        )
        
        # Submit quiz
        answers = {}  # Empty answers for simplicity
        result = quiz_service.submit_quiz(session_id, answers, 'Test User')
        
        # Get results page
        response = self.client.get(f'/quiz/results?attempt_id={result["attempt_id"]}')
        
        assert response.status_code == 200
        # Verify modal elements are present
        assert b'reportModal' in response.data
        assert b'Report Question' in response.data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
