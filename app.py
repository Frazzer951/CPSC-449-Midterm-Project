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
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        cur.execute(
            "SELECT * FROM accounts WHERE username = % s AND password = % s",
            (
                username,
                password,
            ),
        )
        conn.commit()
        account = cur.fetchone()
        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            msg = "Logged in successfully !"
            if account["username"] == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("index"))
        else:
            msg = "Incorrect username / password !"

    if "loggedin" in session:
        return redirect(url_for("index"))
    return render_template("login.html", msg=msg)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
        and "address" in request.form
        and "city" in request.form
        and "country" in request.form
        and "postalcode" in request.form
        and "organisation" in request.form
    ):
        print("reached")
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        organisation = request.form["organisation"]
        address = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        country = request.form["country"]
        postalcode = request.form["postalcode"]
        cur.execute("SELECT * FROM accounts WHERE username = % s", (username,))
        account = cur.fetchone()
        print(account)
        conn.commit()
        if account:
            msg = "Account already exists !"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address !"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "name must contain only characters and numbers !"
        else:
            cur.execute(
                "INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s)",
                (
                    username,
                    password,
                    email,
                    organisation,
                    address,
                    city,
                    state,
                    country,
                    postalcode,
                ),
            )
            conn.commit()

            msg = "You have successfully registered !"
    elif request.method == "POST":
        msg = "Please fill out the form !"
    return render_template("register.html", msg=msg)


@app.route("/index")
def index():
    if "loggedin" in session:
        return render_template("index.html")
    return redirect(url_for("login"))


@app.route("/admin")
def admin():
    if "loggedin" in session and session["username"] == "admin":
        return render_template("admin.html")
    return abort(401)


@app.route("/display")
def display():
    if "loggedin" in session:
        cur.execute("SELECT * FROM accounts WHERE id = % s", (session["id"],))
        account = cur.fetchone()
        return render_template("display.html", account=account)
    return redirect(url_for("login"))


@app.route("/update", methods=["GET", "POST"])
def update():
    msg = ""
    if "loggedin" in session:
        if (
            request.method == "POST"
            and "username" in request.form
            and "password" in request.form
            and "email" in request.form
            and "address" in request.form
            and "city" in request.form
            and "country" in request.form
            and "postalcode" in request.form
            and "organisation" in request.form
        ):
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]
            organisation = request.form["organisation"]
            address = request.form["address"]
            city = request.form["city"]
            state = request.form["state"]
            country = request.form["country"]
            postalcode = request.form["postalcode"]
            cur.execute("SELECT * FROM accounts WHERE username = % s", (username,))
            account = cur.fetchone()
            if account:
                msg = "Account already exists !"
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                msg = "Invalid email address !"
            elif not re.match(r"[A-Za-z0-9]+", username):
                msg = "name must contain only characters and numbers !"
            else:
                cur.execute(
                    """
                    UPDATE accounts
                    SET
                        username = %s,
                        password = %s,
                        email = %s,
                        organisation = %s,
                        address = %s,
                        city = %s,
                        state = %s,
                        country = %s,
                        postalcode = %s
                    WHERE
                        id = %s
                    """,
                    (
                        username,
                        password,
                        email,
                        organisation,
                        address,
                        city,
                        state,
                        country,
                        postalcode,
                        (session["id"],),
                    ),
                )
                conn.commit()
                msg = "You have successfully updated !"
        elif request.method == "POST":
            msg = "Please fill out the form !"
        return render_template("update.html", msg=msg)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))
