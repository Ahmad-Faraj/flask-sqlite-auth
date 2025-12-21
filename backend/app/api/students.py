from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.student import Student
from app.models.user import User

students_bp = Blueprint("students", __name__)


@students_bp.route("/", methods=["GET"])
@login_required
def get_students():
    try:
        students = Student.query.all()
        return jsonify([student.to_dict() for student in students]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@students_bp.route("/<int:student_id>", methods=["GET"])
@login_required
def get_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        return jsonify(student.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@students_bp.route("/profile", methods=["GET"])
@login_required
def get_my_profile():
    try:
        if current_user.role != "student":
            return jsonify({"error": "Access denied"}), 403

        student = Student.query.filter_by(user_id=current_user.id).first_or_404()
        return jsonify(student.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@students_bp.route("/profile", methods=["PUT"])
@login_required
def update_my_profile():
    try:
        if current_user.role != "student":
            return jsonify({"error": "Access denied"}), 403

        data = request.get_json()
        student = Student.query.filter_by(user_id=current_user.id).first_or_404()

        # Update student fields
        if "major" in data:
            student.major = data["major"]
        if "year_level" in data:
            student.year_level = data["year_level"]

        # Update user fields
        user = current_user
        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]
        if "email" in data:
            user.email = data["email"]

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Profile updated successfully",
                    "student": student.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
