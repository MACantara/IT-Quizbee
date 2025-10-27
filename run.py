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

# Determine environment
config_name = os.environ.get('FLASK_ENV', 'development')

# Create app using factory
app = create_app(config_name)

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║       IT Quizbee Application          ║
    ║     Design Pattern Architecture       ║
    ╚═══════════════════════════════════════╝
    
    Environment: {config_name}
    Host: {host}
    Port: {port}
    Debug: {debug}
    
    Design Patterns Implemented:
    🏭 Factory Pattern - App creation
    🧩 Blueprint Pattern - Modular routing
    ⚙️  Service Layer - Business logic
    🧱 Repository Pattern - Data access
    🧠 Decorator Pattern - Cross-cutting concerns
    🔁 Observer Pattern - Event system
    
    Starting server...
    """)
    
    app.run(host=host, port=port, debug=debug)
