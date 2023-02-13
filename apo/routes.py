import os
import pathlib
from datetime import datetime

import google
import jwt
import requests
from flask import abort, jsonify, redirect, request, session, make_response
from flask_cors import CORS
from flask_restful import Resource, reqparse
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from apo.models import User, Backtest, BacktestClasses, Chargers

from apo import api, app, db

# bypass http
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = app.config["GOOGLE_CLIENT_ID"]
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client-secret.json")
algorithm = app.config["ALGORITHM"]
BACKEND_URL = app.config["BACKEND_URL"]
FRONTEND_URL = app.config["FRONTEND_URL"]
FOUR_HOURS = 60 * 60 * 4

users = []
global user


# flow = Flow.from_client_secrets_file(
#     client_secrets_file=client_secrets_file,
#     scopes=[
#         "https://www.googleapis.com/auth/userinfo.profile",
#         "https://www.googleapis.com/auth/userinfo.email",
#         "openid",
#     ],
#     redirect_uri=BACKEND_URL + "/callback",
# )


# wrapper
def login_required(function):
    def wrapper(*args, **kwargs):
        encoded_jwt = request.headers.get("Authorization").split("Bearer ")[1]
        if encoded_jwt is None:
            return abort(401)

        decoded_jwt = None
        try:
            decoded_jwt = jwt.decode(
                encoded_jwt,
                app.secret_key,
                algorithms=[
                    algorithm,
                ],
            )
        except Exception as e:
            return make_response(
                jsonify({"message": "Decoding JWT Failed", "exception": e.args}), 500
            )

        check = False
        for user in users:
            if decoded_jwt in user[0]:
                check = True

        if not check:
            abort(401)
        return function()

    return wrapper


def Generate_JWT(payload):
    encoded_jwt = jwt.encode(payload, app.secret_key, algorithm=algorithm)
    return encoded_jwt


class Callback(Resource):
    def get(self):
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        request_session = requests.session()
        token_request = google.auth.transport.requests.Request(session=request_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID,
        )
        session["google_id"] = id_info.get("sub")

        del id_info["aud"]
        jwt_token = Generate_JWT(id_info)
        now = datetime.now()

        check = False
        for user in users:
            if not check and user[0] == id_info:
                user[1] = now
                check = True

        users = [user for user in users if (now - user[1]).total_seconds() < FOUR_HOURS]

        if not check:
            users.append(list(id_info, now))

        check_user = User.query.filter_by(email=id_info.get("email")).first()
        if check_user is None:
            new_user = User(name=id_info.get("name"), email=id_info.get("email"))
            db.session.add(new_user)
            db.session.commit()
        return redirect(f"{FRONTEND_URL}?jwt={jwt_token}")


class GoogleAuth(Resource):
    def get(self):
        authorization_url, state = flow.authorization_url()
        # Store the state so the callback can verify the auth server response.
        session["state"] = state
        return make_response(jsonify({"auth_url": authorization_url}), 200)


class LogOut(Resource):
    def get(self):
        encoded_jwt = request.headers.get("Authorization").split("Bearer ")[1]
        if encoded_jwt is None:
            return abort(401)

        decoded_jwt = None
        try:
            decoded_jwt = jwt.decode(
                encoded_jwt,
                app.secret_key,
                algorithms=[
                    algorithm,
                ],
            )
        except Exception as e:
            return make_response(
                jsonify({"message": "Decoding JWT Failed", "exception": e.args}), 500
            )

        now = datetime.now()
        users = [
            user
            for user in users
            if (now - user[1]).total_seconds() < FOUR_HOURS or user[0] != decoded_jwt
        ]

        # clear the local storage from frontend
        session.clear()
        return make_response(jsonify({"message": "Logged out"}), 202)


class Home(Resource):
    # @login_required
    def get(self):
        return make_response(jsonify({"hello": "there"}), 200)


parser_backtest_classes = reqparse.RequestParser()
parser_backtest_classes.add_argument("subject_code", type=str, required=True)

parser_backtest_classes_post = reqparse.RequestParser()
parser_backtest_classes_post.add_argument("subject_code", type=str, required=True)
parser_backtest_classes_post.add_argument("course_number", type=int, required=True)
parser_backtest_classes_post.add_argument("name_of_course", type=str, required=True)


