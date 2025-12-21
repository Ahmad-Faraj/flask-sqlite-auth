from app import db


class Grade(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(
        db.Integer, db.ForeignKey("enrollments.id"), nullable=False
    )
    assignment_name = db.Column(db.String(200), nullable=False)
    grade_value = db.Column(db.Float, nullable=False)
    max_points = db.Column(db.Float, nullable=False, default=100.0)
    assignment_type = db.Column(
        db.String(50), nullable=False
    )  # exam, homework, project, quiz
    date_recorded = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    enrollment = db.relationship("Enrollment", backref="grades")

    @property
    def percentage(self):
        return (self.grade_value / self.max_points) * 100 if self.max_points > 0 else 0

    @property
    def letter_grade(self):
        percentage = self.percentage
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"

    def to_dict(self):
        return {
            "id": self.id,
            "enrollment_id": self.enrollment_id,
            "assignment_name": self.assignment_name,
            "grade_value": self.grade_value,
            "max_points": self.max_points,
            "assignment_type": self.assignment_type,
            "percentage": self.percentage,
            "letter_grade": self.letter_grade,
            "date_recorded": (
                self.date_recorded.isoformat() if self.date_recorded else None
            ),
        }

    def __repr__(self):
        return f"<Grade {self.assignment_name}: {self.grade_value}/{self.max_points}>"
