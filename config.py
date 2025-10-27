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
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'quizbee')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
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
    
    # Question Analytics Configuration
    MIN_ATTEMPTS_FOR_ANALYTICS = 3  # Minimum attempts required for success rate calculation
    DEFAULT_ANALYTICS_LIMIT = 20  # Default number of questions to return in analytics
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED = True
    DEFAULT_RATE_LIMIT = "60/minute"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    FLASK_ENV = 'development'
    
    # Use MYSQL_PUBLIC_URL if available, otherwise fallback to DEV_DATABASE_URL or localhost
    mysql_url = os.getenv('MYSQL_PUBLIC_URL') or os.getenv('DEV_DATABASE_URL') or \
        f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8mb4"
    
    # Convert mysql:// to mysql+pymysql:// if needed
    if mysql_url.startswith('mysql://'):
        mysql_url = mysql_url.replace('mysql://', 'mysql+pymysql://', 1)
    
    SQLALCHEMY_DATABASE_URI = mysql_url


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    FLASK_ENV = 'production'
    
    # Override with production-specific settings
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    
    # Use DATABASE_URL first, then MYSQL_PUBLIC_URL, then fallback to constructed URL
    mysql_url = os.getenv('DATABASE_URL') or os.getenv('MYSQL_PUBLIC_URL') or \
        f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8mb4"
    
    # Convert mysql:// to mysql+pymysql:// if needed
    if mysql_url.startswith('mysql://'):
        mysql_url = mysql_url.replace('mysql://', 'mysql+pymysql://', 1)
    
    SQLALCHEMY_DATABASE_URI = mysql_url
    
    # Use Redis for sessions in production
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Set Redis connection in production
    
    # Stricter rate limiting in production
    DEFAULT_RATE_LIMIT = "30/minute"


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    
    # Use separate test database
    DB_NAME = os.getenv('TEST_DB_NAME', 'quizbee_test')
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@"
        f"{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )
    
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