class BacktestClassesRoute(Resource):
    def get(self):
        args = parser_backtest_classes.parse_args()

        subject_code = args["subject_code"].upper().strip()
        if len(subject_code) != 4:
            return make_response(
                jsonify({"error": "Incorrect subject_code length passed in"}), 400
            )

        backtest_classes = BacktestClasses.query.filter_by(
            subject_code=subject_code
        ).all()
        backtest_classes = sorted(backtest_classes, key=lambda x: x.course_number)

        return make_response(
            jsonify(
                {
                    "classes": [
                        {
                            "names": f"{bt_class.course_number} - {bt_class.name_of_class}",
                            "course_number": bt_class.course_number,
                        }
                        for bt_class in backtest_classes
                    ]
                }
            ),
            200,
        )

    # @login_required
    def post(self):
        args = parser_backtest_classes_post.parse_args()

        subject_code = args["subject_code"].upper().strip()
        if len(subject_code) != 4:
            return make_response(
                jsonify({"error": "Incorrect subject_code length passed in"}), 400
            )

        course_number = args["course_number"]
        if len(str(course_number)) != 4:
            return make_response(
                jsonify({"error": "Incorrect course_number length passed in"}), 400
            )

        name_of_course = args["name_of_course"].strip().lower().title()

        backtest = BacktestClasses.query.filter_by(
            subject_code=subject_code,
            course_number=course_number,
            name_of_class=name_of_course,
        ).first()

        if backtest is not None:
            return make_response(jsonify({"error": "Class already exists"}), 400)

        new_backtest_class = BacktestClasses(
            subject_code=subject_code,
            course_number=course_number,
            name_of_class=name_of_course,
        )

        db.session.add(new_backtest_class)
        db.session.commit()

        return make_response(
            jsonify(
                {
                    "success": f"new backtest class {subject_code} {course_number} {name_of_course} created"
                }
            ),
            201,
        )


parser_backtest = reqparse.RequestParser()
parser_backtest.add_argument("subject_code", type=str, required=True)
parser_backtest.add_argument("course_number", type=int, required=True)

parser_backtest_post = reqparse.RequestParser()
parser_backtest_post.add_argument("subject_code", type=str, required=True)
parser_backtest_post.add_argument("course_number", type=int, required=True)
parser_backtest_post.add_argument("type", type=str, required=True)
parser_backtest_post.add_argument("backtest_number", type=int, required=True)
parser_backtest_post.add_argument("year", type=int, required=True)
parser_backtest_post.add_argument("semester", type=str, required=True)


class BacktestsRoute(Resource):
    def get(self):
        args = parser_backtest.parse_args()

        subject_code = args["subject_code"].upper().strip()
        if len(subject_code) != 4:
            return make_response(
                jsonify({"error": "Incorrect subject_code length passed in"}), 400
            )

        course_number = args["course_number"]
        if len(str(course_number)) != 4:
            return make_response(
                jsonify({"error": "Incorrect course_number length passed in"}), 400
            )

        backtests_exams = Backtest.query.filter_by(
            subject_code=subject_code, course_number=course_number, exam=True
        ).all()
        backtests_quizzes = Backtest.query.filter_by(
            subject_code=subject_code, course_number=course_number, quiz=True
        ).all()
        backtests_midterms = Backtest.query.filter_by(
            subject_code=subject_code, course_number=course_number, midterm=True
        ).all()

        if (
            backtests_exams is None
            and backtests_quizzes is None
            and backtests_midterms is None
        ):
            return make_response(
                jsonify({"error": "No backwork found for this class"}), 404
            )

        if backtests_exams is not None:
            backtests_exams = sorted(
                backtests_exams, key=lambda x: (x.year, x.semester), reverse=True
            )
        if backtests_quizzes is not None:
            backtests_quizzes = sorted(
                backtests_quizzes, key=lambda x: (x.year, x.semester), reverse=True
            )
        if backtests_midterms is not None:
            backtests_midterms = sorted(
                backtests_midterms, key=lambda x: (x.year, x.semester), reverse=True
            )

        exams = {}
        if backtests_exams is not None:
            for exam in backtests_exams:
                semester = ""
                if exam.semester == "A":
                    semester = "Spring"
                elif exam.semester == "U":
                    semester = "Summer"
                else:
                    semester = "Fall"

                if exam.backtest_number in exams:
                    exams[exam.backtest_number].append(f"{semester} {exam.year}")
                else:
                    exams[exam.backtest_number] = [f"{semester} {exam.year}"]
        else:
            exams = None

        quizzes = {}
        if backtests_quizzes is not None:
            for quiz in backtests_quizzes:
                semester = ""
                if quiz.semester == "A":
                    semester = "Spring"
                elif quiz.semester == "U":
                    semester = "Summer"
                else:
                    semester = "Fall"

                if quiz.backtest_number in quizzes:
                    quizzes[quiz.backtest_number].append(f"{semester} {quiz.year}")
                else:
                    quizzes[quiz.backtest_number] = [f"{semester} {quiz.year}"]
        else:
            quizzes = None

        midterms = {}
        if backtests_midterms is not None:
            for midterm in backtests_midterms:
                semester = ""
                if midterm.semester == "A":
                    semester = "Spring"
                elif midterm.semester == "U":
                    semester = "Summer"
                else:
                    semester = "Fall"

                if midterm.backtest_number in midterms:
                    midterms[midterm.backtest_number].append(
                        f"{semester} {midterm.year}"
                    )
                else:
                    midterms[midterm.backtest_number] = [f"{semester} {midterm.year}"]
        else:
            midterm = None

        return make_response(
            jsonify({"exams": exams, "quizzes": quizzes, "midterms": midterms}), 200
        )

    # @login_required
    def post(self):
        args = parser_backtest_post.parse_args()

        subject_code = args["subject_code"].upper().strip()
        if len(subject_code) != 4:
            return make_response(
                jsonify({"error": "Incorrect subject_code length passed in"}), 400
            )

        course_number = args["course_number"]
        if len(str(course_number)) != 4:
            return make_response(
                jsonify({"error": "Incorrect course_number length passed in"}), 400
            )

        year = args["year"]
        if len(str(year)) != 4:
            return make_response(
                jsonify({"error": "Incorrect year length passed in"}), 400
            )

        semester = args["semester"].upper().strip()
        if len(semester) != 1:
            return make_response(
                jsonify({"error": "Incorrect semester length passed in"}), 400
            )
        if semester not in ["A", "U", "Z"]:
            return make_response(
                jsonify(
                    {
                        "error": "Incorrect semester type, A for Spring, U for Summer, and Z for Fall"
                    }
                ),
                400,
            )

        backwork_type = args["type"].upper().strip()
        if backwork_type not in ["EXAM", "QUIZ", "MIDTERM"]:
            return make_response(
                jsonify(
                    {
                        "error": "unrecognized backwork_type, acceptable types are exam, quiz, or midterm"
                    }
                ),
                400,
            )

        backtest_number = args["backtest_number"]

        new_backtest = None

        exam = False
        quiz = False
        midterm = False

        if backwork_type == "EXAM":
            exam = True
        elif backwork_type == "QUIZ":
            quiz = True
        else:
            midterm = True

        now = datetime.now()
        backtests_class = BacktestClasses.query.filter_by(
            subject_code=subject_code, course_number=course_number
        ).first()

        if backtests_class is None:
            return make_response(jsonify({"error": "Course not found"}), 404)

        name_of_class = backtests_class.name_of_class

        new_backtest = Backtest(
            subject_code=subject_code,
            added=now,
            course_number=course_number,
            name_of_class=name_of_class,
            exam=exam,
            quiz=quiz,
            midterm=midterm,
            year=year,
            semester=semester,
            backtest_number=backtest_number,
        )

        db.session.add(new_backtest)
        db.session.commit()

        return make_response(
            jsonify(
                {
                    "success": f"new backtest {subject_code} {course_number} {semester} {year} created"
                }
            ),
            201,
        )


