from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models.user import User
from app.models.student import Student

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        # Check if user already exists
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "Username already exists"}), 400

        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 400

        # Create new user
        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=data.get("role", "student"),
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        # If user is a student, create student profile
        if user.role == "student":
            student = Student(
                user_id=user.id,
                student_id=f"STU{user.id:06d}",
                major=data.get("major", "Undeclared"),
                year_level=data.get("year_level", "freshman"),
            )
            db.session.add(student)
            db.session.commit()

        return (
            jsonify(
                {"message": "User registered successfully", "user": user.to_dict()}
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data["username"]).first()

        if user and user.check_password(data["password"]):
            login_user(user)
            return jsonify({"message": "Login successful", "user": user.to_dict()}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({"user": current_user.to_dict()}), 200
