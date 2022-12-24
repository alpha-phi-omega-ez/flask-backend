from . import db


# Backtest Subject Codes Table
class BacktestSubjectCode(db.Model):
    subject_code = db.Column(db.String(4), primary_key=True, unique=True)


# Backtest Classes Table
class BacktestClasses(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    subject_code = db.Column(db.String(4), nullable=False, unique=False)
    course_number = db.Column(db.Integer, nullable=False, unique=False)
    name_of_class = db.Column(db.String(100), nullable=False, unique=False)


# Backtest Table
class Backtest(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    subject_code = db.Column(db.String(4), nullable=False, unique=False)
    added = db.Column(db.DateTime, nullable=False, unique=False)
    course_number = db.Column(db.Integer, nullable=False, unique=False)
    exam = db.Column(db.Boolean, unique=False, default=False)
    quiz = db.Column(db.Boolean, unique=False, default=False)
    midterm = db.Column(db.Boolean, unique=False, default=False)
    year = db.Column(db.Integer, nullable=False, unique=False)
    semester = db.Column(db.String(1), nullable=False, unique=False)


# LAF Locations
class LAFLocations(db.Model):
    location = db.Column(db.String(50), primary_key=True, unique=True)


# Lost Reports Table
class LostReport(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(40), nullable=False, unique=False)
    last_name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(100), nullable=False, unique=False)
    phone_area_code = db.Column(db.Integer, nullable=False, unique=False)
    phone_middle = db.Column(db.Integer, nullable=False, unique=False)
    phone_end = db.Column(db.Integer, nullable=False, unique=False)
    