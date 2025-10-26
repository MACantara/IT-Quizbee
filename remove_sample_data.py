"""
Script to remove sample quiz data from the database
Cleans up test data created by insert_sample_data.py
"""

import os
from dotenv import load_dotenv
from flask import Flask
from models import db, QuizSession, QuizAttempt, init_db

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

def remove_sample_data():
    """Remove all sample data from the database"""
    print("="*70)
    print("IT-QUIZBEE: Remove Sample Data")
    print("="*70)
    print()
    
    app = create_app()
    init_db(app)
    
    with app.app_context():
        # Count existing sample data
        sample_sessions = QuizSession.query.filter(
            QuizSession.id.like('sample-%')
        ).all()
        
        sample_attempts = QuizAttempt.query.filter(
            QuizAttempt.session_id.like('sample-%')
        ).all()
        
        if not sample_sessions and not sample_attempts:
            print("ℹ️  No sample data found in the database.")
            print("\n💡 To create sample data, run: python insert_sample_data.py")
            print("="*70)
            print()
            return
        
        print(f"📊 Found sample data:")
        print(f"   • Sessions: {len(sample_sessions)}")
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
        
        # Delete attempts first (due to foreign key constraint)
        attempts_deleted = QuizAttempt.query.filter(
            QuizAttempt.session_id.like('sample-%')
        ).delete(synchronize_session=False)
        
        # Delete sessions
        sessions_deleted = QuizSession.query.filter(
            QuizSession.id.like('sample-%')
        ).delete(synchronize_session=False)
        
        # Commit changes
        db.session.commit()
        
        print("\n" + "="*70)
        print("✅ SAMPLE DATA SUCCESSFULLY REMOVED!")
        print("="*70)
        print(f"\n📊 Deletion Summary:")
        print(f"   • Sessions Removed: {sessions_deleted}")
        print(f"   • Attempts Removed: {attempts_deleted}")
        print(f"\n🌐 Verify removal:")
        print(f"   • Admin Dashboard: http://localhost:5000/admin")
        print(f"   • API Summary: http://localhost:5000/api/analytics/summary")
        print("\n💡 To add sample data again, run: python insert_sample_data.py")
        print("="*70)
        print()

def remove_all_data():
    """Remove ALL data from the database (use with extreme caution)"""
    print("="*70)
    print("IT-QUIZBEE: Remove ALL Data (DANGEROUS)")
    print("="*70)
    print()
    
    app = create_app()
    init_db(app)
    
    with app.app_context():
        # Count all data
        all_sessions = QuizSession.query.count()
        all_attempts = QuizAttempt.query.count()
        
        if all_sessions == 0 and all_attempts == 0:
            print("ℹ️  Database is already empty.")
            print("="*70)
            print()
            return
        
        print(f"📊 Current database contents:")
        print(f"   • Total Sessions: {all_sessions}")
        print(f"   • Total Attempts: {all_attempts}")
        print()
        
        # Triple confirmation for deleting all data
        print("⚠️  DANGER: This will DELETE ALL quiz data from the database!")
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
        
        print("\n🗑️  Removing ALL data from database...")
        
        # Delete all attempts first
        attempts_deleted = QuizAttempt.query.delete()
        
        # Delete all sessions
        sessions_deleted = QuizSession.query.delete()
        
        # Commit changes
        db.session.commit()
        
        print("\n" + "="*70)
        print("✅ ALL DATA REMOVED!")
        print("="*70)
        print(f"\n📊 Deletion Summary:")
        print(f"   • Sessions Removed: {sessions_deleted}")
        print(f"   • Attempts Removed: {attempts_deleted}")
        print(f"\n⚠️  The database is now empty!")
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
        print("  1. Ensure MySQL server is running")
        print("  2. Verify database connection in .env file")
        print("  3. Check that the database exists")
