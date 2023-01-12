from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)


# Backtest Classes Table
class BacktestClasses(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    subject_code = db.Column(db.String(4), nullable=False, unique=False)
    course_number = db.Column(db.Integer, nullable=False, unique=False)
    name_of_class = db.Column(db.String(100), nullable=False, unique=False)


# Backtest Table
# Spring semester denoted a for proper sorting
class Backtest(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    subject_code = db.Column(db.String(4), nullable=False, unique=False)
    added = db.Column(db.DateTime, nullable=False, unique=False)
    course_number = db.Column(db.Integer, nullable=False, unique=False)
    name_of_class = db.Column(db.String(100), nullable=False, unique=False)
    exam = db.Column(db.Boolean, unique=False, default=False)
    quiz = db.Column(db.Boolean, unique=False, default=False)
    midterm = db.Column(db.Boolean, unique=False, default=False)
    year = db.Column(db.Integer, nullable=False, unique=False)
    semester = db.Column(db.String(1), nullable=False, unique=False)
    backtest_number = db.Column(db.Integer, nullable=False, unique=False)


# Backtest Table
# Spring semester denoted a for proper sorting
class Chargers(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    in_office = db.Column(db.Boolean, nullable=False, unique=False)
    checked_out = db.Column(db.DateTime, nullable=False, unique=False)
    description = db.Column(db.Text, nullable=False, unique=False)


# Lost Reports Table
class LostReport(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(40), nullable=False, unique=False)
    last_name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(100), nullable=False, unique=False)
    phone_area_code = db.Column(db.Integer, nullable=False, unique=False)
    phone_middle = db.Column(db.Integer, nullable=False, unique=False)
    phone_end = db.Column(db.Integer, nullable=False, unique=False)
    description = db.Column(db.Text, nullable=False, unique=False)
    item_type = db.Column(db.String(15), nullable=False, unique=False)
    date_lost = db.Column(db.Date, nullable=False, unique=False)
