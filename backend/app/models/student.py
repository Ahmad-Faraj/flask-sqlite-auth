from app import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    major = db.Column(db.String(100), nullable=False)
    year_level = db.Column(
        db.String(20), nullable=False
    )  # freshman, sophomore, junior, senior
    gpa = db.Column(db.Float, default=0.0)
    total_credits = db.Column(db.Integer, default=0)

    # Relationships
    user = db.relationship("User", backref="student_profile")
    enrollments = db.relationship("Enrollment", backref="student", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "student_id": self.student_id,
            "major": self.major,
            "year_level": self.year_level,
            "gpa": self.gpa,
            "total_credits": self.total_credits,
            "user": self.user.to_dict() if self.user else None,
        }

    def __repr__(self):
        return f"<Student {self.student_id}>"
