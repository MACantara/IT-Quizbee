"""
Quiz Service Layer
Handles business logic for quiz operations
"""

import json
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from app.repositories.quiz_session_repository import QuizSessionRepository
from app.repositories.quiz_attempt_repository import QuizAttemptRepository
from app.events.event_manager import event_manager, Event, EventType


class QuizService:
    """Service layer for quiz business logic"""
    
    def __init__(self, session_repo: QuizSessionRepository, attempt_repo: QuizAttemptRepository):
        self.session_repo = session_repo
        self.attempt_repo = attempt_repo
        self.data_dir = Path(__file__).parent.parent.parent / 'data'
    
    def load_questions(self, topic: str, subtopic: str, num_questions: int = 10) -> List[Dict]:
        """
        Load questions for a quiz
        
        Args:
            topic: Topic name
            subtopic: Subtopic name
            num_questions: Number of questions to load
            
        Returns:
            List of question dictionaries
        """
        questions_file = self.data_dir / topic / subtopic / 'questions.json'
        
        if not questions_file.exists():
            raise ValueError(f"Questions file not found: {questions_file}")
        
        with open(questions_file, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
        
        # Validate questions have required fields
        valid_questions = [
            q for q in all_questions 
            if all(key in q for key in ['id', 'question', 'options', 'correct_answer'])
        ]
        
        # Randomly select questions
        if len(valid_questions) < num_questions:
            return valid_questions
        
        return random.sample(valid_questions, num_questions)
    
    def create_elimination_quiz(
        self, 
        topic: str, 
        subtopic: str, 
        difficulty: str,
        user_name: str
    ) -> Tuple[str, List[Dict]]:
        """
        Create an elimination mode quiz session
        
        Args:
            topic: Topic name
            subtopic: Subtopic name
            difficulty: Difficulty level
            user_name: Name of the user
            
        Returns:
            Tuple of (session_id, questions)
        """
        # Load questions (10 for elimination mode)
        questions = self.load_questions(topic, subtopic, 10)
        
        # Create session
        session = self.session_repo.create_session(
            quiz_type='elimination',
            questions=questions,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            user_name=user_name
        )
        
        # Trigger event
        event_manager.notify(Event(
            EventType.QUIZ_STARTED,
            data={
                'session_id': session.id,
                'user_name': user_name,
                'mode': 'elimination',
                'topic': topic,
                'subtopic': subtopic,
                'difficulty': difficulty,
                'num_questions': len(questions)
            }
        ))
        
        return session.id, questions
    
    def create_finals_quiz(
        self,
        topic: str,
        subtopic: str,
        difficulty: str,
        user_name: str
    ) -> Tuple[str, List[Dict]]:
        """
        Create a finals mode quiz session
        
        Args:
            topic: Topic name
            subtopic: Subtopic name
            difficulty: Difficulty level
            user_name: Name of the user
            
        Returns:
            Tuple of (session_id, questions)
        """
        # Load questions (5 for finals mode)
        questions = self.load_questions(topic, subtopic, 5)
        
        # Create session
        session = self.session_repo.create_session(
            quiz_type='finals',
            questions=questions,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            user_name=user_name
        )
        
        # Trigger event
        event_manager.notify(Event(
            EventType.QUIZ_STARTED,
            data={
                'session_id': session.id,
                'user_name': user_name,
                'mode': 'finals',
                'topic': topic,
                'subtopic': subtopic,
                'difficulty': difficulty,
                'num_questions': len(questions)
            }
        ))
        
        return session.id, questions
    
    def calculate_score(
        self, 
        questions: List[Dict], 
        answers: Dict[str, str],
        quiz_type: str
    ) -> Dict:
        """
        Calculate quiz score with detailed results
        
        Args:
            questions: List of question dictionaries
            answers: User's answers {question_id: answer}
            quiz_type: 'elimination' or 'finals'
            
        Returns:
            Dict with score, correct_count, incorrect_count, results
        """
        correct_count = 0
        incorrect_count = 0
        results = []
        
        for question in questions:
            question_id = str(question['id'])
            user_answer = answers.get(question_id, '')
            correct_answer = question['correct_answer']
            
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1
            else:
                incorrect_count += 1
            
            results.append({
                'question_id': question_id,
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'options': question.get('options', [])
            })
        
        # Calculate score percentage
        total_questions = len(questions)
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'score': round(score, 2),
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'total_questions': total_questions,
            'results': results,
            'passed': self._check_passing_criteria(score, quiz_type)
        }
    
    def _check_passing_criteria(self, score: float, quiz_type: str) -> bool:
        """
        Check if score meets passing criteria
        
        Args:
            score: Score percentage
            quiz_type: 'elimination' or 'finals'
            
        Returns:
            True if passed, False otherwise
        """
        if quiz_type == 'elimination':
            return score >= 70  # 70% to pass elimination
        elif quiz_type == 'finals':
            return score >= 80  # 80% to pass finals
        return False
    
    def submit_quiz(
        self,
        session_id: str,
        answers: Dict[str, str],
        user_name: str,
        time_taken: Optional[int] = None
    ) -> Dict:
        """
        Submit quiz and create attempt record
        
        Args:
            session_id: Quiz session ID
            answers: User's answers
            user_name: Name of the user
            time_taken: Time taken in seconds
            
        Returns:
            Dict with results and attempt_id
        """
        # Get session
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Check if already completed
        if session.completed:
            raise ValueError("Quiz already submitted")
        
        # Check if expired
        if session.is_expired():
            raise ValueError("Quiz session has expired")
        
        # Load questions from session
        questions = json.loads(session.questions_json) if session.questions_json else []
        
        # Calculate score
        results = self.calculate_score(questions, answers, session.quiz_type)
        
        # Mark session as completed
        self.session_repo.mark_completed(session_id)
        
        # Create attempt record
        attempt = self.attempt_repo.create_attempt(
            quiz_type=session.quiz_type,
            topic=session.topic,
            subtopic=session.subtopic,
            difficulty=session.difficulty,
            user_name=user_name,
            score=results['score'],
            correct_count=results['correct_count'],
            incorrect_count=results['incorrect_count'],
            time_taken=time_taken
        )
        
        # Trigger events
        event_manager.notify(Event(
            EventType.QUIZ_COMPLETED,
            data={
                'session_id': session_id,
                'attempt_id': attempt.id,
                'user_name': user_name,
                'mode': session.quiz_type,
                'score': results['score'],
                'passed': results['passed'],
                'topic': session.topic,
                'subtopic': session.subtopic
            }
        ))
        
        # Check for high score
        if results['score'] >= 90:
            event_manager.notify(Event(
                EventType.HIGH_SCORE_ACHIEVED,
                data={
                    'user_name': user_name,
                    'score': results['score'],
                    'mode': session.quiz_type
                }
            ))
        
        return {
            'attempt_id': attempt.id,
            **results
        }
    
    def get_session_questions(self, session_id: str) -> List[Dict]:
        """
        Get questions for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of question dictionaries
        """
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        return json.loads(session.questions_json) if session.questions_json else []
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if session is still valid
        
        Args:
            session_id: Session ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        session = self.session_repo.get_by_id(session_id)
        
        if not session:
            return False, "Session not found"
        
        if session.completed:
            return False, "Quiz already submitted"
        
        if session.is_expired():
            return False, "Quiz session has expired"
        
        return True, None
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired quiz sessions
        
        Returns:
            Number of sessions cleaned up
        """
        return self.session_repo.cleanup_expired()
    
    def get_available_topics(self) -> List[Dict]:
        """
        Get list of available topics with metadata
        
        Returns:
            List of topic dictionaries
        """
        topics = []
        
        for topic_dir in self.data_dir.iterdir():
            if not topic_dir.is_dir():
                continue
            
            index_file = topic_dir / 'index.json'
            if not index_file.exists():
                continue
            
            with open(index_file, 'r', encoding='utf-8') as f:
                topic_data = json.load(f)
                topics.append(topic_data)
        
        return sorted(topics, key=lambda x: x.get('title', ''))
    
    def get_subtopics(self, topic: str) -> List[Dict]:
        """
        Get subtopics for a topic
        
        Args:
            topic: Topic name
            
        Returns:
            List of subtopic dictionaries
        """
        index_file = self.data_dir / topic / 'index.json'
        
        if not index_file.exists():
            raise ValueError(f"Topic not found: {topic}")
        
        with open(index_file, 'r', encoding='utf-8') as f:
            topic_data = json.load(f)
        
        return topic_data.get('subtopics', [])
