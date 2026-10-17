"""
Centralized Configuration
Manages all application settings and database connections
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Server Configuration
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

    # File storage - quiz attempts and question reports persist as JSON here
    STORE_DIR = os.getenv('QUIZBEE_STORE_DIR', os.path.join(os.path.dirname(__file__), 'instance'))

    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'flask_session')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Admin Configuration
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Application Configuration
    QUESTIONS_PER_PAGE = 10
    MAX_QUIZ_TIME = 3600  # 1 hour in seconds
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED = True
    DEFAULT_RATE_LIMIT = "60/minute"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    FLASK_ENV = 'production'

    # Override with production-specific settings
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production

    # Stricter rate limiting in production
    DEFAULT_RATE_LIMIT = "30/minute"


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True

    # Tests point QUIZBEE_STORE_DIR at a temp directory via conftest

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name=None):
    """
    Get configuration object for specified environment
    
    Args:
        env_name: Environment name ('development', 'production', 'testing')
        
    Returns:
        Configuration class for the specified environment
    """
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env_name, config['default'])
