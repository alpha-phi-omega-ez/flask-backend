import sys
import random
from datetime import datetime

from apo import app, db
from apo.models import *

if sys.argv[1] == 'clear':
    with app.app_context():
        db.drop_all()
        db.create_all()

elif sys.argv[1] == 'create':
    with app.app_context():
        db.create_all()

        courses = [("CSCI", 1100, "Computer Science I"), ("CSCI", 1200, "Data Structures"), ("CSCI", 2200, "FOCS"), ("CSCI", 2500, "Computer Organizations"), ("CSCI", 2300, "Intro to Algo"), ("CSCI", 2500, "Principals of Software"), ("CSCI", 4210, "Operating Systems")]

        for bt_class in courses:
            print(f"Added {bt_class[0]} {bt_class[1]} {bt_class[2]}")
            new_backtest_class = BacktestClasses(
                subject_code=bt_class[0],
                course_number=bt_class[1],
                name_of_class=bt_class[2],
            )

            db.session.add(new_backtest_class)
            db.session.commit()

        courses2 = [("MATH", 1010, "Calculus I"), ("MATH", 1020, "Calculus II"), ("MATH", 2010, "Multivariable Calculus"), ("MATH", 2400, "Differential Equations")]

        for bt_class in courses2:
            print(f"Added {bt_class[0]} {bt_class[1]} {bt_class[2]}")
            new_backtest_class = BacktestClasses(
                subject_code=bt_class[0],
                course_number=bt_class[1],
                name_of_class=bt_class[2],
            )

            db.session.add(new_backtest_class)
            db.session.commit()
        
        for bt_class in courses:
            for j in range(0, 20):
                bt_type = random.choice(["exam", "quiz", "midterm", "exam", "exam", "quiz", "quiz", "quiz", "quiz", "quiz"])
                exam = False
                quiz = False
                midterm = False
                if bt_type == "exam":
                    exam = True
                elif bt_type == "quiz":
                    quiz = True
                else:
                    midterm = True
                    
                bt = Backtest(
                    subject_code = bt_class[0],
                    added = datetime.now(),
                    course_number = bt_class[1],
                    name_of_class = bt_class[2],
                    exam = exam,
                    quiz = quiz,
                    midterm = midterm,
                    year = random.choice([2016, 2017, 2018, 2019, 2020, 2021, 2022]),
                    semester = random.choice(["A","U", "Z"]),
                    backtest_number = random.choice([1, 2, 3, 4, 5, 6])
                )

                db.session.add(bt)
                db.session.commit()

        for bt_class in courses2:
            for j in range(0, 20):
                bt_type = random.choice(["exam", "quiz", "midterm", "exam", "exam", "quiz", "quiz", "quiz", "quiz", "quiz"])
                exam = False
                quiz = False
                midterm = False
                if bt_type == "exam":
                    exam = True
                elif bt_type == "quiz":
                    quiz = True
                else:
                    midterm = True
                    
                bt = Backtest(
                    subject_code = bt_class[0],
                    added = datetime.now(),
                    course_number = bt_class[1],
                    name_of_class = bt_class[2],
                    exam = exam,
                    quiz = quiz,
                    midterm = midterm,
                    year = random.choice([2016, 2017, 2018, 2019, 2020, 2021, 2022]),
                    semester = random.choice(["A","U", "Z"]),
                    backtest_number = random.choice([1, 2, 3, 4, 5, 6])
                )

                db.session.add(bt)
                db.session.commit()

else:
    sys.exit('No argument or exsisting argument found')