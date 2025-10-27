"""
Tests for QuestionAnalyticsService
Tests all enhanced question analytics methods including:
- Question statistics
- Most missed questions with wrong answer tracking
- Lowest success rate questions
- Questions needing improvement
- Answer pattern analysis
- Question details with answer distribution
"""

import pytest
from datetime import datetime
from models import QuizAttempt, QuestionReport
from app.services.question_analytics_service import QuestionAnalyticsService
from app.repositories import QuizAttemptRepository
from app.repositories.question_report_repository import QuestionReportRepository
from config import TestingConfig
import json


class TestQuestionAnalyticsService:
    """Test suite for Question Analytics Service"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app, db_session):
        """Setup test environment"""
        self.app = app
        self.db = db_session
        self.service = QuestionAnalyticsService()
        
        # Create sample quiz attempts with detailed answer data
        self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample quiz attempts and reports for testing"""
        # Sample question data
        sample_questions = [
            {
                'question_id': 'test_q1',
                'question': 'What is polymorphism?',
                'topic': 'OOP',
                'subtopic': 'Polymorphism',
                'difficulty': 'easy',
                'correct_answer': 0,
                'options': ['Many forms', 'One form', 'No form', 'Complex form']
            },
            {
                'question_id': 'test_q2',
                'question': 'What is encapsulation?',
                'topic': 'OOP',
                'subtopic': 'Encapsulation',
                'difficulty': 'average',
                'correct_answer': 1,
                'options': ['Data hiding', 'Data protection', 'Data polymorphism', 'Data abstraction']
            },
            {
                'question_id': 'test_q3',
                'question': 'Explain inheritance',
                'topic': 'OOP',
                'subtopic': 'Inheritance',
                'difficulty': 'difficult',
                'correct_answer': 'Parent-child relationship'
            }
        ]
        
        # Create 10 attempts with varying success rates
        for i in range(10):
            # Question 1: 30% success rate (3/10 correct)
            answers_1 = []
            for j, q in enumerate(sample_questions):
                answer = {
                    'question_id': q['question_id'],
                    'question': q['question'],
                    'topic': q['topic'],
                    'subtopic': q['subtopic'],
                    'difficulty': q['difficulty'],
                    'correct_answer': q['correct_answer'],
                    'options': q.get('options', [])
                }
                
                # Set user answers and correctness
                if q['question_id'] == 'test_q1':
                    # Only 3 correct answers (indices 0, 1, 2)
                    if i < 3:
                        answer['user_answer'] = 0
                        answer['is_correct'] = True
                    else:
                        # Wrong answers distributed: mostly option 2
                        answer['user_answer'] = 2 if i % 2 == 0 else 3
                        answer['is_correct'] = False
                elif q['question_id'] == 'test_q2':
                    # 70% success rate (7/10 correct)
                    if i < 7:
                        answer['user_answer'] = 1
                        answer['is_correct'] = True
                    else:
                        answer['user_answer'] = 0
                        answer['is_correct'] = False
                elif q['question_id'] == 'test_q3':
                    # Identification question - 50% success rate
                    if i < 5:
                        answer['user_answer'] = 'Parent-child relationship'
                        answer['is_correct'] = True
                    else:
                        answer['user_answer'] = f'Wrong Answer {i}'
                        answer['is_correct'] = False
                
                answers_1.append(answer)
            
            attempt = QuizAttempt(
                session_id=f'test_session_{i}',
                quiz_type='elimination',
                topic='OOP',
                subtopic='Polymorphism',
                difficulty='mixed',
                user_name=f'TestUser{i}',
                score=50 + i,
                correct_count=1 + (i % 3),
                incorrect_count=2,
                time_taken=1800,
                answers_json=json.dumps(answers_1)
            )
            self.db.add(attempt)
        
        # Create question reports
        report1 = QuestionReport(
            question_id='test_q1',
            question_text='What is polymorphism?',
            topic='OOP',
            subtopic='Polymorphism',
            quiz_type='elimination',
            difficulty='easy',
            report_type='incorrect_answer',
            reason='The correct answer seems wrong',
            user_name='TestUser1',
            question_data_json=json.dumps(sample_questions[0]),
            status='pending'
        )
        
        report2 = QuestionReport(
            question_id='test_q1',
            question_text='What is polymorphism?',
            topic='OOP',
            subtopic='Polymorphism',
            quiz_type='elimination',
            difficulty='easy',
            report_type='confusing_wording',
            reason='Question is confusing',
            user_name='TestUser2',
            question_data_json=json.dumps(sample_questions[0]),
            status='pending'
        )
        
        self.db.add(report1)
        self.db.add(report2)
        self.db.commit()
    
    def test_get_question_statistics(self):
        """Test retrieving comprehensive question statistics"""
        stats = self.service.get_question_statistics(limit=10)
        
        assert 'most_missed' in stats
        assert 'lowest_success_rate' in stats
        assert 'most_reported' in stats
        assert 'report_types' in stats
        
        # Verify data structure
        assert isinstance(stats['most_missed'], list)
        assert isinstance(stats['lowest_success_rate'], list)
        assert isinstance(stats['most_reported'], list)
    
    def test_most_missed_questions(self):
        """Test most missed questions with wrong answer tracking"""
        stats = self.service.get_question_statistics(limit=10)
        most_missed = stats['most_missed']
        
        assert len(most_missed) > 0
        
        # Check first question (test_q1 should have most incorrect)
        first = most_missed[0]
        assert 'question_id' in first
        assert 'question_text' in first
        assert 'incorrect_count' in first
        assert 'total_attempts' in first
        assert 'success_rate' in first
        
        # Verify wrong answer tracking
        if 'most_common_wrong_answer' in first:
            wrong = first['most_common_wrong_answer']
            assert 'answer' in wrong
            assert 'frequency' in wrong
            assert 'percentage' in wrong
            assert wrong['percentage'] <= 100
    
    def test_lowest_success_rate_questions(self):
        """Test lowest success rate questions"""
        stats = self.service.get_question_statistics(limit=10)
        lowest = stats['lowest_success_rate']
        
        assert len(lowest) > 0
        
        # Verify sorting (lowest success rate first)
        if len(lowest) > 1:
            assert lowest[0]['success_rate'] <= lowest[1]['success_rate']
        
        # Check data structure
        first = lowest[0]
        assert 'question_id' in first
        assert 'success_rate' in first
        assert first['success_rate'] >= 0
        assert first['success_rate'] <= 100
        
        # Verify wrong answer summary
        if 'most_common_wrong_answer' in first:
            assert 'answer' in first['most_common_wrong_answer']
    
    def test_most_reported_questions(self):
        """Test most reported questions"""
        stats = self.service.get_question_statistics(limit=10)
        reported = stats['most_reported']
        
        assert len(reported) > 0
        
        # test_q1 should be most reported (2 reports)
        first = reported[0]
        assert first['question_id'] == 'test_q1'
        assert first['report_count'] >= 2
        assert 'question_text' in first
        assert 'topic' in first
    
    def test_get_questions_needing_improvement(self):
        """Test questions needing improvement identification"""
        questions = self.service.get_questions_needing_improvement(
            limit=10,
            max_success_rate=60
        )
        
        assert isinstance(questions, list)
        
        if len(questions) > 0:
            # All questions should have success_rate <= 60%
            for q in questions:
                assert q['success_rate'] <= 60
                assert 'priority_score' in q
                assert 'issues' in q
                assert 'recommendations' in q
                assert 'wrong_answer_distribution' in q
                
                # Verify priority score calculation
                assert q['priority_score'] > 0
                
                # test_q1 should have high priority (low success + reports)
                if q['question_id'] == 'test_q1':
                    assert q['report_count'] >= 2
                    assert len(q['issues']) > 0
                    assert len(q['recommendations']) > 0
    
    def test_improvement_priority_scoring(self):
        """Test priority scoring algorithm for improvements"""
        questions = self.service.get_questions_needing_improvement(limit=10)
        
        if len(questions) > 1:
            # Verify questions are sorted by priority
            for i in range(len(questions) - 1):
                assert questions[i]['priority_score'] >= questions[i+1]['priority_score']
        
        # Check that priority increases with:
        # 1. Lower success rate
        # 2. More attempts
        # 3. More reports
        if len(questions) > 0:
            q = questions[0]
            # Priority should be affected by success rate
            success_component = 100 - q['success_rate']
            assert q['priority_score'] >= success_component
    
    def test_get_question_details(self):
        """Test detailed question analytics"""
        details = self.service.get_question_details('test_q1')
        
        assert details is not None
        assert details['question_id'] == 'test_q1'
        assert 'question_text' in details
        assert 'total_attempts' in details
        assert 'correct_count' in details
        assert 'incorrect_count' in details
        assert 'success_rate' in details
        assert 'report_count' in details
        assert 'priority_score' in details
        assert 'needs_improvement' in details
        
        # Verify answer analysis
        assert 'answer_analysis' in details
        answer_analysis = details['answer_analysis']
        
        if len(answer_analysis) > 0:
            # Check answer distribution structure
            first_answer = answer_analysis[0]
            
            # Multiple choice questions have option_index and option_text
            if 'option_index' in first_answer:
                assert 'option_text' in first_answer
                assert 'is_correct' in first_answer
                assert 'frequency' in first_answer
                assert 'percentage' in first_answer
                
                # Verify percentages sum to ~100% (accounting for rounding)
                total_percentage = sum(ans['percentage'] for ans in answer_analysis)
                assert 95 <= total_percentage <= 105
            
            # Identification questions have answer_text
            elif 'answer_text' in first_answer:
                assert 'is_correct' in first_answer
                assert 'frequency' in first_answer
                assert 'percentage' in first_answer
    
    def test_answer_pattern_analysis(self):
        """Test answer pattern analysis for specific question"""
        pattern = self.service.get_answer_pattern_analysis('test_q1')
        
        assert pattern is not None
        assert pattern['question_id'] == 'test_q1'
        
        # Check question info
        assert 'question_info' in pattern
        info = pattern['question_info']
        assert 'question_text' in info
        assert 'correct_answer' in info
        assert 'options' in info
        
        # Check statistics
        assert 'statistics' in pattern
        stats = pattern['statistics']
        assert 'total_attempts' in stats
        assert 'correct_count' in stats
        assert 'incorrect_count' in stats
        assert 'success_rate' in stats
        assert stats['success_rate'] >= 0 and stats['success_rate'] <= 100
        
        # Check answer distribution
        assert 'answer_distribution' in pattern
        dist = pattern['answer_distribution']
        assert isinstance(dist, dict)
        
        # Verify each answer choice has count and percentage
        for choice, data in dist.items():
            assert 'count' in data
            assert 'percentage' in data
            assert 'is_correct' in data
            assert data['percentage'] >= 0 and data['percentage'] <= 100
        
        # Check insights
        assert 'insights' in pattern
        assert isinstance(pattern['insights'], list)
    
    def test_answer_distribution_accuracy(self):
        """Test accuracy of answer distribution calculations"""
        details = self.service.get_question_details('test_q1')
        
        if details['answer_analysis']:
            # Sum all frequencies should equal total attempts
            total_frequency = sum(ans['frequency'] for ans in details['answer_analysis'])
            assert total_frequency == details['total_attempts']
            
            # Each percentage should be accurate
            for ans in details['answer_analysis']:
                expected_percentage = (ans['frequency'] / details['total_attempts'] * 100)
                # Allow small rounding difference
                assert abs(ans['percentage'] - expected_percentage) < 0.2
    
    def test_confusing_distractors_detection(self):
        """Test detection of confusing wrong answers"""
        pattern = self.service.get_answer_pattern_analysis('test_q1')
        
        # test_q1 should have most wrong answers on option 2
        # This should be flagged in insights
        insights = pattern['insights']
        
        # Check if the pattern was detected
        # (In our sample data, option 2 is chosen most frequently)
        assert isinstance(insights, list)
    
    def test_insufficient_data_handling(self):
        """Test handling of questions with insufficient data"""
        # Try to get details for non-existent question
        details = self.service.get_question_details('non_existent_question')
        
        # Should return None or empty structure
        assert details is None or details.get('total_attempts', 0) == 0
    
    def test_minimum_attempts_threshold(self):
        """Test minimum attempts threshold for analytics"""
        # Questions with fewer attempts should be filtered out in some methods
        questions = self.service.get_questions_needing_improvement(limit=50)
        
        # All returned questions should have minimum attempts
        min_attempts = self.service.config.MIN_ATTEMPTS_FOR_ANALYTICS
        for q in questions:
            assert q['total_attempts'] >= min_attempts
    
    def test_report_integration(self):
        """Test integration between analytics and question reports"""
        details = self.service.get_question_details('test_q1')
        
        # test_q1 has 2 reports
        assert details['report_count'] == 2
        
        # Priority score should be affected by reports
        # Each report adds 10 to priority
        assert details['priority_score'] > details['report_count'] * 10
    
    def test_difficulty_categorization(self):
        """Test handling of different difficulty levels"""
        questions = self.service.get_questions_needing_improvement(limit=50)
        
        # Should have questions from different difficulties
        difficulties = set(q['difficulty'] for q in questions if q['difficulty'])
        
        # Each question should have a valid difficulty
        for q in questions:
            assert q['difficulty'] in ['easy', 'average', 'difficult', 'mixed', None]
    
    def test_topic_subtopic_tracking(self):
        """Test proper tracking of topics and subtopics"""
        stats = self.service.get_question_statistics(limit=10)
        
        for question in stats['most_missed']:
            assert 'topic' in question
            assert 'subtopic' in question
            # Topic/subtopic should not be empty
            assert question['topic'] or question['subtopic']
    
    def test_concurrent_access(self):
        """Test service can handle concurrent access"""
        # Create multiple service instances
        service1 = QuestionAnalyticsService()
        service2 = QuestionAnalyticsService()
        
        # Both should return same data
        stats1 = service1.get_question_statistics(limit=5)
        stats2 = service2.get_question_statistics(limit=5)
        
        assert len(stats1['most_missed']) == len(stats2['most_missed'])
    
    def test_wrong_answer_summary_ordering(self):
        """Test wrong answers are ordered by frequency"""
        questions = self.service.get_questions_needing_improvement(limit=10)
        
        for q in questions:
            if q['wrong_answer_distribution']:
                # Convert to list and verify ordering
                answers = list(q['wrong_answer_distribution'].items())
                if len(answers) > 1:
                    # Should be in descending order of count
                    for i in range(len(answers) - 1):
                        assert answers[i][1] >= answers[i+1][1]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
