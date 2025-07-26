import os

from dotenv import load_dotenv

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
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SECRET_KEY = os.environ.get("SECRET_KEY", "super secret secrets")
    print(
        f"DEBUG: SQLALCHEMY_DATABASE_URI = {SQLALCHEMY_DATABASE_URI}"
    )  # This will show in Render logs

    CACHE_TYPE = "SimpleCache"
