# Project

Project Description

#### Requirements

[Use a virtualenv to create an isolated enviorment](https://virtualenv.pypa.io/en/latest/)

Run the make command to install requirements

```
make
```

or with pip manually

```
pip3 install -r requirements.txt
```

## Running the program

Run description

```
make run
```

or with python manually

```
python3 run.py
```

## Running the tests

```
make test
```

or with ... manually

```
run test command
```

#### What are the tests checking

test check for ...

#### What happens when a test fails

Report the failed test [here](issue link)!

## Authors

* [**Author Name**](author link)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details


This Readme was created with [pystarter](https://github.com/RafaelCenzano/PyStarter)

```
pip3 install pystarter
```

Code and documentation below and in GoogleLogin.md and References.md are done modified from this repo: https://github.com/Abhiramborige/Flask-React-Google-Login

## Client side: React:
### Steps:
1. create .env file 
  ```
    REACT_APP_BACKEND_URL= http://localhost:8000
  ```
2. Use the commands to start the app locally.
  ```
    cd google-login-react
    npm install
    npm start
  ```

## Server side: Flask:
### Steps:
1. create .env file 
  ```
    DB_NAME=
    CLUSTER_URL=
    GOOGLE_CLIENT_ID=
    SECRET_KEY=
    ALGORITHM=
    PROJECT_ID=
    BACKEND_URL=http://127.0.0.1:8000
    FRONTEND_URL=http://localhost:3000
  ```
2. Go to https://console.cloud.google.com/ and create client secrets and configuration file
3. Save as client-secret.json
4. Use the commands to start the server locally.
  ```
    cd flask-server-google
    pip install virtualenv
    virtualenv google_env
    cd google_env/Scripts
    activate
    cd ..
    cd ..
    pip install -r requirements.txt
    python app.py
  ```
