import json

from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

from site import app, login_manager, google_client
from site.models import User

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def get_google_provider_cfg():
    return requests.get(app.config["GOOGLE_DISCOVERY_URL"]).json()


@app.route("/")
def index():
    if current_user.is_authenticated:
        return f"""
<p>Hello, {current_user.name}! You're logged in! Email: {current_user.email}</p>
<div><p>Google Profile Picture:</p>
<img src="{current_user.profile_pic}" alt="Google profile pic"></img></div>
<a class="button" href="{url_for("logout")}">Logout</a>"""
    else:
        return f'<a class="button" href="{url_for("login")}">Google Login</a>'


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config["GOOGLE_CLIENT_ID"], app.config["GOOGLE_CLIENT_SECRET"]),
    )

    # Parse the tokens!
    google_client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = google_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    user_json = userinfo_response.json()
    if user_json.get("email_verified"):
        unique_id = user_json["sub"]
        users_email = user_json["email"]
        picture = user_json["picture"]
        users_name = user_json["given_name"]

        # Create a user in your db with the information provided
        # by Google
        user = User(
            id_=unique_id, name=users_name, email=users_email, profile_pic=picture
        )

        # Doesn't exist? Add it to the database.
        if not User.get(unique_id):
            User.create(unique_id, users_name, users_email, picture)

        # Begin user session by logging the user in
        login_user(user)

        # Send user back to homepage
        return redirect(url_for("index"))
    else:
        return "User email not available or not verified by Google.", 400


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


'''
SEO
'''


@app.route('/robots.txt', methods=['GET'])
def robots():

    # Return static robots.txt file for any web crawlers that use it
    return send_file('templates/seo/robots.txt')


@app.route('/favicon.ico', methods=['GET'])
def favicon():

    # Return static favicon.ico
    return send_file('static/img/jyl.ico')


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():

    # Return static sitemap XML file for SEO
    sitemap_xml = render_template('seo/sitemap.xml')
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response



'''
Error Handlers
'''


@app.errorhandler(404)
def page_not_found(e):

    # 404 error page
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_for_server(e):

    # 500 error page
    return render_template('500.html'), 500