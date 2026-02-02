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
   
    # File upload – Flask uses this to reject oversized requests before they
    # hit your route handler.  5 MB is a safe default for product images.
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
    # PostgreSQL for production - must be provided via environment variable
    database_url = os.getenv('DATABASE_URL')
    
    # Handle Heroku postgres:// URL (convert to postgresql://)
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_ECHO = False
    
    # PostgreSQL-specific production settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_timeout': 20,
        'pool_pre_ping': True,  # Verify connections before using them
        'max_overflow': 5
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