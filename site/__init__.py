# Flask imports
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2 import WebApplicationClient

# Create Flask app
app = Flask(__name__)

# Add Configurations to app
app.config.from_pyfile("config.py", silent=True)

# Create Database object from brcrypt object
db = SQLAlchemy(app)

# Create Login manager
login_manager = LoginManager(app)

# OAuth 2 client setup
google_client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])

# Importing all the models and initializing them
from site.models import *
db.create_all()

# Import all views
import site.views
