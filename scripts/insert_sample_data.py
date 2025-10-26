"""
Script to insert sample quiz data for testing the admin dashboard
Creates realistic quiz attempts across different modes, difficulties, and topics
"""

import os
import sys
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask

# Add parent directory to path to import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models import db, QuizSession, QuizAttempt, init_db

# Sample user names for testing
SAMPLE_NAMES = [
    'John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Williams', 'David Brown',
    'Emily Davis', 'Chris Wilson', 'Jessica Garcia', 'Daniel Martinez', 'Ashley Anderson',
    'Matthew Taylor', 'Stephanie Thomas', 'James Moore', 'Amanda Jackson', 'Robert White',
    'Jennifer Harris', 'Michael Martin', 'Lisa Thompson', 'William Garcia', 'Mary Robinson'
]

# Load environment variables
load_dotenv()

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configure MySQL database connection
    mysql_url = os.environ.get('MYSQL_PUBLIC_URL')
    if mysql_url:
        if mysql_url.startswith('mysql://'):
            mysql_url = mysql_url.replace('mysql://', 'mysql+pymysql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = mysql_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/itquizbee'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'echo': False
    }
    
    return app

def generate_sample_questions(mode='elimination', count=100):
    """Generate sample questions for a quiz session"""
    questions = []
    
    for i in range(count):
        if mode in ['elimination', 'elimination_full']:
            question = {
                'id': f'sample_{mode}_{i}',
                'question': f'Sample {mode} question {i+1}?',
                'options': [
                    'Option A',
                    'Option B',
                    'Option C',
                    'Option D'
                ],
                'correct': random.randint(0, 3),
                'explanation': f'Sample explanation for question {i+1}',
                'topic_name': random.choice([
                    'Computer Architecture', 'Data Science', 'DBMS',
                    'Networks', 'Operating Systems', 'OOP',
                    'Software Engineering', 'Logic', 'IT Basics', 'E-commerce'
                ]),
                'subtopic_name': f'Subtopic {random.randint(1, 10)}'
            }
        else:  # finals
            question = {
                'id': f'sample_{mode}_{i}',
                'question': f'Sample finals question {i+1}?',
                'answer': f'Sample Answer {i+1}',
                'alternatives': [f'Alt Answer {i+1}'],
                'explanation': f'Sample explanation for question {i+1}',
                'difficulty': random.choice(['easy', 'average', 'difficult']),
                'topic_name': random.choice([
                    'Computer Architecture', 'Data Science', 'DBMS'
                ]),
                'subtopic_name': f'Subtopic {random.randint(1, 10)}'
            }
        
        questions.append(question)
    
    return questions

def generate_sample_answers(questions, mode='elimination', score_range=(50, 100)):
    """Generate sample answers based on a desired score range"""
    total = len(questions)
    min_correct = int(total * score_range[0] / 100)
    max_correct = int(total * score_range[1] / 100)
    correct_count = random.randint(min_correct, max_correct)
    
    # Randomly select which questions to get correct
    correct_indices = random.sample(range(total), correct_count)
    
    answers = []
    for i, question in enumerate(questions):
        is_correct = i in correct_indices
        
        if mode in ['elimination', 'elimination_full']:
            user_answer = question['correct'] if is_correct else random.choice([
                x for x in range(4) if x != question['correct']
            ])
            
            answers.append({
                'question': question['question'],
                'options': question['options'],
                'user_answer': user_answer,
                'correct_answer': question['correct'],
                'is_correct': is_correct,
                'explanation': question['explanation'],
                'topic_name': question.get('topic_name', ''),
                'subtopic_name': question.get('subtopic_name', '')
            })
        else:  # finals
            user_answer = question['answer'] if is_correct else f'Wrong Answer {i}'
            
            answers.append({
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': question['answer'],
                'is_correct': is_correct,
                'explanation': question['explanation'],
                'difficulty': question.get('difficulty', 'easy'),
                'topic_name': question.get('topic_name', ''),
                'subtopic_name': question.get('subtopic_name', '')
            })
    
    return answers, correct_count

