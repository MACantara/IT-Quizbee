"""
Script to remove sample quiz data from the JSON file store
Cleans up test data created by insert_sample_data.py
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


def remove_sample_data():
    """Remove all sample data from the JSON store"""
    print("="*70)
    print("IT-QUIZBEE: Remove Sample Data")
    print("="*70)
    print()

    attempt_repo = QuizAttemptRepository()

    # Count existing sample data
    sample_attempts = [
        a for a in attempt_repo.get_all()
        if str(a.session_id or '').startswith('sample-')
    ]

    if not sample_attempts:
        print("ℹ️  No sample data found in the store.")
        print("\n💡 To create sample data, run: python scripts/insert_sample_data.py")
        print("="*70)
        print()
        return

    print(f"📊 Found sample data:")
    print(f"   • Attempts: {len(sample_attempts)}")
    print()

    # Confirm deletion
    print("⚠️  WARNING: This will permanently delete all sample data!")
    print("   This action cannot be undone.")
    print()
    response = input("Type 'DELETE' to confirm removal: ").strip()

    if response != 'DELETE':
        print("\n❌ Operation cancelled. No data was removed.")
        print("="*70)
        print()
        return

    print("\n🗑️  Removing sample data...")

    # Delete sample attempts (session_id starting with 'sample-')
    attempts_deleted = attempt_repo.delete_sample_attempts()

    print("\n" + "="*70)
    print("✅ SAMPLE DATA SUCCESSFULLY REMOVED!")
    print("="*70)
    print(f"\n📊 Deletion Summary:")
    print(f"   • Attempts Removed: {attempts_deleted}")
    print("\n💡 To add sample data again, run: python scripts/insert_sample_data.py")
    print("="*70)
    print()

def remove_all_data():
    """Remove ALL data from the JSON store (use with extreme caution)"""
    print("="*70)
    print("IT-QUIZBEE: Remove ALL Data (DANGEROUS)")
    print("="*70)
    print()

    attempt_repo = QuizAttemptRepository()

    all_attempts = len(attempt_repo.get_all())

    if all_attempts == 0:
        print("ℹ️  Store is already empty.")
        print("="*70)
        print()
        return

    print(f"📊 Current store contents:")
    print(f"   • Total Attempts: {all_attempts}")
    print()

    # Triple confirmation for deleting all data
    print("⚠️  DANGER: This will DELETE ALL quiz data from the store!")
    print("   This includes both sample data AND real quiz attempts!")
    print("   This action is PERMANENT and CANNOT be undone!")
    print()

    response1 = input("Are you absolutely sure? Type 'YES' to continue: ").strip()
    if response1 != 'YES':
        print("\n❌ Operation cancelled.")
        return

    response2 = input("Type 'DELETE ALL DATA' to confirm: ").strip()
    if response2 != 'DELETE ALL DATA':
        print("\n❌ Operation cancelled.")
        return

    print("\n🗑️  Removing ALL data from store...")

    attempts_deleted = attempt_repo.store.delete_where(lambda r: True)

    print("\n" + "="*70)
    print("✅ ALL DATA REMOVED!")
    print("="*70)
    print(f"\n📊 Deletion Summary:")
    print(f"   • Attempts Removed: {attempts_deleted}")
    print(f"\n⚠️  The store is now empty!")
    print("="*70)
    print()

if __name__ == '__main__':
    import sys

    try:
        # Check for --all flag to remove all data
        if '--all' in sys.argv:
            print("\n⚠️  WARNING: You are about to remove ALL data!\n")
            remove_all_data()
        else:
            remove_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify QUIZBEE_STORE_DIR in .env points to a writable directory")
        print("  2. Run from the project root directory")
