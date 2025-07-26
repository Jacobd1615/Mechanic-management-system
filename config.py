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
    DATABASE_URL = os.environ.get("DATABASE_URL")
    print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")  # This will show in Render logs
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    CACHE_TYPE = "SimpleCache"