class ChargersInventory(Resource):
    def get(self):
        chargers = Chargers.query.all()
        return make_response(
            jsonify({"chargers": [charger.description for charger in chargers]}), 200
        )


parser_charger = reqparse.RequestParser()
parser_charger.add_argument("charger_id", type=int, required=False)

parser_charger_post = reqparse.RequestParser()
parser_charger_post.add_argument("charger_id", type=int, required=True)
parser_charger_post.add_argument("in_office", type=bool, required=True)


class ChargersInventoryBrothers(Resource):
    # @login_required
    def get(self):
        args = parser_charger_post.parse_args()
        charger_id = args["charger_id"]

        if charger_id is not None:
            charger = Chargers.query.get(charger_id)
            if charger is None:
                return make_response(jsonify({"error": "charger not found"}), 404)
            return make_response(
                jsonify(
                    {
                        "charger": [
                            charger.description,
                            charger.checked_out,
                            charger.in_office,
                        ]
                    }
                ),
                200,
            )

        chargers = Chargers.query.all()
        return make_response(
            jsonify(
                {
                    "chargers": [
                        [charger.description, charger.checked_out, charger.in_office]
                        for charger in chargers
                    ]
                }
            ),
            200,
        )

    # @login_required
    def post(self):
        args = parser_charger_post.parse_args()

        charger_id = args["charger_id"]
        in_office = args["in_office"]

        charger = Chargers.query.get(charger_id)
        if charger is None:
            return make_response(jsonify({"error": "charger not found"}), 404)

        charger.in_office = in_office

        db.session.commit()

        return make_response(jsonify({"success": "charger status updated"}), 200)


api.add_resource(Home, "/home")
api.add_resource(LogOut, "/logout")
api.add_resource(GoogleAuth, "/auth/google")
api.add_resource(Callback, "/callback")
api.add_resource(BacktestClassesRoute, "/backtest/classes")
api.add_resource(BacktestsRoute, "/backtest/")
api.add_resource(ChargersInventory, "/chargers/")
api.add_resource(ChargersInventoryBrothers, "/chargers/status")
