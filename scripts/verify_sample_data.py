"""
Quick verification script to check sample data in the JSON file store
Displays summary without needing to open the browser
"""

import os
import sys
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
from app.repositories.question_report_repository import QuestionReportRepository


def verify_sample_data():
    """Verify sample data exists and show summary"""
    print("="*70)
    print("IT-QUIZBEE: Sample Data Verification")
    print("="*70)
    print()

    attempt_repo = QuizAttemptRepository()
    report_store = QuestionReportRepository._get_store()

    # Count sample data
    all_attempts = attempt_repo.get_all()
    sample_attempts = [
        a for a in all_attempts
        if str(a.session_id or '').startswith('sample-')
    ]

    all_reports = QuestionReportRepository.get_all()
    sample_reports = [
        r for r in all_reports
        if str(r.id or '').startswith('sample-')
    ]

    print("📊 Store Overview:")
    print(f"   • Total Attempts: {len(all_attempts)}")
    print(f"   • Total Question Reports: {len(all_reports)}")
    print()

    print("🧪 Sample Data:")
    print(f"   • Sample Attempts: {len(sample_attempts)}")
    print(f"   • Sample Question Reports: {len(sample_reports)}")
    print()

    if len(sample_attempts) == 0:
        print("ℹ️  No sample data found.")
        print()
        print("💡 To create sample data:")
        print("   python scripts/insert_sample_data.py")
        print()
        print("="*70)
        return

    # Breakdown by mode
    print("📋 Sample Attempts by Mode:")

    elimination_count = sum(1 for a in sample_attempts if a.quiz_type == 'elimination')
    finals_count = sum(1 for a in sample_attempts if a.quiz_type == 'finals')
    review_elimination = sum(1 for a in sample_attempts if a.quiz_type == 'review_elimination')
    review_finals = sum(1 for a in sample_attempts if a.quiz_type == 'review_finals')

    print(f"   • Elimination: {elimination_count} attempts")
    print(f"   • Finals: {finals_count} attempts")
    print(f"   • Review (Elimination): {review_elimination} attempts")
    print(f"   • Review (Finals): {review_finals} attempts")
    print()

    # Question reports breakdown
    if sample_reports:
        print("📝 Sample Question Reports:")
        pending = sum(1 for r in sample_reports if r.status == 'pending')
        reviewed = sum(1 for r in sample_reports if r.status == 'reviewed')
        resolved = sum(1 for r in sample_reports if r.status == 'resolved')
        dismissed = sum(1 for r in sample_reports if r.status == 'dismissed')

        print(f"   • Pending: {pending}")
        print(f"   • Reviewed: {reviewed}")
        print(f"   • Resolved: {resolved}")
        print(f"   • Dismissed: {dismissed}")

        # Report types breakdown
        if len(sample_reports) > 0:
            report_types_count = {}
            for r in sample_reports:
                report_types_count[r.report_type] = report_types_count.get(r.report_type, 0) + 1

            print(f"\n   Report Types:")
            for rtype, count in sorted(report_types_count.items(), key=lambda x: x[1], reverse=True):
                print(f"      - {rtype}: {count}")
        print()

    # Score statistics
    if sample_attempts:
        scores = [a.score for a in sample_attempts]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)

        print("📈 Score Statistics:")
        print(f"   • Average: {avg_score:.1f}%")
        print(f"   • Minimum: {min_score:.1f}%")
        print(f"   • Maximum: {max_score:.1f}%")
        print()

    # Date range
    if sample_attempts:
        dates = [a.created_at for a in sample_attempts]
        oldest = min(dates)
        newest = max(dates)

        print("📅 Date Range:")
        print(f"   • Oldest: {oldest.strftime('%Y-%m-%d %H:%M')}")
        print(f"   • Newest: {newest.strftime('%Y-%m-%d %H:%M')}")
        print()

    # Real data (non-sample)
    real_attempts = len(all_attempts) - len(sample_attempts)
    real_reports = len(all_reports) - len(sample_reports)
    if real_attempts > 0 or real_reports > 0:
        print("⚠️  Warning:")
        if real_attempts > 0:
            print(f"   • Found {real_attempts} real (non-sample) attempts")
        if real_reports > 0:
            print(f"   • Found {real_reports} real (non-sample) question reports")
        print("   • Be careful when using 'remove_sample_data.py --all'")
        print()

    print("🌐 Next Steps:")
    print("   • View Dashboard: http://localhost:5000/admin/dashboard")
    print("   • View Question Reports: http://localhost:5000/admin/question-reports")
    print("   • Question Analytics: http://localhost:5000/api/questions/analytics")
    print("   • API Overview: http://localhost:5000/api/statistics/overview")
    print("   • Remove Sample: python scripts/remove_sample_data.py")
    print()
    print("="*70)

if __name__ == '__main__':
    try:
        verify_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify QUIZBEE_STORE_DIR in .env points to a writable directory")
        print("  2. Run from the project root directory")
        print()
