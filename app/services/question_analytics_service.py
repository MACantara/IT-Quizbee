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
        Get questions that are answered incorrectly most frequently with answer analysis
        
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
                user_answer = answer_item.get('user_answer')
                correct_answer = answer_item.get('correct_answer')
                
                if question_id:
                    if question_id not in question_stats:
                        question_stats[question_id] = {
                            'question_id': question_id,
                            'question_text': question_text,
                            'topic': topic,
                            'subtopic': subtopic,
                            'difficulty': difficulty,
                            'correct_answer': correct_answer,
                            'total_attempts': 0,
                            'incorrect_count': 0,
                            'correct_count': 0,
                            'wrong_answers': {}  # Track frequency of wrong answers
                        }
                    
                    question_stats[question_id]['total_attempts'] += 1
                    
                    if is_correct:
                        question_stats[question_id]['correct_count'] += 1
                    else:
                        question_stats[question_id]['incorrect_count'] += 1
                        
                        # Track wrong answer frequency
                        if user_answer is not None:
                            answer_key = str(user_answer)
                            stats = question_stats[question_id]
                            stats['wrong_answers'][answer_key] = stats['wrong_answers'].get(answer_key, 0) + 1
        
        # Calculate success rate and add most common wrong answer
        for q_id in question_stats:
            stats = question_stats[q_id]
            if stats['total_attempts'] > 0:
                stats['success_rate'] = round((stats['correct_count'] / stats['total_attempts']) * 100, 1)
            else:
                stats['success_rate'] = 0
            
            # Add most common wrong answer
            if stats['wrong_answers']:
                most_common = max(stats['wrong_answers'].items(), key=lambda x: x[1])
                stats['most_common_wrong_answer'] = {
                    'answer': most_common[0],
                    'frequency': most_common[1],
                    'percentage': round((most_common[1] / stats['incorrect_count'] * 100), 1) if stats['incorrect_count'] > 0 else 0
                }
            else:
                stats['most_common_wrong_answer'] = None
            
            # Clean up for JSON serialization
            stats['wrong_answer_summary'] = dict(list(sorted(stats['wrong_answers'].items(), key=lambda x: x[1], reverse=True))[:3])
            del stats['wrong_answers']  # Remove full dict to reduce payload
        
        # Sort by incorrect count (descending)
        sorted_questions = sorted(
            question_stats.values(),
            key=lambda x: x['incorrect_count'],
            reverse=True
        )
        
        return sorted_questions[:limit]
    
    def _get_lowest_success_rate_questions(self, limit=20, min_attempts=None):
        """
        Get questions with lowest success rates with answer distribution
        Only includes questions attempted at least min_attempts times
        
        Args:
            limit: Maximum number of questions to return
            min_attempts: Minimum number of attempts required (uses config default if not provided)
            
        Returns:
            List of dicts with question details and answer analysis
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
                user_answer = answer_item.get('user_answer')
                correct_answer = answer_item.get('correct_answer')
                
                if question_id:
                    if question_id not in question_stats:
                        question_stats[question_id] = {
                            'question_id': question_id,
                            'question_text': question_text,
                            'topic': topic,
                            'subtopic': subtopic,
                            'difficulty': difficulty,
                            'correct_answer': correct_answer,
                            'total_attempts': 0,
                            'incorrect_count': 0,
                            'correct_count': 0,
                            'wrong_answers': {}
                        }
                    
                    question_stats[question_id]['total_attempts'] += 1
                    
                    if is_correct:
                        question_stats[question_id]['correct_count'] += 1
                    else:
                        question_stats[question_id]['incorrect_count'] += 1
                        
                        # Track wrong answers
                        if user_answer is not None:
                            answer_key = str(user_answer)
                            stats = question_stats[question_id]
                            stats['wrong_answers'][answer_key] = stats['wrong_answers'].get(answer_key, 0) + 1
        
        # Filter by minimum attempts and calculate success rate
        filtered_questions = []
        for stats in question_stats.values():
            if stats['total_attempts'] >= min_attempts:
                stats['success_rate'] = round((stats['correct_count'] / stats['total_attempts']) * 100, 1)
                
                # Add most common wrong answer
                if stats['wrong_answers']:
                    most_common = max(stats['wrong_answers'].items(), key=lambda x: x[1])
                    stats['most_common_wrong_answer'] = {
                        'answer': most_common[0],
                        'frequency': most_common[1],
                        'percentage': round((most_common[1] / stats['incorrect_count'] * 100), 1) if stats['incorrect_count'] > 0 else 0
                    }
                    stats['wrong_answer_summary'] = dict(list(sorted(stats['wrong_answers'].items(), key=lambda x: x[1], reverse=True))[:3])
                else:
                    stats['most_common_wrong_answer'] = None
                    stats['wrong_answer_summary'] = {}
                
                del stats['wrong_answers']  # Clean up
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
    
    def get_questions_needing_improvement(self, limit=20, max_success_rate=60):
        """
        Get questions that need improvement based on multiple criteria
        
        Args:
            limit: Maximum number of questions to return
            max_success_rate: Success rate threshold (default 60%)
            
        Returns:
            List of questions with detailed improvement recommendations
        """
        attempts = QuizAttempt.query.all()
        question_stats = {}
        
        for attempt in attempts:
            answers = attempt.get_answers()
            
            for answer_item in answers:
                question_id = answer_item.get('question_id')
                if not question_id:
                    continue
                
                if question_id not in question_stats:
                    question_stats[question_id] = {
                        'question_id': question_id,
                        'question_text': answer_item.get('question', ''),
                        'topic': answer_item.get('topic') or attempt.topic,
                        'subtopic': answer_item.get('subtopic') or attempt.subtopic,
                        'difficulty': answer_item.get('difficulty') or attempt.difficulty,
                        'correct_answer': answer_item.get('correct_answer'),
                        'options': answer_item.get('options', []),
                        'total_attempts': 0,
                        'correct_count': 0,
                        'incorrect_count': 0,
                        'wrong_answers': {}
                    }
                
                stats = question_stats[question_id]
                stats['total_attempts'] += 1
                
                is_correct = answer_item.get('is_correct', False)
                user_answer = answer_item.get('user_answer')
                
                if is_correct:
                    stats['correct_count'] += 1
                else:
                    stats['incorrect_count'] += 1
                    if user_answer is not None:
                        answer_key = str(user_answer)
                        stats['wrong_answers'][answer_key] = stats['wrong_answers'].get(answer_key, 0) + 1
        
        # Get reports count for each question
        all_reports = self.report_repo.get_most_reported_questions(limit=1000)
        reports_dict = {q_id: count for q_id, _, _, _, _, count in all_reports}
        
        # Calculate improvement metrics
        improvement_candidates = []
        min_attempts = self.config.MIN_ATTEMPTS_FOR_ANALYTICS
        
        for q_id, stats in question_stats.items():
            if stats['total_attempts'] < min_attempts:
                continue
            
            success_rate = round((stats['correct_count'] / stats['total_attempts']) * 100, 1)
            
            if success_rate <= max_success_rate:
                report_count = reports_dict.get(q_id, 0)
                
                # Calculate improvement priority
                priority = (100 - success_rate)
                priority += min(stats['total_attempts'] / 10, 20)
                priority += report_count * 10
                
                # Identify improvement issues
                issues = []
                recommendations = []
                
                if success_rate < 30:
                    issues.append('Very low success rate - question may be too difficult or unclear')
                    recommendations.append('Review question wording for clarity')
                    recommendations.append('Verify correct answer is accurate')
                elif success_rate < 50:
                    issues.append('Low success rate - students struggle with this question')
                    recommendations.append('Consider adding hints or clarification')
                
                if report_count > 0:
                    issues.append(f'{report_count} user report(s) filed')
                    recommendations.append('Review user-submitted reports for specific issues')
                
                # Check for confusing wrong answers (if one wrong answer is very popular)
                if stats['wrong_answers']:
                    most_common = max(stats['wrong_answers'].items(), key=lambda x: x[1])
                    if most_common[1] / stats['incorrect_count'] > 0.7:
                        issues.append(f'One wrong answer chosen {round(most_common[1]/stats["incorrect_count"]*100)}% of the time')
                        recommendations.append('This wrong answer may be misleading - review for clarity')
                
                improvement_candidates.append({
                    'question_id': q_id,
                    'question_text': stats['question_text'],
                    'topic': stats['topic'],
                    'subtopic': stats['subtopic'],
                    'difficulty': stats['difficulty'],
                    'correct_answer': stats['correct_answer'],
                    'options': stats['options'],
                    'total_attempts': stats['total_attempts'],
                    'success_rate': success_rate,
                    'incorrect_count': stats['incorrect_count'],
                    'report_count': report_count,
                    'priority_score': round(priority, 1),
                    'wrong_answer_distribution': dict(sorted(stats['wrong_answers'].items(), key=lambda x: x[1], reverse=True)),
                    'issues': issues,
                    'recommendations': recommendations
                })
        
        # Sort by priority score
        improvement_candidates.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return improvement_candidates[:limit]
    
    def get_answer_pattern_analysis(self, question_id):
        """
        Analyze answer patterns for a specific question
        Useful for identifying confusing distractors in multiple choice
        
        Args:
            question_id: ID of the question
            
        Returns:
            Detailed answer pattern analysis
        """
        attempts = QuizAttempt.query.all()
        
        answer_data = {
            'total_attempts': 0,
            'correct_count': 0,
            'answer_choices': {},  # For multiple choice
            'time_pattern': [],  # Track if success rate changes over time
            'user_answers': []  # For identification questions
        }
        
        question_info = None
        
        for attempt in attempts:
            answers = attempt.get_answers()
            
            for answer_item in answers:
                if answer_item.get('question_id') == question_id:
                    if not question_info:
                        question_info = {
                            'question_text': answer_item.get('question', ''),
                            'correct_answer': answer_item.get('correct_answer'),
                            'options': answer_item.get('options', []),
                            'topic': answer_item.get('topic') or attempt.topic,
                            'subtopic': answer_item.get('subtopic') or attempt.subtopic,
                            'difficulty': answer_item.get('difficulty') or attempt.difficulty
                        }
                    
                    answer_data['total_attempts'] += 1
                    
                    is_correct = answer_item.get('is_correct', False)
                    user_answer = answer_item.get('user_answer')
                    
                    if is_correct:
                        answer_data['correct_count'] += 1
                    
                    # Track answer choices
                    if user_answer is not None:
                        answer_key = str(user_answer)
                        if answer_key not in answer_data['answer_choices']:
                            answer_data['answer_choices'][answer_key] = {
                                'count': 0,
                                'is_correct': is_correct
                            }
                        answer_data['answer_choices'][answer_key]['count'] += 1
                    
                    # Track time pattern (simplified - would need attempt timestamp)
                    answer_data['time_pattern'].append({
                        'timestamp': attempt.created_at.isoformat(),
                        'is_correct': is_correct
                    })
        
        # Calculate percentages for each answer choice
        for choice in answer_data['answer_choices'].values():
            choice['percentage'] = round((choice['count'] / answer_data['total_attempts'] * 100), 1) if answer_data['total_attempts'] > 0 else 0
        
        # Build comprehensive analysis
        analysis = {
            'question_id': question_id,
            'question_info': question_info,
            'statistics': {
                'total_attempts': answer_data['total_attempts'],
                'correct_count': answer_data['correct_count'],
                'incorrect_count': answer_data['total_attempts'] - answer_data['correct_count'],
                'success_rate': round((answer_data['correct_count'] / answer_data['total_attempts'] * 100), 1) if answer_data['total_attempts'] > 0 else 0
            },
            'answer_distribution': answer_data['answer_choices'],
            'insights': []
        }
        
        # Generate insights
        if answer_data['total_attempts'] > 0:
            if analysis['statistics']['success_rate'] < 40:
                analysis['insights'].append('Very low success rate - question may need revision')
            
            # Check for equally distributed wrong answers (confusion)
            if len(answer_data['answer_choices']) > 2:
                counts = [v['count'] for v in answer_data['answer_choices'].values()]
                if max(counts) - min(counts) < answer_data['total_attempts'] * 0.2:
                    analysis['insights'].append('Answer choices are evenly distributed - may indicate guessing')
            
            # Check for obvious wrong answer (never chosen)
            for choice_key, choice_data in answer_data['answer_choices'].items():
                if choice_data['count'] == 0 and not choice_data['is_correct']:
                    analysis['insights'].append(f'Answer choice "{choice_key}" is never selected - may be too obviously wrong')
        
        return analysis
    
    def get_question_details(self, question_id):
        """
        Get detailed analytics for a specific question with answer distribution
        
        Args:
            question_id: ID of the question
            
        Returns:
            dict with detailed question analytics including answer frequency
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
        correct_answer = None
        options = []
        question_type = None  # 'multiple_choice' or 'identification'
        
        # Track answer distribution
        answer_distribution = {}
        wrong_answers = {}  # Track which wrong answers were chosen
        
        for attempt in attempts:
            answers = attempt.get_answers()
            
            for answer_item in answers:
                if answer_item.get('question_id') == question_id:
                    total_attempts += 1
                    
                    # Capture question metadata on first encounter
                    if not question_text:
                        question_text = answer_item.get('question', '')
                        topic = answer_item.get('topic') or attempt.topic
                        subtopic = answer_item.get('subtopic') or attempt.subtopic
                        difficulty = answer_item.get('difficulty') or attempt.difficulty
                        correct_answer = answer_item.get('correct_answer')
                        options = answer_item.get('options', [])
                        
                        # Determine question type
                        if options:
                            question_type = 'multiple_choice'
                        else:
                            question_type = 'identification'
                    
                    # Track correctness
                    is_correct = answer_item.get('is_correct', False)
                    user_answer = answer_item.get('user_answer')
                    
                    if is_correct:
                        correct_count += 1
                    else:
                        incorrect_count += 1
                        
                        # Track wrong answer distribution
                        if user_answer is not None:
                            answer_key = str(user_answer)
                            wrong_answers[answer_key] = wrong_answers.get(answer_key, 0) + 1
                    
                    # Track overall answer distribution
                    if user_answer is not None:
                        answer_key = str(user_answer)
                        answer_distribution[answer_key] = answer_distribution.get(answer_key, 0) + 1
        
        # Get reports for this question
        reports = self.report_repo.get_by_question_id(question_id)
        
        # Calculate success rate
        success_rate = 0
        if total_attempts > 0:
            success_rate = round((correct_count / total_attempts) * 100, 1)
        
        # Build answer analysis
        answer_analysis = []
        if question_type == 'multiple_choice' and options:
            # For multiple choice, show each option with its frequency
            for idx, option_text in enumerate(options):
                frequency = answer_distribution.get(str(idx), 0)
                percentage = round((frequency / total_attempts * 100), 1) if total_attempts > 0 else 0
                is_correct_option = (idx == correct_answer) if isinstance(correct_answer, int) else False
                
                answer_analysis.append({
                    'option_index': idx,
                    'option_text': option_text,
                    'is_correct': is_correct_option,
                    'frequency': frequency,
                    'percentage': percentage
                })
        else:
            # For identification questions, show top wrong answers
            for answer_text, frequency in sorted(wrong_answers.items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = round((frequency / total_attempts * 100), 1) if total_attempts > 0 else 0
                answer_analysis.append({
                    'answer_text': answer_text,
                    'is_correct': False,
                    'frequency': frequency,
                    'percentage': percentage
                })
        
        # Calculate improvement priority score
        # Higher score = higher priority for improvement
        # Factors: low success rate, high attempts, reports
        priority_score = 0
        if total_attempts >= self.config.MIN_ATTEMPTS_FOR_ANALYTICS:
            # Low success rate increases priority (inverse)
            priority_score += (100 - success_rate)
            
            # More attempts increases reliability of the metric
            priority_score += min(total_attempts / 10, 20)
            
            # Reports indicate user confusion
            priority_score += len(reports) * 10
        
        return {
            'question_id': question_id,
            'question_text': question_text,
            'question_type': question_type,
            'topic': topic,
            'subtopic': subtopic,
            'difficulty': difficulty,
            'correct_answer': correct_answer,
            'options': options,
            'total_attempts': total_attempts,
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'success_rate': success_rate,
            'answer_analysis': answer_analysis,
            'wrong_answer_distribution': dict(sorted(wrong_answers.items(), key=lambda x: x[1], reverse=True)[:5]),
            'report_count': len(reports),
            'reports': [report.to_dict() for report in reports],
            'priority_score': round(priority_score, 1),
            'needs_improvement': success_rate < 60 and total_attempts >= self.config.MIN_ATTEMPTS_FOR_ANALYTICS,
            'has_sufficient_data': total_attempts >= self.config.MIN_ATTEMPTS_FOR_ANALYTICS
        }
