from site import app

if __name__ == "__main__":
    app.run(ssl_context="adhoc", debug=True, port=8000)