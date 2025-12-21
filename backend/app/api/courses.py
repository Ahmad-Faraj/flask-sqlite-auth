from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/", methods=["GET"])
@login_required
def get_courses():
    try:
        courses = Course.query.all()
        return jsonify([course.to_dict() for course in courses]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_bp.route("/<int:course_id>", methods=["GET"])
@login_required
def get_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        return jsonify(course.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_bp.route("/", methods=["POST"])
@login_required
def create_course():
    try:
        if current_user.role not in ["professor", "admin"]:
            return jsonify({"error": "Access denied"}), 403

        data = request.get_json()

        course = Course(
            course_code=data["course_code"],
            title=data["title"],
            description=data.get("description", ""),
            credits=data.get("credits", 3),
            professor_id=data.get("professor_id", current_user.id),
            department=data["department"],
            semester=data["semester"],
            year=data["year"],
            max_enrollment=data.get("max_enrollment", 30),
        )

        db.session.add(course)
        db.session.commit()

        return (
            jsonify(
                {"message": "Course created successfully", "course": course.to_dict()}
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_bp.route("/<int:course_id>/enroll", methods=["POST"])
@login_required
def enroll_in_course(course_id):
    try:
        if current_user.role != "student":
            return jsonify({"error": "Only students can enroll"}), 403

        student = Student.query.filter_by(user_id=current_user.id).first_or_404()
        course = Course.query.get_or_404(course_id)

        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=student.id, course_id=course_id
        ).first()

        if existing_enrollment:
            return jsonify({"error": "Already enrolled in this course"}), 400

        # Check enrollment capacity
        if course.enrollments.count() >= course.max_enrollment:
            return jsonify({"error": "Course is full"}), 400

        enrollment = Enrollment(student_id=student.id, course_id=course_id)

        db.session.add(enrollment)
        db.session.commit()

        return (
            jsonify(
                {"message": "Enrolled successfully", "enrollment": enrollment.to_dict()}
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_bp.route("/my-courses", methods=["GET"])
@login_required
def get_my_courses():
    try:
        if current_user.role == "student":
            student = Student.query.filter_by(user_id=current_user.id).first_or_404()
            enrollments = Enrollment.query.filter_by(student_id=student.id).all()
            return jsonify([enrollment.to_dict() for enrollment in enrollments]), 200
        elif current_user.role == "professor":
            courses = Course.query.filter_by(professor_id=current_user.id).all()
            return jsonify([course.to_dict() for course in courses]), 200
        else:
            return jsonify({"error": "Access denied"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500
