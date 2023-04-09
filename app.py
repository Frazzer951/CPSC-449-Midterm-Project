import hashlib
import os
import re
import uuid
from datetime import datetime, timedelta
from functools import wraps
from os import getenv

import jwt
import pymysql
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.secret_key = "very_secret_key"
app.config['UPLOAD_FOLDER'] = "Uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


load_dotenv()
SQL_CONFIG = {
    "host":getenv("DB_HOST"),
    "user":getenv("DB_USER"),
    "password":getenv("DB_PASS"),
    "db":getenv("DB_NAME"),
    "cursorclass":pymysql.cursors.DictCursor,
}
# To connect MySQL database
conn = pymysql.connect(
    **SQL_CONFIG
)
cur = conn.cursor()


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error=str(e)), 401


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


@app.route("/")
def root():
    return "Hello World"


### AUTH DECORATOR

def verify_token(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("token")
        if not token:
            return {"message":"Token is missing."}, 403
        try:
            kwargs["_jwt_data"] = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            return func(*args, **kwargs)
        except:
            return {"message": "Token is not valid."}, 403

    wrapper.__name__ = func.__name__
    return wrapper

### END AUTH DECORATOR

# Login to the application
@app.route("/login", methods=["POST"])
def login():
    data = request.form

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        # returns 401 if any username or / and password is missing
        return make_response(
            "Missing username or password",
            401,
        )

    cur.execute("SELECT * FROM users WHERE username = % s", (username,))
    user = cur.fetchone()

    if not user:
        return make_response(
            "User does not exist. Please register.",
            401,
        )

    if check_password_hash(user["password"], password):
        token = jwt.encode({"public_id": user["public_id"], "exp": datetime.utcnow() + timedelta(minutes=30)}, app.secret_key)
        return make_response(jsonify({"token": token}), 200)

    return make_response(
        "Could not verify",
        401,
    )


# Register a new user
@app.route("/register", methods=["POST"])
def register():
    data = request.form

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        # returns 400 if any username or / and password is missing
        return make_response(
            "Missing username or password",
            400,
        )

    cur.execute("SELECT * FROM users WHERE username = % s", (username,))
    user = cur.fetchone()

    if user:
        return make_response(
            "User already exists. Please Log in.",
            401,
        )

    cur.execute(
        "INSERT INTO users (username, password) VALUES (% s, % s)",
        (
            username,
            generate_password_hash(password),
        ),
    )
    conn.commit()

    return make_response(
        "User created successfully!",
        201,
    )


# Get user public data
@app.route("/users", methods=["GET"])
def get_users():
    limit = request.args.get("limit")

    if limit:
        cur.execute("SELECT public_id, username FROM users LIMIT %s", (int(limit),))
    else:
        cur.execute("SELECT public_id, username FROM users")

    users = cur.fetchall()

    return make_response(jsonify(users), 200)


@app.route("/upload", methods=["GET", "POST"])
@verify_token
def upload_file(_jwt_data):
    cur.execute("SELECT `username` FROM users WHERE `public_id` = %s", (_jwt_data["public_id"],))
    acct = cur.fetchone()
    if "file" not in request.files:
        return {"message":"No file uploaded."}
    file = request.files["file"]
    if file.filename == "":
        return {"message":"No file selected."}
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return {
        "user": acct["username"],
        "message":"Success."
    }

@app.route("/profile", methods=["GET", "POST"])
@verify_token
def get_profile(_jwt_data):
    cur.execute("SELECT `username` FROM users WHERE `public_id` = %s", (_jwt_data["public_id"],))
    acct = cur.fetchone()
    return {
        "user": acct["username"],
        "message":"Success."
    }


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))
