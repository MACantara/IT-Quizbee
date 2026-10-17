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
from config import get_config

# Determine environment
config_name = os.environ.get('FLASK_ENV', 'development')

# Create app using factory
app = create_app(config_name)


if __name__ == '__main__':
    # Get configuration
    config = get_config(config_name)

    print(f"""
    =======================================
           IT Quizbee Application
    =======================================

    Environment: {config_name}
    Host: {config.FLASK_HOST}
    Port: {config.FLASK_PORT}
    Debug: {config.DEBUG}
    Store: {config.STORE_DIR}

    Starting server...
    """)
    
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.DEBUG)
