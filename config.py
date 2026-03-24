import os

class Config:
    SECRET_KEY = SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback')
    TESTING    = False

class DevelopmentConfig(Config):
    DEBUG      = True
    TESTING    = False
    CACHE_TYPE = 'SimpleCache'  # Use in-memory cache for development

class TestingConfig(Config):
    DEBUG      = False
    TESTING    = True
    CACHE_TYPE = 'NullCache'  # Disable caching for testing

class ProductionConfig(Config):
    DEBUG      = False
    TESTING    = False
    CACHE_TYPE = 'RedisCache'  # Use Redis for production caching
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

config = {
    'development': DevelopmentConfig,
    'testing'    : TestingConfig,
    'production' : ProductionConfig,
    'default'    : DevelopmentConfig
}