import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'XSXhll9WXqamJ3ADPKyyGxgTqvqY2cd-S9EHs5VzBcsJpduO25L438YlOUi_CqHGbEg')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'OjrbquxMUAOgZCttzDKmGSBS1lG6FxgTX04mSJQfg_F9qU4Iqw-EWf74-JKtHWiM0J43GP1sA4PBNRExwVV6UA')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))
   
    # File upload - Flask uses this to reject oversized requests before they
    # hit your route handler. 5 MB is a safe default for product images.
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # SQLite for development - database file will be in instance folder
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///instance/ecommerce_dev.db'
    )
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    database_url = os.getenv('DATABASE_URL')
    
    # Handle different database URL formats
    if database_url:
        # Heroku/Render postgres:// to postgresql:// conversion
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        # SQL Server URL is typically: mssql+pyodbc://user:pass@host:port/database?driver=...
        # No conversion needed for SQL Server URLs
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_ECHO = False
    
    # Database-specific engine options
    if database_url and 'postgresql' in database_url:
        # PostgreSQL-specific settings
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 10,
            'pool_recycle': 3600,
            'pool_timeout': 20,
            'pool_pre_ping': True,
            'max_overflow': 5
        }
    elif database_url and 'mssql' in database_url:
        # SQL Server-specific settings
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 10,
            'pool_recycle': 3600,
            'pool_timeout': 30,
            'pool_pre_ping': True,
            'max_overflow': 5,
            # SQL Server specific options
            'fast_executemany': True,
        }
    else:
        # Default engine options
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
        }

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}