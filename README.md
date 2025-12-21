# Student Management System

Flask backend with SQLite, multi-page HTML frontend.

## Docker

```bash
docker-compose up --build
```

Open http://localhost:3000

## Manual

```bash
pip install flask flask-cors
python app.py
```

Open `index.html` in browser or:

```bash
python -m http.server 3000
```

## Configuration

Edit `.env` file:

```
SECRET_KEY=your-secret-key
PORT=5000
DEBUG=True
DATA_DIR=.
```

## API Endpoints

- POST /api/register
- POST /api/login
- GET /api/courses
- POST /api/courses/{id}/enroll
- GET /api/my-courses/{user_id}
- GET /api/grades/{user_id}

## Pages

- `index.html` - Home
- `login.html` - Login
- `signup.html` - Registration
- `courses.html` - Course list
- `my-courses.html` - Enrolled courses
- `grades.html` - Grade view
