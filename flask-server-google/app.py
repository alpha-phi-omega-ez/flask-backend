import os
import pathlib
from datetime import datetime

import google
import jwt
import requests
from flask import abort, jsonify, redirect, request, session
from flask_cors import CORS
from flask_restful import Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from models import Backtest, BacktestClasses, BacktestSubjectCode

from . import api, app, db

# bypass http
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = app.config["GOOGLE_CLIENT_ID"]
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client-secret.json")
algorithm = app.config["ALGORITHM"]
BACKEND_URL = app.config["BACKEND_URL"]
FRONTEND_URL = app.config["FRONTEND_URL"]


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri=BACKEND_URL + "/callback",
)


# wrapper
def login_required(function):
    def wrapper(*args, **kwargs):
        encoded_jwt = request.headers.get("Authorization").split("Bearer ")[1]
        if encoded_jwt == None:
            return abort(401)
        else:
            return function()

    return wrapper


def Generate_JWT(payload):
    encoded_jwt = jwt.encode(payload, app.secret_key, algorithm=algorithm)
    return encoded_jwt


class Callback(Resource):
    def post(self):
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

        # removing the specific audience, as it is throwing error
        del id_info["aud"]
        jwt_token = Generate_JWT(id_info)
        # insert_into_db(id_info.get("name"), id_info.get("email"), id_info.get("picture"))
        # add sql alchemy things
        return redirect(f"{FRONTEND_URL}?jwt={jwt_token}")


class GoogleAuth(Resource):
    def get(self):
        authorization_url, state = flow.authorization_url()
        # Store the state so the callback can verify the auth server response.
        session["state"] = state
        return jsonify({"auth_url": authorization_url}), 200


class LogOut(Resource):
    def get(self):
        # clear the local storage from frontend
        session.clear()
        return jsonify({"message": "Logged out"}), 202


class Home(Resource):
    @login_required
    def get(self):
        encoded_jwt = request.headers.get("Authorization").split("Bearer ")[1]
        try:
            decoded_jwt = jwt.decode(
                encoded_jwt,
                app.secret_key,
                algorithms=[
                    algorithm,
                ],
            )
            # print(decoded_jwt)
        except Exception as e:
            return jsonify({"message": "Decoding JWT Failed", "exception": e.args}), 500
        return jsonify(decoded_jwt), 200


class BacktestSubjectCodesRoute(Resource):
    def get(self):
        backtest_subject_codes = BacktestSubjectCode.query.all()
        backtest_subject_codes = sorted(
            backtest_subject_codes, key=lambda x: x.subject_code
        )
        return (
            jsonify(
                {
                    "subject_codes": [
                        subject_code.subject_code
                        for subject_code in backtest_subject_codes
                    ]
                }
            ),
            200,
        )


parser_backtest_classes = reqparse.RequestParser()
parser_backtest_classes.add_argument("subject_code", type=str, required=True)


class BacktestClassesRoute(Resource):
    def get(self):
        args = parser_backtest_classes.parse_args()

        subject_code = args["subject_code"].upper().strip()
        if len(subject_code) != 4:
            return jsonify({"error": "Incorrect subject_code length passed in"}), 400

        backtest_classes = BacktestClasses.query.filter_by(
            subject_code=subject_code
        ).all()
        backtest_classes = sorted(backtest_classes, key=lambda x: x.course_number)
        return (
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
            return jsonify({"error": "Incorrect subject_code length passed in"}), 400

        course_number = args["course_number"]
        if len(str(course_number)) != 4:
            return jsonify({"error": "Incorrect course_number length passed in"}), 400

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
            return jsonify({"error": "No backwork found for this class"}), 404

        if backtests_exams is not None:
            backtests_exams = sorted(
                backtests_exams, key=lambda x: (x.backtest_number, x.year, x.semester)
            )
        if backtests_quizzes is not None:
            backtests_quizzes = sorted(
                backtests_quizzes, key=lambda x: (x.backtest_number, x.year, x.semester)
            )
        if backtests_midterms is not None:
            backtests_midterms = sorted(
                backtests_midterms,
                key=lambda x: (x.backtest_number, x.year, x.semester),
            )

        exams = dict()
        if backtests_exams is not None:
            for exam in backtests_exams:
                semester = ""
                if exam.semester == "A":
                    semester = "Spring"
                elif exam.semester == "U":
                    semester = "Summer"
                else:
                    semester = "Fall"

                if exam.backtest_number in exams.keys():
                    exams[exam.backtest_number].append(f"{semester} {exam.year}")
                else:
                    exams[exam.backtest_number] = [f"{semester} {exam.year}"]
        else:
            exams = None

        quizzes = dict()
        if backtests_quizzes is not None:
            for quiz in backtests_quizzes:
                semester = ""
                if quiz.semester == "A":
                    semester = "Spring"
                elif quiz.semester == "U":
                    semester = "Summer"
                else:
                    semester = "Fall"

                if quiz.backtest_number in quizzes.keys():
                    quizzes[quiz.backtest_number].append(f"{semester} {quiz.year}")
                else:
                    quizzes[quiz.backtest_number] = [f"{semester} {quiz.year}"]
        else:
            quizzes = None

        midterms = dict()
        if backtests_midterms is not None:
            for midterm in backtests_midterms:
                semester = ""
                if midterm.semester == "A":
                    semester = "Spring"
                elif midterm.semester == "U":
                    semester = "Summer"
                else:
                    semester = "Fall"

                if midterm.backtest_number in quizzes.keys():
                    midterms[midterm.backtest_number].append(
                        f"{semester} {midterm.year}"
                    )
                else:
                    midterms[midterm.backtest_number] = [f"{semester} {midterm.year}"]
        else:
            midterm = None

        return jsonify({"exams": exams, "quizzes": quizzes, "midterms": midterms}), 200

    @login_required
    def post(self):
        args = parser_backtest_post.parse_args()

        subject_code = args["subject_code"].upper().strip()
        if len(subject_code) != 4:
            return jsonify({"error": "Incorrect subject_code length passed in"}), 400

        course_number = args["course_number"]
        if len(str(course_number)) != 4:
            return jsonify({"error": "Incorrect course_number length passed in"}), 400

        year = args["year"]
        if len(str(year)) != 4:
            return jsonify({"error": "Incorrect year length passed in"}), 400

        semester = args["semester"].upper().strip()
        if len(semester) != 1:
            return jsonify({"error": "Incorrect semester length passed in"}), 400
        if semester != "A" or semester != "U" or semester != "Z":
            return (
                jsonify(
                    {
                        "error": "Incorrect semester type, A for Spring, U for Summer, and Z for Fall"
                    }
                ),
                400,
            )

        backwork_type = args["type"].upper().strip()
        if (
            backwork_type != "EXAM"
            or backwork_type != "QUIZ"
            or backwork_type != "MIDTERM"
        ):
            return (
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

        new_backtest = Backtest(
            subject_code=subject_code,
            added=now,
            course_number=course_number,
            exam=exam,
            quiz=quiz,
            midterm=midterm,
            year=year,
            semester=semester,
            backtest_number=backtest_number,
        )

        db.session.add(new_backtest)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": f"new backtest {subject_code} {course_number} {semester} {year} created"
                }
            ),
            201,
        )


api.add_resource(Home, "/home")
api.add_resource(LogOut, "/logout")
api.add_resource(GoogleAuth, "/auth/google")
api.add_resource(Callback, "/callback")
api.add_resource(BacktestSubjectCodesRoute, "/backtest/subjectcodes")
api.add_resource(BacktestClassesRoute, "/backtest/classes")
api.add_resource(BacktestsRoute, "/backtest/")
