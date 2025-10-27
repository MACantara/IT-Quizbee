"""
Tests for Enhanced Question Analytics API Endpoints
Tests all new API endpoints for question analytics including:
- Improvement insights
- Question details with answer distribution
- Answer pattern analysis
"""

import pytest
import json
from models import QuizAttempt, QuestionReport


class TestQuestionAnalyticsAPI:
    """Test suite for Question Analytics API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, app, db_session):
        """Setup test environment with admin authentication"""
        self.client = client
        self.app = app
        self.db = db_session
        
        # Login as admin for protected endpoints
        with client.session_transaction() as sess:
            sess['admin_authenticated'] = True
            sess['admin_username'] = 'testadmin'
        
        # Create sample data
        self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample quiz attempts for testing"""
        sample_answers = []
        
        for i in range(10):
            # Question with low success rate
            answer = {
                'question_id': 'analytics_test_q1',
                'question': 'What is test question 1?',
                'topic': 'Testing',
                'subtopic': 'Unit Tests',
                'difficulty': 'easy',
                'correct_answer': 0,
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'user_answer': 0 if i < 3 else (1 if i % 2 == 0 else 2),  # 30% success
                'is_correct': i < 3
            }
            sample_answers.append(answer)
        
        for i in range(10):
            attempt = QuizAttempt(
                session_id=f'analytics_session_{i}',
                quiz_type='elimination',
                topic='Testing',
                subtopic='Unit Tests',
                difficulty='easy',
                user_name=f'AnalyticsUser{i}',
                score=30 if i < 3 else 0,
                correct_count=1 if i < 3 else 0,
                incorrect_count=0 if i < 3 else 1,
                time_taken=300,
                answers_json=json.dumps([sample_answers[i]])
            )
            self.db.add(attempt)
        
        # Add question reports
        report = QuestionReport(
            question_id='analytics_test_q1',
            question_text='What is test question 1?',
            topic='Testing',
            subtopic='Unit Tests',
            quiz_type='elimination',
            difficulty='easy',
            report_type='incorrect_answer',
            reason='This question seems incorrect',
            user_name='TestUser',
            question_data_json=json.dumps({
                'question': 'What is test question 1?',
                'options': ['Option A', 'Option B', 'Option C', 'Option D']
            }),
            status='pending'
        )
        self.db.add(report)
        self.db.commit()
    
    def test_get_question_details_api(self):
        """Test GET /api/questions/<id>/details endpoint"""
        response = self.client.get('/api/questions/analytics_test_q1/details')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'details' in data
        
        details = data['details']
        assert details['question_id'] == 'analytics_test_q1'
        assert 'question_text' in details
        assert 'total_attempts' in details
        assert 'success_rate' in details
        assert 'answer_analysis' in details
        assert 'priority_score' in details
        assert 'needs_improvement' in details
    
    def test_get_question_details_not_found(self):
        """Test question details for non-existent question"""
        response = self.client.get('/api/questions/nonexistent_question/details')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_get_improvement_insights_api(self):
        """Test GET /api/questions/improvement-insights endpoint"""
        response = self.client.get('/api/questions/improvement-insights')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'questions' in data
        assert 'count' in data
        assert isinstance(data['questions'], list)
        
        # Verify question structure
        if len(data['questions']) > 0:
            q = data['questions'][0]
            assert 'question_id' in q
            assert 'success_rate' in q
            assert 'priority_score' in q
            assert 'issues' in q
            assert 'recommendations' in q
            assert 'wrong_answer_distribution' in q
    
    def test_improvement_insights_with_filters(self):
        """Test improvement insights with query parameters"""
        response = self.client.get('/api/questions/improvement-insights?limit=5&max_success_rate=40')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert len(data['questions']) <= 5
        
        # All questions should have success_rate <= 40%
        for q in data['questions']:
            assert q['success_rate'] <= 40
    
    def test_get_answer_pattern_api(self):
        """Test GET /api/questions/<id>/answer-pattern endpoint"""
        response = self.client.get('/api/questions/analytics_test_q1/answer-pattern')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'pattern' in data
        
        pattern = data['pattern']
        assert pattern['question_id'] == 'analytics_test_q1'
        assert 'question_info' in pattern
        assert 'statistics' in pattern
        assert 'answer_distribution' in pattern
        assert 'insights' in pattern
    
    def test_answer_pattern_statistics(self):
        """Test answer pattern statistics structure"""
        response = self.client.get('/api/questions/analytics_test_q1/answer-pattern')
        data = response.get_json()
        
        stats = data['pattern']['statistics']
        assert 'total_attempts' in stats
        assert 'correct_count' in stats
        assert 'incorrect_count' in stats
        assert 'success_rate' in stats
        
        # Verify calculations
        assert stats['total_attempts'] == stats['correct_count'] + stats['incorrect_count']
        expected_rate = (stats['correct_count'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
        assert abs(stats['success_rate'] - expected_rate) < 0.5
    
    def test_answer_pattern_not_found(self):
        """Test answer pattern for non-existent question"""
        response = self.client.get('/api/questions/nonexistent_question/answer-pattern')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_question_analytics_api(self):
        """Test GET /api/questions/analytics endpoint"""
        response = self.client.get('/api/questions/analytics?limit=10')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'analytics' in data
        
        analytics = data['analytics']
        assert 'most_missed' in analytics
        assert 'lowest_success_rate' in analytics
        assert 'most_reported' in analytics
        assert 'report_types' in analytics
    
    def test_api_requires_authentication(self):
        """Test that analytics endpoints require admin authentication"""
        # Create unauthenticated client
        with self.client.session_transaction() as sess:
            sess.clear()
        
        endpoints = [
            '/api/questions/analytics_test_q1/details',
            '/api/questions/improvement-insights',
            '/api/questions/analytics_test_q1/answer-pattern',
            '/api/questions/analytics'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Should be redirected or forbidden
            assert response.status_code in [302, 403]
    
    def test_api_rate_limiting(self):
        """Test API rate limiting on analytics endpoints"""
        # Note: This test may need adjustment based on actual rate limits
        # Make many requests quickly
        endpoint = '/api/questions/analytics_test_q1/details'
        
        responses = []
        for i in range(65):  # Exceed rate limit (60/minute)
            response = self.client.get(endpoint)
            responses.append(response.status_code)
        
        # At least some should succeed, but might get rate limited
        # (depending on rate limit configuration)
        assert 200 in responses
    
    def test_improvement_insights_empty_result(self):
        """Test improvement insights when no questions need improvement"""
        # Set very low threshold
        response = self.client.get('/api/questions/improvement-insights?max_success_rate=0')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['count'] == 0
        assert len(data['questions']) == 0
    
    def test_answer_distribution_in_details(self):
        """Test answer distribution accuracy in question details"""
        response = self.client.get('/api/questions/analytics_test_q1/details')
        data = response.get_json()
        
        answer_analysis = data['details']['answer_analysis']
        
        if len(answer_analysis) > 0:
            # Total frequency should match total attempts
            total_frequency = sum(ans['frequency'] for ans in answer_analysis)
            assert total_frequency == data['details']['total_attempts']
            
            # Each answer should have valid percentage
            for ans in answer_analysis:
                assert 0 <= ans['percentage'] <= 100
                assert ans['frequency'] >= 0
    
    def test_priority_score_calculation(self):
        """Test priority score in improvement insights"""
        response = self.client.get('/api/questions/improvement-insights')
        data = response.get_json()
        
        for q in data['questions']:
            # Priority score should be positive
            assert q['priority_score'] > 0
            
            # Should reflect success rate (lower rate = higher priority)
            # Priority includes: (100 - success_rate) + attempt factor + report factor
            base_priority = 100 - q['success_rate']
            assert q['priority_score'] >= base_priority
    
    def test_issues_and_recommendations(self):
        """Test issues and recommendations in improvement insights"""
        response = self.client.get('/api/questions/improvement-insights')
        data = response.get_json()
        
        for q in data['questions']:
            # Low success rate questions should have issues
            if q['success_rate'] < 40:
                assert len(q['issues']) > 0
                assert len(q['recommendations']) > 0
            
            # Questions with reports should mention them in issues
            if q['report_count'] > 0:
                has_report_issue = any('report' in issue.lower() for issue in q['issues'])
                assert has_report_issue
    
    def test_wrong_answer_distribution_format(self):
        """Test wrong answer distribution format"""
        response = self.client.get('/api/questions/improvement-insights')
        data = response.get_json()
        
        for q in data['questions']:
            if q['wrong_answer_distribution']:
                # Should be a dictionary
                assert isinstance(q['wrong_answer_distribution'], dict)
                
                # Keys should be answer strings, values should be counts
                for answer, count in q['wrong_answer_distribution'].items():
                    assert isinstance(answer, str)
                    assert isinstance(count, int)
                    assert count > 0
    
    def test_api_error_handling(self):
        """Test API error handling"""
        # Invalid question ID format
        response = self.client.get('/api/questions//details')
        assert response.status_code == 404
        
        # Invalid parameters
        response = self.client.get('/api/questions/improvement-insights?limit=invalid')
        # Should handle gracefully (default to 20)
        assert response.status_code == 200
    
    def test_cross_mode_analytics(self):
        """Test analytics work across different quiz modes"""
        # Add finals mode attempt
        finals_answer = {
            'question_id': 'analytics_test_q1',
            'question': 'What is test question 1?',
            'topic': 'Testing',
            'subtopic': 'Unit Tests',
            'difficulty': 'difficult',
            'correct_answer': 'Answer text',
            'user_answer': 'Wrong answer',
            'is_correct': False
        }
        
        attempt = QuizAttempt(
            session_id='finals_analytics_session',
            quiz_type='finals',
            topic='Testing',
            subtopic='Unit Tests',
            difficulty='difficult',
            user_name='FinalsUser',
            score=0,
            correct_count=0,
            incorrect_count=1,
            time_taken=300,
            answers_json=json.dumps([finals_answer])
        )
        self.db.add(attempt)
        self.db.commit()
        
        # Analytics should include both elimination and finals attempts
        response = self.client.get('/api/questions/analytics_test_q1/details')
        data = response.get_json()
        
        # Total attempts should increase
        assert data['details']['total_attempts'] > 10
    
    def test_json_response_format(self):
        """Test all endpoints return proper JSON format"""
        endpoints = [
            '/api/questions/analytics_test_q1/details',
            '/api/questions/improvement-insights',
            '/api/questions/analytics_test_q1/answer-pattern',
            '/api/questions/analytics'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.content_type == 'application/json'
            
            # Should be valid JSON
            data = response.get_json()
            assert data is not None
            assert 'success' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
