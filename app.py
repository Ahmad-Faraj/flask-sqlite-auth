from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this"

DATABASE = "users.db"


def init_db():
    """Initialize the database with users and items tables"""
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
        c.execute(
            """CREATE TABLE items
                     (id INTEGER PRIMARY KEY,
                      user_id INTEGER NOT NULL,
                      title TEXT NOT NULL,
                      description TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))"""
        )
        conn.commit()
        conn.close()


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_user(username):
    """Get user from database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Get user by ID"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user


def get_all_users():
    """Get all users from database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, username, created_at FROM users ORDER BY id")
    users = c.fetchall()
    conn.close()
    return users


def create_user(username, password):
    """Create new user in database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        hashed_pw = hash_password(password)
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pw),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_user(user_id):
    """Delete user from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("DELETE FROM items WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_password(username, new_password):
    """Update user password"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        hashed_pw = hash_password(new_password)
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_pw, username))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def add_item(user_id, title, description=""):
    """Add new item for user"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO items (user_id, title, description) VALUES (?, ?, ?)",
            (user_id, title, description),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_user_items(user_id):
    """Get all items for a user"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        "SELECT id, title, description, created_at FROM items WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    items = c.fetchall()
    conn.close()
    return items


def delete_item(item_id, user_id):
    """Delete item belonging to user"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("DELETE FROM items WHERE id = ? AND user_id = ?", (item_id, user_id))
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
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (session["username"],))
    user = c.fetchone()
    conn.close()
    
    if user:
        user_id = user[0]
        items = get_user_items(user_id)
        return render_template("dashboard.html", username=session["username"], items=items, user_id=user_id)
    
    return redirect(url_for("login"))


@app.route("/items", methods=["GET", "POST"])
def items():
    if "username" not in session:
        return redirect(url_for("login"))
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (session["username"],))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return redirect(url_for("login"))
    
    user_id = user[0]
    
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        
        if not title:
            return render_template("items.html", username=session["username"], error="Title is required", user_items=get_user_items(user_id))
        
        if add_item(user_id, title, description):
            return redirect(url_for("items"))
        else:
            return render_template("items.html", username=session["username"], error="Error adding item", user_items=get_user_items(user_id))
    
    user_items = get_user_items(user_id)
    return render_template("items.html", username=session["username"], user_items=user_items, user_id=user_id)


@app.route("/delete-item/<int:item_id>", methods=["POST"])
def delete_item_route(item_id):
    if "username" not in session:
        return redirect(url_for("login"))
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (session["username"],))
    user = c.fetchone()
    conn.close()
    
    if user and delete_item(item_id, user[0]):
        return redirect(url_for("items"))
    
    return redirect(url_for("items"))


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
            return render_template("settings.html", username=session["username"], error="Old password is incorrect")
        
        if len(new_password) < 6:
            return render_template("settings.html", username=session["username"], error="New password must be at least 6 characters")
        
        if new_password != confirm_password:
            return render_template("settings.html", username=session["username"], error="Passwords do not match")
        
        if update_password(session["username"], new_password):
            return render_template("settings.html", username=session["username"], success="Password changed successfully")
        else:
            return render_template("settings.html", username=session["username"], error="Error changing password")
    
    return render_template("settings.html", username=session["username"])


@app.route("/admin")
def admin():
    if "username" not in session:
        return redirect(url_for("login"))
    
    users = get_all_users()
    return render_template("admin.html", username=session["username"], users=users)


@app.route("/admin/add-user", methods=["POST"])
def admin_add_user():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    
    if len(username) < 3:
        return redirect(url_for("admin"))
    
    if len(password) < 6:
        return redirect(url_for("admin"))
    
    create_user(username, password)
    return redirect(url_for("admin"))


@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):
    if "username" not in session:
        return redirect(url_for("login"))
    
    if user_id != get_user(session["username"])[0]:
        delete_user(user_id)
    
    return redirect(url_for("admin"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

