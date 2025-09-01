"""
Deployment Configuration for OLynk AI MVP
Phase 3: Week 11 - Production Deployment
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    
    # Database configuration (for future use)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///olynk.db'
    
    # File storage
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/olynk.log'
    
    # Performance
    WORKERS = 4
    TIMEOUT = 30
    
    # Monitoring
    ENABLE_MONITORING = True
    METRICS_ENDPOINT = '/metrics'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required for production")
    
    # Production database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required for production")
    
    # Production file storage
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/var/olynk/uploads'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/olynk/olynk.log'
    
    # Production performance
    WORKERS = int(os.environ.get('WORKERS', 4))
    TIMEOUT = int(os.environ.get('TIMEOUT', 30))
    
    # SSL/TLS
    SSL_CONTEXT = ('cert.pem', 'key.pem') if os.path.exists('cert.pem') else None

class StagingConfig(Config):
    """Staging configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'INFO'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])
