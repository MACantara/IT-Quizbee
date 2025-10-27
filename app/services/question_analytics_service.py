"""
Question Analytics Service
Provides question-level analytics and statistics
"""
from app.repositories.quiz_attempt_repository import QuizAttemptRepository
from app.repositories.question_report_repository import QuestionReportRepository
from config import get_config
from sqlalchemy import func
from models import db, QuizAttempt
import json


class QuestionAnalyticsService:
    """Service for question-level analytics"""
    
    def __init__(self):
        self.attempt_repo = QuizAttemptRepository()
        self.report_repo = QuestionReportRepository()
        self.config = get_config()
    
    def get_question_statistics(self, limit=20):
        """
        Get comprehensive question statistics
        
        Args:
            limit: Maximum number of questions to return
            
        Returns:
            dict with question analytics
        """
        return {
            'most_missed': self._get_most_missed_questions(limit),
            'lowest_success_rate': self._get_lowest_success_rate_questions(limit),
            'most_reported': self._get_most_reported_questions(limit),
            'report_types': self._get_report_type_distribution()
        }
    
    def _get_most_missed_questions(self, limit=20):
        """
        Get questions that are answered incorrectly most frequently
        
        Returns:
            List of dicts with question details and miss statistics
        """
        # Get all quiz attempts
        attempts = QuizAttempt.query.all()
        
        question_stats = {}
        
        for attempt in attempts:
            answers = attempt.get_answers()
            
            for answer_item in answers:
                question_id = answer_item.get('question_id')
                is_correct = answer_item.get('is_correct', False)
                question_text = answer_item.get('question', '')
                topic = answer_item.get('topic') or attempt.topic
                subtopic = answer_item.get('subtopic') or attempt.subtopic
                difficulty = answer_item.get('difficulty') or attempt.difficulty
                
                if question_id:
                    if question_id not in question_stats:
                        question_stats[question_id] = {
                            'question_id': question_id,
                            'question_text': question_text,
                            'topic': topic,
                            'subtopic': subtopic,
                            'difficulty': difficulty,
                            'total_attempts': 0,
                            'incorrect_count': 0,
                            'correct_count': 0
                        }
                    
                    question_stats[question_id]['total_attempts'] += 1
                    
                    if is_correct:
                        question_stats[question_id]['correct_count'] += 1
                    else:
                        question_stats[question_id]['incorrect_count'] += 1
        
        # Calculate success rate and sort by incorrect count
        for q_id in question_stats:
            stats = question_stats[q_id]
            if stats['total_attempts'] > 0:
                stats['success_rate'] = round((stats['correct_count'] / stats['total_attempts']) * 100, 1)
            else:
                stats['success_rate'] = 0
        
        # Sort by incorrect count (descending)
        sorted_questions = sorted(
            question_stats.values(),
            key=lambda x: x['incorrect_count'],
            reverse=True
        )
        
        return sorted_questions[:limit]
    
    def _get_lowest_success_rate_questions(self, limit=20, min_attempts=None):
        """
        Get questions with lowest success rates
        Only includes questions attempted at least min_attempts times
        
        Args:
            limit: Maximum number of questions to return
            min_attempts: Minimum number of attempts required (uses config default if not provided)
            
        Returns:
            List of dicts with question details
        """
        if min_attempts is None:
            min_attempts = self.config.MIN_ATTEMPTS_FOR_ANALYTICS
        
        # Get all quiz attempts
        attempts = QuizAttempt.query.all()
        
        question_stats = {}
        
        for attempt in attempts:
            answers = attempt.get_answers()
            
            for answer_item in answers:
                question_id = answer_item.get('question_id')
                is_correct = answer_item.get('is_correct', False)
                question_text = answer_item.get('question', '')
                topic = answer_item.get('topic') or attempt.topic
                subtopic = answer_item.get('subtopic') or attempt.subtopic
                difficulty = answer_item.get('difficulty') or attempt.difficulty
                
                if question_id:
                    if question_id not in question_stats:
                        question_stats[question_id] = {
                            'question_id': question_id,
                            'question_text': question_text,
                            'topic': topic,
                            'subtopic': subtopic,
                            'difficulty': difficulty,
                            'total_attempts': 0,
                            'incorrect_count': 0,
                            'correct_count': 0
                        }
                    
                    question_stats[question_id]['total_attempts'] += 1
                    
                    if is_correct:
                        question_stats[question_id]['correct_count'] += 1
                    else:
                        question_stats[question_id]['incorrect_count'] += 1
        
        # Filter by minimum attempts and calculate success rate
        filtered_questions = []
        for stats in question_stats.values():
            if stats['total_attempts'] >= min_attempts:
                stats['success_rate'] = round((stats['correct_count'] / stats['total_attempts']) * 100, 1)
                filtered_questions.append(stats)
        
        # Sort by success rate (ascending)
        sorted_questions = sorted(
            filtered_questions,
            key=lambda x: x['success_rate']
        )
        
        return sorted_questions[:limit]
    
    def _get_most_reported_questions(self, limit=10):
        """Get questions with most reports"""
        results = self.report_repo.get_most_reported_questions(limit)
        
        return [
            {
                'question_id': q_id,
                'question_text': q_text,
                'topic': topic,
                'subtopic': subtopic,
                'difficulty': difficulty,
                'report_count': count
            }
            for q_id, q_text, topic, subtopic, difficulty, count in results
        ]
    
    def _get_report_type_distribution(self):
        """Get distribution of report types"""
        return self.report_repo.get_reports_by_type()
    
    def get_question_details(self, question_id):
        """
        Get detailed analytics for a specific question
        
        Args:
            question_id: ID of the question
            
        Returns:
            dict with detailed question analytics
        """
        # Get all attempts for this question
        attempts = QuizAttempt.query.all()
        
        total_attempts = 0
        correct_count = 0
        incorrect_count = 0
        question_text = ''
        topic = None
        subtopic = None
        difficulty = None
        
        for attempt in attempts:
            answers = attempt.get_answers()
            
            for answer_item in answers:
                if answer_item.get('question_id') == question_id:
                    total_attempts += 1
                    
                    if not question_text:
                        question_text = answer_item.get('question', '')
                        topic = answer_item.get('topic') or attempt.topic
                        subtopic = answer_item.get('subtopic') or attempt.subtopic
                        difficulty = answer_item.get('difficulty') or attempt.difficulty
                    
                    if answer_item.get('is_correct', False):
                        correct_count += 1
                    else:
                        incorrect_count += 1
        
        # Get reports for this question
        reports = self.report_repo.get_by_question_id(question_id)
        
        # Calculate success rate
        success_rate = 0
        if total_attempts > 0:
            success_rate = round((correct_count / total_attempts) * 100, 1)
        
        return {
            'question_id': question_id,
            'question_text': question_text,
            'topic': topic,
            'subtopic': subtopic,
            'difficulty': difficulty,
            'total_attempts': total_attempts,
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'success_rate': success_rate,
            'report_count': len(reports),
            'reports': [report.to_dict() for report in reports]
        }
