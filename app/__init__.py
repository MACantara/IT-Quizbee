"""
Application Factory
Creates and configures Flask application instance
"""

import os
from flask import Flask
from flask_session import Session

# Import extensions
from models import db

# Import blueprints
from app.blueprints import admin_bp, quiz_bp, navigation_bp, api_bp

# Import event system
from app.events.event_manager import event_manager
from app.events.observers import (
    LoggingObserver,
    AnalyticsObserver,
    NotificationObserver,
    PerformanceMonitor
)


def create_app(config_name='development'):
    """
    Application Factory
    
    Creates and configures Flask application instance with:
    - Database configuration
    - Session management
    - Blueprint registration
    - Event system initialization
    
    Args:
        config_name: Configuration environment ('development', 'testing', 'production')
        
    Returns:
        Configured Flask app instance
    """
    # Create Flask app
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )
    
    # Load configuration
    app.config.from_object(get_config(config_name))
    
    # Validate production config
    if config_name == 'production' and not app.config.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize event system
    init_event_system()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    return app


def get_config(config_name):
    """
    Get configuration object based on environment
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configuration object
    """
    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    return configs.get(config_name, DevelopmentConfig)


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours
    
    # Quiz settings
    QUIZ_TIME_LIMIT = 900  # 15 minutes in seconds
    QUESTIONS_PER_ELIMINATION = 10
    QUESTIONS_PER_FINALS = 5
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:password@localhost/it_quizbee'
    SQLALCHEMY_ECHO = True  # Log SQL queries


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_TYPE = 'null'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/it_quizbee_prod'
    
    # Use Redis for sessions in production
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Set Redis connection in production
    
    # Stronger secret key required (will be validated in create_app)
    SECRET_KEY = os.environ.get('SECRET_KEY')


def init_extensions(app):
    """
    Initialize Flask extensions
    
    Args:
        app: Flask application instance
    """
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Session
    Session(app)
    
    # Create database tables if they don't exist (only in app context, not during import)
    # This will be called when the app is run, not during import
    # with app.app_context():
    #     db.create_all()


def register_blueprints(app):
    """
    Register all blueprints
    
    Args:
        app: Flask application instance
    """
    # Register admin blueprint
    app.register_blueprint(admin_bp)
    
    # Register quiz blueprint
    app.register_blueprint(quiz_bp)
    
    # Register navigation blueprint
    app.register_blueprint(navigation_bp)
    
    # Register API blueprint
    app.register_blueprint(api_bp)


def init_event_system():
    """Initialize event system with observers"""
    from app.events.event_manager import EventType
    
    # Create observers
    logging_observer = LoggingObserver()
    analytics_observer = AnalyticsObserver()
    notification_observer = NotificationObserver()
    performance_monitor = PerformanceMonitor()
    
    # Subscribe logging observer to specific events
    event_manager.subscribe(EventType.QUIZ_STARTED, logging_observer.on_quiz_started)
    event_manager.subscribe(EventType.QUIZ_COMPLETED, logging_observer.on_quiz_completed)
    event_manager.subscribe(EventType.HIGH_SCORE_ACHIEVED, logging_observer.on_high_score)
    
    # Subscribe analytics observer to quiz completed events
    event_manager.subscribe(EventType.QUIZ_COMPLETED, analytics_observer.on_quiz_completed)
    
    # Subscribe notification observer to important events
    event_manager.subscribe(EventType.HIGH_SCORE_ACHIEVED, notification_observer.on_high_score)
    event_manager.subscribe(EventType.QUIZ_COMPLETED, notification_observer.on_quiz_completed)
    
    # Subscribe performance monitor to quiz events
    event_manager.subscribe(EventType.QUIZ_STARTED, performance_monitor.on_quiz_started)
    event_manager.subscribe(EventType.QUIZ_COMPLETED, performance_monitor.on_quiz_completed)


def register_error_handlers(app):
    """
    Register error handlers
    
    Args:
        app: Flask application instance
    """
    from flask import render_template, jsonify, request
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403


def register_cli_commands(app):
    """
    Register CLI commands
    
    Args:
        app: Flask application instance
    """
    import click
    
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        db.create_all()
        click.echo('Database initialized!')
    
    @app.cli.command()
    def cleanup():
        """Cleanup expired quiz sessions"""
        from app.services import QuizService
        from app.repositories import QuizSessionRepository, QuizAttemptRepository
        
        session_repo = QuizSessionRepository(db.session)
        attempt_repo = QuizAttemptRepository(db.session)
        quiz_service = QuizService(session_repo, attempt_repo)
        
        count = quiz_service.cleanup_expired_sessions()
        click.echo(f'Cleaned up {count} expired sessions!')
    
    @app.cli.command()
    @click.option('--days', default=30, help='Number of days for statistics')
    def stats(days):
        """Display analytics statistics"""
        from app.services import AnalyticsService
        from app.repositories import QuizAttemptRepository
        
        attempt_repo = QuizAttemptRepository(db.session)
        analytics_service = AnalyticsService(attempt_repo)
        
        stats_data = analytics_service.get_dashboard_statistics(days=days)
        
        click.echo('\n=== IT Quizbee Statistics ===')
        click.echo(f"Period: Last {days} days\n")
        
        overview = stats_data.get('overview', {})
        click.echo(f"Total Attempts: {overview.get('total_attempts', 0)}")
        click.echo(f"Average Score: {overview.get('average_score', 0)}%")
        click.echo(f"Pass Rate: {overview.get('pass_rate', 0)}%")
        click.echo(f"Average Time: {overview.get('average_time', 0)}s")


# Export for easy import
__all__ = ['create_app']
