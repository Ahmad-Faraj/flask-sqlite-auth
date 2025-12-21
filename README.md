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

<img width="1599" height="899" alt="image" src="https://github.com/user-attachments/assets/57c422cf-424c-4ccd-bff0-020b039eccdb" />
<img width="1599" height="766" alt="image" src="https://github.com/user-attachments/assets/dce14c03-1eee-4053-8dd3-33c795096522" />
<img width="1582" height="899" alt="image" src="https://github.com/user-attachments/assets/67f0a1d1-f3a3-47e3-9eee-69ce1922993f" />
<img width="1593" height="899" alt="image" src="https://github.com/user-attachments/assets/b2fd3818-b1a6-47ac-a8fe-1c12e84f95d6" />

