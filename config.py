# Import os
import os

SECRET_KEY = os.urandom(32)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
TESTING = True
DEBUG = True

# Using Postgresql
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', )
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_COMMIT_ON_TEARDOWN = True