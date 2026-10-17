"""
Script to insert sample quiz data for testing
Creates realistic quiz attempts using actual questions from the data folder
Data is written to the JSON file store (instance/ or QUIZBEE_STORE_DIR)
"""

import os
import sys
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path to import models/repositories
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Emojis in output need UTF-8; cp1252 consoles would otherwise crash
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Load environment variables (incl. QUIZBEE_STORE_DIR) before touching stores
load_dotenv()

from app.repositories.quiz_attempt_repository import QuizAttemptRepository

# Sample user names for testing
SAMPLE_NAMES = [
    'John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Williams', 'David Brown',
    'Emily Davis', 'Chris Wilson', 'Jessica Garcia', 'Daniel Martinez', 'Ashley Anderson',
    'Matthew Taylor', 'Stephanie Thomas', 'James Moore', 'Amanda Jackson', 'Robert White',
    'Jennifer Harris', 'Michael Martin', 'Lisa Thompson', 'William Garcia', 'Mary Robinson'
]

# Get data directory
DATA_DIR = Path(__file__).parent.parent / 'data'

def get_available_topics():
    """Get list of available topics from data directory"""
    topics = []
    for topic_dir in DATA_DIR.iterdir():
        if topic_dir.is_dir() and not topic_dir.name.startswith('.'):
            index_file = topic_dir / 'index.json'
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    topic_data = json.load(f)
                    topics.append({
                        'id': topic_dir.name,
                        'name': topic_data.get('topic_name', topic_dir.name),
                        'subtopics': topic_data.get('subtopics', [])
                    })
    return topics

def load_real_questions(topic_id, subtopic_id, mode='elimination', difficulty='average', count=100):
    """Load real questions from data directory"""
    if mode == 'elimination':
        questions_file = DATA_DIR / topic_id / subtopic_id / 'elimination' / f'{subtopic_id}.json'
    else:  # finals
        questions_file = DATA_DIR / topic_id / subtopic_id / 'finals' / difficulty / f'{subtopic_id}.json'

    if not questions_file.exists():
        return []

    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract questions from the data structure
    if isinstance(data, dict) and 'questions' in data:
        questions = data['questions']
    elif isinstance(data, list):
        questions = data
    else:
        return []

    # Add metadata to each question
    for q in questions:
        if 'topic_name' not in q:
            q['topic_name'] = topic_id.replace('_', ' ').title()
        if 'subtopic_name' not in q:
            q['subtopic_name'] = subtopic_id.replace('_', ' ').title()
        if mode == 'finals' and 'difficulty' not in q:
            q['difficulty'] = difficulty

    # Return random sample
    if len(questions) <= count:
        return questions
    return random.sample(questions, count)

def generate_sample_answers(questions, mode='elimination', score_range=(50, 100)):
    """
    Generate sample answers based on a desired score range.
    Result items match the shape produced by quiz_service.calculate_score.
    """
    total = len(questions)
    min_correct = int(total * score_range[0] / 100)
    max_correct = int(total * score_range[1] / 100)
    correct_count = random.randint(min_correct, max_correct)

    # Randomly select which questions to get correct
    correct_indices = random.sample(range(total), correct_count)

    answers = []
    for i, question in enumerate(questions):
        is_correct = i in correct_indices

        # Get question_id from question data
        question_id = str(question.get('id', f'q_{i}'))

        if mode in ['elimination', 'elimination_full']:
            # Multiple choice: correct answer is an option index
            correct_answer = question['correct']
            options = question.get('options', [])
            if is_correct:
                user_answer = correct_answer
            else:
                user_answer = random.choice([
                    x for x in range(len(options)) if x != correct_answer
                ])
        else:  # finals / identification
            correct_answer = question.get('answer')
            options = question.get('options', [])
            user_answer = correct_answer if is_correct else f'Wrong Answer {i}'

        answers.append({
            'question_id': question_id,
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'options': options,
            'explanation': question.get('explanation', ''),
            'topic_name': question.get('topic_name', ''),
            'subtopic_name': question.get('subtopic_name', ''),
            'difficulty': question.get('difficulty', ''),
            'mode': mode
        })

    return answers, correct_count

