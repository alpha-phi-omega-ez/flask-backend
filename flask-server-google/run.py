from . import app

if __name__ == "__main__":
    app.run(ssl_context="adhoc", port=8000, host="0.0.0.0")
