"""
Blueprints Package
Exports all blueprint instances
"""

from app.blueprints.quiz import quiz_bp
from app.blueprints.navigation import navigation_bp
from app.blueprints.api import api_bp

__all__ = [
    'quiz_bp',
    'navigation_bp',
    'api_bp'
]