def insert_sample_data():
    """Insert comprehensive sample data for testing"""
    print("="*70)
    print("IT-QUIZBEE: Insert Sample Data")
    print("="*70)
    print()

    attempt_repo = QuizAttemptRepository()

    # Check if sample data already exists
    existing_attempts = [
        a for a in attempt_repo.get_all()
        if str(a.session_id or '').startswith('sample-')
    ]

    if existing_attempts:
        print("⚠️  Sample data already exists!")
        response = input("Remove existing sample data and create new? (yes/no): ").lower()
        if response != 'yes':
            print("\n❌ Operation cancelled.")
            return

        # Remove existing sample data
        print("\n🗑️  Removing existing sample data...")
        attempts_deleted = attempt_repo.delete_sample_attempts()
        print(f"✅ Existing sample data removed ({attempts_deleted} attempts).")

    print("\n🚀 Creating sample data...")
    print()

    total_attempts = 0

    # Generate data over the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Get available topics
    print("📚 Loading questions from data directory...")
    topics = get_available_topics()
    if not topics:
        print("❌ No topics found in data directory!")
        return
    print(f"   ✅ Found {len(topics)} topics")

    # Collect all questions for full mode
    all_elim_questions = []
    all_finals_questions = {'easy': [], 'average': [], 'difficult': []}

    for topic in topics:
        for subtopic in topic['subtopics']:
            # Load elimination questions
            elim_qs = load_real_questions(topic['id'], subtopic['id'], 'elimination', count=200)
            all_elim_questions.extend(elim_qs)

            # Load finals questions by difficulty
            for diff in ['easy', 'average', 'difficult']:
                finals_qs = load_real_questions(topic['id'], subtopic['id'], 'finals', diff, count=50)
                all_finals_questions[diff].extend(finals_qs)

    print(f"   📊 Loaded {len(all_elim_questions)} elimination questions")
    print(f"   📊 Loaded {len(all_finals_questions['easy'])} easy, {len(all_finals_questions['average'])} average, {len(all_finals_questions['difficult'])} difficult finals questions")

    # 1. Create Elimination Mode attempts (60-80 attempts)
    print("\n📝 Creating Elimination Mode attempts...")
    elimination_count = random.randint(60, 80)

    for i in range(elimination_count):
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        created_at = end_date - timedelta(
            days=days_ago,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # Use real questions from all topics
        if len(all_elim_questions) >= 100:
            questions = random.sample(all_elim_questions, 100)
        else:
            questions = all_elim_questions

        session_id = f'sample-elim-{i:04d}'

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

        total_questions = len(questions)
        incorrect_count = total_questions - correct_count
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        time_taken = random.randint(1800, 3600)  # 30-60 minutes

        attempt_repo.create_attempt(
            session_id=session_id,
            quiz_type='elimination',
            score=score,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            topic='all_topics',
            difficulty='mixed',
            user_name=random.choice(SAMPLE_NAMES),
            time_taken=time_taken,
            answers=answers,
            created_at=created_at,
            completed_at=created_at + timedelta(seconds=time_taken)
        )
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

        # 30 questions (10 easy, 10 average, 10 difficult)
        questions = []
        for diff, q_list in all_finals_questions.items():
            if len(q_list) >= 10:
                questions.extend(random.sample(q_list, 10))
            else:
                questions.extend(q_list)

        # If we don't have enough, fill from what we have
        if len(questions) < 30:
            all_q = all_finals_questions['easy'] + all_finals_questions['average'] + all_finals_questions['difficult']
            if len(all_q) >= 30:
                questions = random.sample(all_q, 30)
            else:
                questions = all_q

        session_id = f'sample-finals-{i:04d}'

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

        total_questions = len(questions)
        incorrect_count = total_questions - correct_count
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        time_taken = random.randint(900, 1800)  # 15-30 minutes

        attempt_repo.create_attempt(
            session_id=session_id,
            quiz_type='finals',
            score=score,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            topic='all_topics',
            difficulty=difficulty,
            user_name=random.choice(SAMPLE_NAMES),
            time_taken=time_taken,
            answers=answers,
            created_at=created_at,
            completed_at=created_at + timedelta(seconds=time_taken)
        )
        total_attempts += 1

    print(f"   ✅ Created {finals_count} finals attempts")

    # 3. Create Review Mode attempts (20-30 attempts)
    print("📝 Creating Review Mode attempts...")
    review_count = random.randint(20, 30)
    review_created = 0

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

        # Randomly select a topic and subtopic
        topic = random.choice(topics)
        subtopic = random.choice(topic['subtopics'])

        # Load real questions for this review
        questions = load_real_questions(
            topic['id'],
            subtopic['id'],
            mode,
            difficulty if mode == 'finals' else 'average',
            count=10
        )

        # Skip if no questions available
        if not questions:
            continue

        # Shorter session ID to avoid database length limit
        mode_short = 'e' if mode == 'elimination' else 'f'  # e or f
        diff_short = difficulty[0]  # e, a, or d
        session_id = f'sample-r{mode_short}{diff_short}-{i:04d}'

        # Review mode typically has moderate scores
        score_range = (60, 90)
        answers, correct_count = generate_sample_answers(
            questions, mode, score_range
        )

        # Create quiz mode label that distinguishes mode and difficulty
        quiz_type = f'review_{mode}'

        total_questions = len(questions)
        incorrect_count = total_questions - correct_count
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        time_taken = random.randint(300, 900)  # 5-15 minutes

        attempt_repo.create_attempt(
            session_id=session_id,
            quiz_type=quiz_type,
            score=score,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            topic=topic['id'],
            subtopic=subtopic['id'],
            difficulty=difficulty if mode == 'finals' else None,
            user_name=random.choice(SAMPLE_NAMES),
            time_taken=time_taken,
            answers=answers,
            created_at=created_at,
            completed_at=created_at + timedelta(seconds=time_taken)
        )
        total_attempts += 1
        review_created += 1

    print(f"   ✅ Created {review_created} review attempts")

    print("\n💾 Saving to JSON store...")
    print("   ✅ Done (all records already written)")

    print("\n" + "="*70)
    print("✅ SAMPLE DATA SUCCESSFULLY CREATED!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   • Total Attempts: {total_attempts}")
    print(f"   • Elimination Attempts: {elimination_count}")
    print(f"   • Finals Attempts: {finals_count}")
    print(f"   • Review Attempts: {review_created}")
    print(f"   • Date Range: Last 30 days")
    print("\n💡 To remove this sample data, run: python scripts/remove_sample_data.py")
    print("="*70)
    print()

if __name__ == '__main__':
    try:
        insert_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that the data/ folder contains topic question files")
        print("  2. Verify QUIZBEE_STORE_DIR in .env points to a writable directory")
        print("  3. Run from the project root directory")
