from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    # Import models
    from app.models import user, student, course, enrollment, grade

    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.students import students_bp
    from app.api.courses import courses_bp
    from app.api.grades import grades_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(grades_bp, url_prefix="/api/grades")

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User

        return User.query.get(int(user_id))

    # Create tables
    with app.app_context():
        db.create_all()

    return app
