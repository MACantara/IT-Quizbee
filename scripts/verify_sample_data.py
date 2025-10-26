"""
Quick verification script to check sample data in the database
Displays summary without needing to open the browser
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask

# Add parent directory to path to import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
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

def verify_sample_data():
    """Verify sample data exists and show summary"""
    print("="*70)
    print("IT-QUIZBEE: Sample Data Verification")
    print("="*70)
    print()
    
    app = create_app()
    init_db(app)
    
    with app.app_context():
        # Count sample data
        sample_sessions = QuizSession.query.filter(
            QuizSession.id.like('sample-%')
        ).all()
        
        sample_attempts = QuizAttempt.query.filter(
            QuizAttempt.session_id.like('sample-%')
        ).all()
        
        # Count all data
        total_sessions = QuizSession.query.count()
        total_attempts = QuizAttempt.query.count()
        
        print("📊 Database Overview:")
        print(f"   • Total Sessions: {total_sessions}")
        print(f"   • Total Attempts: {total_attempts}")
        print()
        
        print("🧪 Sample Data:")
        print(f"   • Sample Sessions: {len(sample_sessions)}")
        print(f"   • Sample Attempts: {len(sample_attempts)}")
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
        
        elimination_count = sum(1 for a in sample_attempts if a.quiz_mode == 'elimination_full')
        finals_count = sum(1 for a in sample_attempts if a.quiz_mode == 'finals_full')
        review_count = sum(1 for a in sample_attempts if a.quiz_mode == 'review')
        
        print(f"   • Elimination: {elimination_count} attempts")
        print(f"   • Finals: {finals_count} attempts")
        print(f"   • Review: {review_count} attempts")
        print()
        
        # Score statistics
        if sample_attempts:
            scores = [a.score_percentage for a in sample_attempts]
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
        real_attempts = total_attempts - len(sample_attempts)
        if real_attempts > 0:
            print("⚠️  Warning:")
            print(f"   • Found {real_attempts} real (non-sample) attempts")
            print("   • Be careful when using 'remove_sample_data.py --all'")
            print()
        
        print("🌐 Next Steps:")
        print("   • View Dashboard: http://localhost:5000/admin")
        print("   • View API: http://localhost:5000/api/analytics/summary")
        print("   • Remove Sample: python scripts/remove_sample_data.py")
        print()
        print("="*70)

if __name__ == '__main__':
    try:
        verify_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure MySQL server is running")
        print("  2. Verify database connection in .env file")
        print("  3. Run 'python scripts/init_db.py' first")
        print()
