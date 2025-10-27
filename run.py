"""
Main Application Entry Point
Uses Application Factory pattern to create and run the Flask app
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from config import get_config

# Determine environment
config_name = os.environ.get('FLASK_ENV', 'development')

# Create app using factory
app = create_app(config_name)


def init_database():
    """Initialize database tables if they don't exist"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables initialized successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize database tables: {e}")
        print("   The application will continue, but database operations may fail.")


if __name__ == '__main__':
    # Get configuration
    config = get_config(config_name)
    
    # Initialize database tables
    init_database()
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║       IT Quizbee Application          ║
    ║     Design Pattern Architecture       ║
    ╚═══════════════════════════════════════╝
    
    Environment: {config_name}
    Host: {config.FLASK_HOST}
    Port: {config.FLASK_PORT}
    Debug: {config.DEBUG}
    Database: {config.DB_NAME}
    
    Design Patterns Implemented:
    🏭 Factory Pattern - App creation
    🧩 Blueprint Pattern - Modular routing
    ⚙️  Service Layer - Business logic
    🧱 Repository Pattern - Data access
    🧠 Decorator Pattern - Cross-cutting concerns
    🔁 Observer Pattern - Event system
    
    Starting server...
    """)
    
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.DEBUG)
