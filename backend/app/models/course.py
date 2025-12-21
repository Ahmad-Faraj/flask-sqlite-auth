from app import db


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False, default=3)
    professor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20), nullable=False)  # fall, spring, summer
    year = db.Column(db.Integer, nullable=False)
    max_enrollment = db.Column(db.Integer, default=30)

    # Relationships
    professor = db.relationship("User", backref="taught_courses")
    enrollments = db.relationship("Enrollment", backref="course", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "course_code": self.course_code,
            "title": self.title,
            "description": self.description,
            "credits": self.credits,
            "professor_id": self.professor_id,
            "department": self.department,
            "semester": self.semester,
            "year": self.year,
            "max_enrollment": self.max_enrollment,
            "professor": self.professor.to_dict() if self.professor else None,
            "enrolled_count": self.enrollments.count(),
        }

    def __repr__(self):
        return f"<Course {self.course_code}>"
