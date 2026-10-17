"""
Script to insert sample quiz data for testing the admin dashboard
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

from models import QuestionReport
from app.repositories.quiz_attempt_repository import QuizAttemptRepository
from app.repositories.question_report_repository import QuestionReportRepository

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

        # Get question_id from question data (required for analytics)
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
            'question_id': question_id,  # Required for question analytics
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
    print("IT-QUIZBEE: Insert Sample Data for Admin Dashboard")
    print("="*70)
    print()

    attempt_repo = QuizAttemptRepository()
    report_store = QuestionReportRepository._get_store()

    # Check if sample data already exists
    existing_attempts = [
        a for a in attempt_repo.get_all()
        if str(a.session_id or '').startswith('sample-')
    ]
    existing_reports = [
        r for r in report_store.all()
        if str(r.get('id', '')).startswith('sample-')
    ]

    if existing_attempts or existing_reports:
        print("⚠️  Sample data already exists!")
        response = input("Remove existing sample data and create new? (yes/no): ").lower()
        if response != 'yes':
            print("\n❌ Operation cancelled.")
            return

        # Remove existing sample data
        print("\n🗑️  Removing existing sample data...")
        attempts_deleted = attempt_repo.delete_sample_attempts()
        reports_deleted = report_store.delete_where(
            lambda r: str(r.get('id', '')).startswith('sample-')
        )
        print(f"✅ Existing sample data removed ({attempts_deleted} attempts, {reports_deleted} reports).")

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

    # 4. Create sample question reports (10-25 reports)
    print("📝 Creating sample question reports...")
    report_count = 0
    report_types = ['incorrect_answer', 'unclear_question', 'typo', 'outdated_info', 'other']
    report_statuses = ['pending', 'reviewed', 'resolved', 'dismissed']

    # Collect question IDs from attempts for realistic reports
    all_question_ids = []
    sample_attempts_for_reports = [
        a for a in attempt_repo.get_all()
        if str(a.session_id or '').startswith('sample-')
    ]

    for attempt in sample_attempts_for_reports[:30]:  # Use first 30 attempts
        answers = attempt.get_answers()
        if not answers:
            continue

        for answer in answers:
            question_id = answer.get('question_id')
            if question_id:
                # Collect both correct and incorrect questions for variety
                # But favor incorrect ones (60% incorrect, 40% correct)
                is_correct = answer.get('is_correct', False)

                if not is_correct or random.random() < 0.4:
                    all_question_ids.append({
                        'question_id': question_id,
                        'question_text': answer.get('question', '')[:200],  # Limit length
                        'topic': answer.get('topic_name') or attempt.topic,
                        'subtopic': answer.get('subtopic_name') or attempt.subtopic,
                        'difficulty': answer.get('difficulty') or attempt.difficulty,
                        'quiz_type': attempt.quiz_type,
                        'is_correct': is_correct
                    })

    # Create 10-25 random reports with unique question IDs
    num_reports = random.randint(10, 25)
    used_question_ids = set()  # Track to avoid duplicates

    if all_question_ids:
        # Shuffle to get random selection
        random.shuffle(all_question_ids)

        for q_data in all_question_ids:
            if report_count >= num_reports:
                break

            # Skip if already reported
            if q_data['question_id'] in used_question_ids:
                continue

            used_question_ids.add(q_data['question_id'])

            days_ago = random.randint(0, 30)
            created_at = end_date - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            # Choose report type based on whether answer was correct
            if q_data.get('is_correct'):
                # For correct answers, more likely to be typo/unclear
                report_type = random.choice(['typo', 'unclear_question', 'outdated_info'])
            else:
                # For incorrect answers, could be any type
                report_type = random.choice(report_types)

            # Status distribution: 40% pending, 30% reviewed, 20% resolved, 10% dismissed
            status_weights = [0.4, 0.3, 0.2, 0.1]
            status = random.choices(report_statuses, weights=status_weights)[0]

            # Generate more realistic reasons based on report type
            reason_templates = {
                'incorrect_answer': [
                    "The correct answer seems wrong. I believe option {alt} is correct.",
                    "Multiple options could be correct. Please clarify.",
                    "The explanation contradicts the marked correct answer."
                ],
                'unclear_question': [
                    "The question wording is confusing and ambiguous.",
                    "Question lacks context to determine the correct answer.",
                    "The question could be interpreted in multiple ways."
                ],
                'typo': [
                    "There's a spelling mistake in the question.",
                    "Grammar error makes the question unclear.",
                    "Formatting issue in one of the options."
                ],
                'outdated_info': [
                    "The information in this question is outdated.",
                    "This technology/standard has been updated since this question was written.",
                    "Current best practices differ from what's stated."
                ],
                'other': [
                    "This question seems out of scope for the topic.",
                    "Question difficulty doesn't match the indicated level.",
                    "Similar question appears multiple times in the quiz."
                ]
            }

            reason = random.choice(reason_templates.get(report_type, ["Sample report issue"]))
            if '{alt}' in reason:
                reason = reason.replace('{alt}', random.choice(['A', 'B', 'C', 'D']))

            report = QuestionReport(
                question_id=q_data['question_id'],
                report_type=report_type,
                reason=reason,
                user_name=random.choice(SAMPLE_NAMES),
                topic=q_data.get('topic'),
                subtopic=q_data.get('subtopic'),
                quiz_type=q_data.get('quiz_type', 'elimination'),
                difficulty=q_data.get('difficulty'),
                question_text=q_data.get('question_text', ''),
                question_data={'sample': True, 'is_correct_when_reported': q_data.get('is_correct')}
            )
            report.id = f'sample-report-{report_count:04d}'
            report.created_at = created_at
            report.status = status

            # If reviewed, resolved, or dismissed, add review data
            if status in ['reviewed', 'resolved', 'dismissed']:
                report.reviewed_by = 'admin'
                report.reviewed_at = created_at + timedelta(hours=random.randint(1, 72))

                # Generate realistic admin notes based on status
                if status == 'resolved':
                    report.admin_notes = random.choice([
                        'Fixed the error in question data. Updated correct answer.',
                        'Corrected typo and updated question text.',
                        'Updated question with current information.',
                        'Clarified question wording based on feedback.'
                    ])
                elif status == 'reviewed':
                    report.admin_notes = random.choice([
                        'Under review. Checking with subject matter expert.',
                        'Investigating the reported issue.',
                        'Needs verification before making changes.'
                    ])
                elif status == 'dismissed':
                    report.admin_notes = random.choice([
                        'Question is correct as written. Explanation added.',
                        'Unable to reproduce the reported issue.',
                        'Report appears to be based on misunderstanding.'
                    ])

            report_store.upsert(report.to_dict())
            report_count += 1

    # Add a few reports for questions that might not exist (edge cases)
    for i in range(min(3, num_reports - report_count)):
        days_ago = random.randint(0, 30)
        created_at = end_date - timedelta(days=days_ago, hours=random.randint(0, 23))

        report = QuestionReport(
            question_id=f'nonexistent_q_{i}',
            report_type='other',
            reason='Sample report for testing edge cases',
            user_name=random.choice(SAMPLE_NAMES),
            topic='test_topic',
            subtopic='test_subtopic',
            quiz_type='elimination',
            question_text='[Question no longer exists]',
            question_data={'sample': True, 'edge_case': True}
        )
        report.id = f'sample-report-edge-{i:04d}'
        report.created_at = created_at
        report.status = 'pending'

        report_store.upsert(report.to_dict())
        report_count += 1

    print(f"   ✅ Created {report_count} question reports")

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
    print(f"   • Question Reports: {report_count}")
    print(f"   • Date Range: Last 30 days")
    print(f"\n🌐 View the data:")
    print(f"   • Admin Dashboard: http://localhost:5000/admin/dashboard")
    print(f"   • Question Reports: http://localhost:5000/admin/question-reports")
    print(f"   • Question Analytics: http://localhost:5000/api/questions/analytics")
    print(f"   • API Summary: http://localhost:5000/api/statistics/overview")
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