def insert_sample_data():
    """Insert comprehensive sample data for testing"""
    print("="*70)
    print("IT-QUIZBEE: Insert Sample Data for Admin Dashboard")
    print("="*70)
    print()
    
    app = create_app()
    init_db(app)
    
    with app.app_context():
        # Check if sample data already exists
        existing_sample = QuizSession.query.filter(
            QuizSession.id.like('sample-%')
        ).first()
        
        if existing_sample:
            print("⚠️  Sample data already exists!")
            response = input("Remove existing sample data and create new? (yes/no): ").lower()
            if response != 'yes':
                print("\n❌ Operation cancelled.")
                return
            
            # Remove existing sample data
            print("\n🗑️  Removing existing sample data...")
            QuizSession.query.filter(QuizSession.id.like('sample-%')).delete()
            db.session.commit()
            print("✅ Existing sample data removed.")
        
        print("\n🚀 Creating sample data...")
        print()
        
        total_sessions = 0
        total_attempts = 0
        
        # Generate data over the last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # 1. Create Elimination Mode attempts (60-80 attempts)
        print("📝 Creating Elimination Mode attempts...")
        elimination_count = random.randint(60, 80)
        
        for i in range(elimination_count):
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            created_at = end_date - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Create session
            questions = generate_sample_questions('elimination_full', 100)
            session = QuizSession(
                session_type='elimination',
                questions=questions,
                ttl_seconds=7200
            )
            session.id = f'sample-elim-{i:04d}'
            session.created_at = created_at
            session.expires_at = created_at + timedelta(seconds=7200)
            session.completed = True
            
            db.session.add(session)
            
            # Create attempt with varying scores
            # Earlier attempts have lower scores (learning curve)
            if days_ago > 20:
                score_range = (40, 70)  # Lower scores for older attempts
            elif days_ago > 10:
                score_range = (60, 80)  # Medium scores
            else:
                score_range = (70, 95)  # Higher scores for recent attempts
            
            answers, correct_count = generate_sample_answers(
                questions, 'elimination_full', score_range
            )
            
            attempt = QuizAttempt(
                session_id=session.id,
                quiz_mode='elimination_full',
                total_questions=100,
                correct_answers=correct_count,
                answers=answers,
                user_name=random.choice(SAMPLE_NAMES)
            )
            attempt.created_at = created_at
            attempt.completed_at = created_at + timedelta(minutes=random.randint(30, 60))
            
            db.session.add(attempt)
            total_sessions += 1
            total_attempts += 1
        
        print(f"   ✅ Created {elimination_count} elimination attempts")
        
        # 2. Create Finals Mode attempts (40-60 attempts)
        print("📝 Creating Finals Mode attempts...")
        finals_count = random.randint(40, 60)
        
        for i in range(finals_count):
            days_ago = random.randint(0, 30)
            created_at = end_date - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Create session with 30 questions (10 easy, 10 average, 10 difficult)
            questions = generate_sample_questions('finals_full', 30)
            session = QuizSession(
                session_type='finals',
                questions=questions,
                ttl_seconds=7200
            )
            session.id = f'sample-finals-{i:04d}'
            session.created_at = created_at
            session.expires_at = created_at + timedelta(seconds=7200)
            session.completed = True
            
            db.session.add(session)
            
            # Finals typically have higher scores
            if days_ago > 20:
                score_range = (50, 75)
            elif days_ago > 10:
                score_range = (65, 85)
            else:
                score_range = (75, 95)
            
            answers, correct_count = generate_sample_answers(
                questions, 'finals_full', score_range
            )
            
            # Randomly assign difficulty to the attempt
            difficulty = random.choice(['easy', 'average', 'difficult'])
            
            attempt = QuizAttempt(
                session_id=session.id,
                quiz_mode='finals_full',
                total_questions=30,
                correct_answers=correct_count,
                answers=answers,
                difficulty=difficulty,
                user_name=random.choice(SAMPLE_NAMES)
            )
            attempt.created_at = created_at
            attempt.completed_at = created_at + timedelta(minutes=random.randint(15, 30))
            
            db.session.add(attempt)
            total_sessions += 1
            total_attempts += 1
        
        print(f"   ✅ Created {finals_count} finals attempts")
        
        # 3. Create Review Mode attempts (20-30 attempts)
        print("📝 Creating Review Mode attempts...")
        review_count = random.randint(20, 30)
        
        topics = [
            'computer_architecture', 'data_science', 'dbms',
            'ecommerce_web', 'it_basics', 'logic',
            'networks', 'oop', 'operating_systems', 'software_engineering'
        ]
        
        # Review mode options
        review_modes = ['elimination', 'finals']
        review_difficulties = ['easy', 'average', 'difficult']
        
        for i in range(review_count):
            days_ago = random.randint(0, 30)
            created_at = end_date - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Randomly select mode and difficulty for this review attempt
            mode = random.choice(review_modes)
            difficulty = random.choice(review_difficulties)
            
            # Review quizzes are typically 10 questions
            questions = generate_sample_questions(mode, 10)
            session = QuizSession(
                session_type='review',
                questions=questions,
                ttl_seconds=3600
            )
            # Shorter session ID to avoid database length limit
            mode_short = 'e' if mode == 'elimination' else 'f'  # e or f
            diff_short = difficulty[0]  # e, a, or d
            session.id = f'sample-r{mode_short}{diff_short}-{i:04d}'
            session.created_at = created_at
            session.expires_at = created_at + timedelta(seconds=3600)
            session.completed = True
            
            db.session.add(session)
            
            # Review mode typically has moderate scores
            score_range = (60, 90)
            answers, correct_count = generate_sample_answers(
                questions, mode, score_range
            )
            
            # Assign random topic and subtopic
            topic_id = random.choice(topics)
            subtopic_id = f'subtopic_{random.randint(1, 10)}'
            
            # Create quiz mode label that distinguishes mode and difficulty
            quiz_mode_label = f'review_{mode}_{difficulty}'
            
            attempt = QuizAttempt(
                session_id=session.id,
                quiz_mode=quiz_mode_label,
                total_questions=10,
                correct_answers=correct_count,
                answers=answers,
                topic_id=topic_id,
                subtopic_id=subtopic_id,
                difficulty=difficulty if mode == 'finals' else None,
                user_name=random.choice(SAMPLE_NAMES)
            )
            attempt.created_at = created_at
            attempt.completed_at = created_at + timedelta(minutes=random.randint(5, 15))
            
            db.session.add(attempt)
            total_sessions += 1
            total_attempts += 1
        
        print(f"   ✅ Created {review_count} review attempts")
        
        # Commit all changes
        print("\n💾 Saving to database...")
        db.session.commit()
        
        print("\n" + "="*70)
        print("✅ SAMPLE DATA SUCCESSFULLY CREATED!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   • Total Sessions: {total_sessions}")
        print(f"   • Total Attempts: {total_attempts}")
        print(f"   • Elimination Attempts: {elimination_count}")
        print(f"   • Finals Attempts: {finals_count}")
        print(f"   • Review Attempts: {review_count}")
        print(f"   • Date Range: Last 30 days")
        print(f"\n🌐 View the data:")
        print(f"   • Admin Dashboard: http://localhost:5000/admin")
        print(f"   • API Summary: http://localhost:5000/api/analytics/summary")
        print("\n💡 To remove this sample data, run: python scripts/remove_sample_data.py")
        print("="*70)
        print()

if __name__ == '__main__':
    try:
        insert_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure MySQL server is running")
        print("  2. Verify database connection in .env file")
        print("  3. Run 'python scripts/init_db.py' first to create tables")
