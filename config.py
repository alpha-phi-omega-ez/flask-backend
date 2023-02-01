# Import os
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class TestingConfig():
    SECRET_KEY = os.urandom(32)
    TESTING = True
    DEBUG = True

    # Using SQLLITE locally
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    ALGORITHM = "ES256K"
    #PROJECT_ID =
    BACKEND_URL = "http://127.0.0.1:8000"
    FRONTEND_URL = "http://localhost:3000"

class ProductionConfig(TestingConfig):
    #SQLALCHEMY_DATABASE_URI = ""
    
    BACKEND_URL = "http://127.0.0.1:8000"
    FRONTEND_URL = "http://localhost:3000"