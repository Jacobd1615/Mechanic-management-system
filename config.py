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
    # Load environment variables
    load_dotenv()  # Load from .env file if it exists

    DATABASE_URL = os.environ.get("DATABASE_URL")
    CACHE_TYPE = "SimpleCache"
