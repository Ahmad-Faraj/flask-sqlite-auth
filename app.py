from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this"

DATABASE = "users.db"


def init_db():
    """Initialize a minimal users table if it does not exist."""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE users
                     (id INTEGER PRIMARY KEY,
                      username TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
        )
        conn.commit()
        conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_user(username: str):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user


def create_user(username: str, password: str) -> bool:
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def update_password(username: str, new_password: str) -> bool:
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hash_password(new_password), username),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user(username)

        if user and user[2] == hash_password(password):
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if len(username) < 3:
            return render_template(
                "signup.html", error="Username must be at least 3 characters"
            )
        if len(password) < 6:
            return render_template(
                "signup.html", error="Password must be at least 6 characters"
            )
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")

        if create_user(username, password):
            return redirect(url_for("login"))
        else:
            return render_template("signup.html", error="Username already exists")

    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        user = get_user(session["username"])

        if not user or user[2] != hash_password(old_password):
            return render_template(
                "settings.html",
                username=session["username"],
                error="Old password is incorrect",
            )

        if len(new_password) < 6:
            return render_template(
                "settings.html",
                username=session["username"],
                error="New password must be at least 6 characters",
            )

        if new_password != confirm_password:
            return render_template(
                "settings.html",
                username=session["username"],
                error="Passwords do not match",
            )

        if update_password(session["username"], new_password):
            return render_template(
                "settings.html",
                username=session["username"],
                success="Password changed successfully",
            )
        else:
            return render_template(
                "settings.html",
                username=session["username"],
                error="Error changing password",
            )

    return render_template("settings.html", username=session["username"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
