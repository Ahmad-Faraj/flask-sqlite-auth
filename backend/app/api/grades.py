from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.models.student import Student

grades_bp = Blueprint("grades", __name__)


@grades_bp.route("/", methods=["GET"])
@login_required
def get_grades():
    try:
        if current_user.role == "student":
            student = Student.query.filter_by(user_id=current_user.id).first_or_404()
            enrollments = Enrollment.query.filter_by(student_id=student.id).all()
            grades = []
            for enrollment in enrollments:
                grades.extend(enrollment.grades)
            return jsonify([grade.to_dict() for grade in grades]), 200
        else:
            grades = Grade.query.all()
            return jsonify([grade.to_dict() for grade in grades]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@grades_bp.route("/", methods=["POST"])
@login_required
def create_grade():
    try:
        if current_user.role not in ["professor", "admin"]:
            return jsonify({"error": "Access denied"}), 403

        data = request.get_json()

        grade = Grade(
            enrollment_id=data["enrollment_id"],
            assignment_name=data["assignment_name"],
            grade_value=data["grade_value"],
            max_points=data.get("max_points", 100.0),
            assignment_type=data["assignment_type"],
        )

        db.session.add(grade)
        db.session.commit()

        return (
            jsonify(
                {"message": "Grade recorded successfully", "grade": grade.to_dict()}
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@grades_bp.route("/course/<int:course_id>", methods=["GET"])
@login_required
def get_course_grades(course_id):
    try:
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        grades = []
        for enrollment in enrollments:
            grades.extend(enrollment.grades)
        return jsonify([grade.to_dict() for grade in grades]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@grades_bp.route("/my-grades", methods=["GET"])
@login_required
def get_my_grades():
    try:
        if current_user.role != "student":
            return jsonify({"error": "Access denied"}), 403

        student = Student.query.filter_by(user_id=current_user.id).first_or_404()
        enrollments = Enrollment.query.filter_by(student_id=student.id).all()

        grades_by_course = {}
        for enrollment in enrollments:
            course_code = enrollment.course.course_code
            course_title = enrollment.course.title
            grades_by_course[course_code] = {
                "course": {
                    "code": course_code,
                    "title": course_title,
                    "credits": enrollment.course.credits,
                },
                "grades": [grade.to_dict() for grade in enrollment.grades],
            }

        return jsonify(grades_by_course), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
