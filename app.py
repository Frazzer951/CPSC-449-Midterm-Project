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

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.secret_key = "very_secret_key"
app.permanent_session_lifetime = timedelta(minutes=10)


load_dotenv()

# To connect MySQL database
conn = pymysql.connect(
    host=getenv("DB_HOST"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASS"),
    db=getenv("DB_NAME"),
    cursorclass=pymysql.cursors.DictCursor,
)
cur = conn.cursor()


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404


@app.route("/")
def root():
    return "Hello World"


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


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))
