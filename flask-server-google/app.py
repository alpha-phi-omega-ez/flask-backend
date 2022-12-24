from flask import jsonify, redirect, abort, request, session
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os, pathlib
import google
import jwt
from flask_cors import CORS
from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy
from . import app, db, api
from models import Backtest, BacktestClasses, BacktestSubjectCode

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
    def post():
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        request_session = requests.session()
        token_request = google.auth.transport.requests.Request(session=request_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
        )
        session["google_id"] = id_info.get("sub")

        # removing the specific audience, as it is throwing error
        del id_info["aud"]
        jwt_token = Generate_JWT(id_info)
        #insert_into_db(id_info.get("name"), id_info.get("email"), id_info.get("picture"))
        #add sql alchemy things
        return redirect(f"{FRONTEND_URL}?jwt={jwt_token}")
        """ return Response(
            response=json.dumps({'JWT':jwt_token}),
            status=200,
            mimetype='application/json'
        ) """

class GoogleAuth(Resource):
    def get():
        authorization_url, state = flow.authorization_url()
        # Store the state so the callback can verify the auth server response.
        session["state"] = state
        return jsonify({"auth_url": authorization_url}), 200


class LogOut(Resource):
    def get():
        # clear the local storage from frontend
        session.clear()
        return jsonify({"message": "Logged out"}), 202


class Home(Resource):
    @login_required
    def get():
        encoded_jwt = request.headers.get("Authorization").split("Bearer ")[1]
        try:
            decoded_jwt = jwt.decode(
                encoded_jwt,
                app.secret_key,
                algorithms=[
                    algorithm,
                ],
            )
            #print(decoded_jwt)
        except Exception as e:
            return jsonify({"message": "Decoding JWT Failed", "exception": e.args}), 500
        return jsonify(decoded_jwt), 200

api.add_resource(Home, "/home")
api.add_resource(LogOut, "/logout")
api.add_resource(GoogleAuth, "/auth/google")
api.add_resource(Callback, "/callback")
#api.add_resource(Square, '/square/<int:num>')