"""
Database initialization script for IT-Quizbee
Creates necessary tables and indexes in MySQL
"""

import os
from dotenv import load_dotenv
from flask import Flask
from models import db, init_db

# Load environment variables
load_dotenv()

def create_app():
    """Create Flask app for database initialization"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configure MySQL database connection
    mysql_url = os.environ.get('MYSQL_PUBLIC_URL')
    if mysql_url:
        # Convert mysql:// to mysql+pymysql://
        if mysql_url.startswith('mysql://'):
            mysql_url = mysql_url.replace('mysql://', 'mysql+pymysql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = mysql_url
    else:
        # Fallback for local development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/itquizbee'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'echo': False
    }
    
    return app

def initialize_database():
    """Initialize the database with all tables"""
    print("="*70)
    print("IT-QUIZBEE: Database Initialization")
    print("="*70)
    
    try:
        app = create_app()
        
        # Initialize database
        init_db(app)
        
        print("\n✅ Database initialized successfully!")
        print("\nCreated tables:")
        print("  • quiz_sessions - Stores active quiz sessions")
        print("  • quiz_attempts - Stores quiz submission results")
        
        print("\nDatabase configuration:")
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if '@' in db_uri:
            print(f"  • Database: {db_uri.split('@')[1]}")
        print(f"  • Track Modifications: {app.config['SQLALCHEMY_TRACK_MODIFICATIONS']}")
        print(f"  • Pool Pre-ping: Enabled (connection verification)")
        print(f"  • Pool Recycle: 3600 seconds")
        
        print("\n" + "="*70)
        print("✨ Database is ready for use!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure MySQL server is running")
        print("  2. Verify MYSQL_PUBLIC_URL in .env file")
        print("  3. Check database credentials")
        print("  4. Ensure the database exists")
        return False
    
    return True

if __name__ == '__main__':
    initialize_database()