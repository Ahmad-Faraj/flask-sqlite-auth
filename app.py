from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re

app = Flask(__name__)
CORS(app)
DB_PATH = os.path.join(os.getenv("DATA_DIR", "."), "university.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def validate_password(password):
    if len(password) < 8 or len(password) > 128:
        return False, "Password must be 8-128 characters"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, ""


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT, name TEXT, role TEXT DEFAULT 'student')"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, name TEXT, code TEXT UNIQUE)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER, grade TEXT)"
    )
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        courses = [
            ("Introduction to Programming", "CS101"),
            ("Database Systems", "CS201"),
            ("Web Development", "CS301"),
            ("Data Structures", "CS102"),
            ("Software Engineering", "CS401"),
        ]
        cursor.executemany("INSERT INTO courses (name, code) VALUES (?, ?)", courses)
    conn.commit()
    conn.close()


@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    if not all(
        [
            data.get("username"),
            data.get("email"),
            data.get("name"),
            data.get("password"),
        ]
    ):
        return jsonify({"error": "Missing required fields"}), 400
    is_valid, error_msg = validate_password(data["password"])
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password, name, role) VALUES (?, ?, ?, ?, ?)",
            (
                data["username"],
                data["email"],
                generate_password_hash(data["password"]),
                data["name"],
                data.get("role", "student"),
            ),
        )
        conn.commit()
        user = conn.execute(
            "SELECT id, username, email, name, role FROM users WHERE username = ?",
            (data["username"],),
        ).fetchone()
        return jsonify({"user": dict(user)}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 400
    finally:
        conn.close()


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (data["username"],)
    ).fetchone()
    conn.close()
    if user and check_password_hash(user["password"], data["password"]):
        user_dict = dict(user)
        del user_dict["password"]
        return jsonify({"user": user_dict}), 200
    return jsonify({"error": "Invalid username or password"}), 401


@app.route("/api/courses")
def get_courses():
    conn = get_db()
    courses = [dict(row) for row in conn.execute("SELECT * FROM courses").fetchall()]
    conn.close()
    return jsonify(courses)


@app.route("/api/courses/<int:course_id>/enroll", methods=["POST"])
def enroll_course(course_id):
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    conn = get_db()
    if not conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone():
        conn.close()
        return jsonify({"error": "Course not found"}), 404
    if conn.execute(
        "SELECT * FROM enrollments WHERE user_id = ? AND course_id = ?",
        (user_id, course_id),
    ).fetchone():
        conn.close()
        return jsonify({"error": "Already enrolled"}), 400
    conn.execute(
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        (user_id, course_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Enrolled"}), 201


@app.route("/api/my-courses/<int:user_id>")
def get_my_courses(user_id):
    conn = get_db()
    courses = [
        dict(row)
        for row in conn.execute(
            "SELECT c.*, e.grade, e.id as enrollment_id FROM courses c JOIN enrollments e ON c.id = e.course_id WHERE e.user_id = ?",
            (user_id,),
        ).fetchall()
    ]
    conn.close()
    return jsonify(courses)


@app.route("/api/students")
def get_students():
    conn = get_db()
    students = conn.execute("SELECT id, username, name, email FROM users").fetchall()
    result = []
    for student in students:
        courses = conn.execute(
            "SELECT c.name, c.code FROM courses c JOIN enrollments e ON c.id = e.course_id WHERE e.user_id = ?",
            (student["id"],),
        ).fetchall()
        result.append(
            {
                "id": student["id"],
                "username": student["username"],
                "name": student["name"],
                "email": student["email"],
                "courses": [dict(c) for c in courses],
            }
        )
    conn.close()
    return jsonify(result)


@app.route("/api/enrollments/<int:enrollment_id>", methods=["DELETE"])
def unenroll(enrollment_id):
    conn = get_db()
    conn.execute("DELETE FROM enrollments WHERE id = ?", (enrollment_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Unenrolled"}), 200


@app.route("/api/students/<int:user_id>", methods=["DELETE"])
def delete_student(user_id):
    conn = get_db()
    conn.execute("DELETE FROM enrollments WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted"}), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
