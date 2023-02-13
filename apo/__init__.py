from flask import Flask
from config import TestingConfig#, ProductionConfig
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(TestingConfig)
app.config["Access-Control-Allow-Origin"] = "*"
app.config["Access-Control-Allow-Headers"] = "Content-Type"
api = Api(app)
db = SQLAlchemy(app, session_options={'expire_on_commit': False})

import apo.routes
