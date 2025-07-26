import os


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:240179@localhost/mechanic_db"
    DEBUG = True
    SECRET_KEY = "x"


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///testing.db"
    DEBUG = True
    CACHE_TYPE = "SimpleCache"


class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")  # Render uses DATABASE_URL
    CACHE_TYPE = "SimpleCache"
