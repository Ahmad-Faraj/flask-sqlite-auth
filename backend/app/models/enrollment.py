from app import db


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(
        db.String(20), default="enrolled"
    )  # enrolled, dropped, completed

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", name="student_course_unique"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrollment_date": (
                self.enrollment_date.isoformat() if self.enrollment_date else None
            ),
            "status": self.status,
            "student": self.student.to_dict() if self.student else None,
            "course": self.course.to_dict() if self.course else None,
        }

    def __repr__(self):
        return f"<Enrollment {self.student_id}-{self.course_id}>"
