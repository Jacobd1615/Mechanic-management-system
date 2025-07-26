import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:240179@localhost/mechanic_db"
    DEBUG = True
    SECRET_KEY = "x"


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///testing.db"
    DEBUG = True
    CACHE_TYPE = "SimpleCache"


class ProductionConfig:
    # Render sets DATABASE_URL in environment, fallback to .env file
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        # Try to load from .env if not in environment
        load_dotenv()
        DATABASE_URL = os.environ.get("DATABASE_URL")

    print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")  # This will show in Render logs
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    CACHE_TYPE = "SimpleCache"
