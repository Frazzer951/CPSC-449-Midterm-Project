import re
from datetime import timedelta
from os import getenv

import pymysql
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.secret_key = "happykey"
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


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))
