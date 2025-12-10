# Flask Login & Sign-up App

A minimal, modern Flask web application with user authentication using SQLite.

## Features

- User registration (Sign-up)
- User login with password hashing
- Protected dashboard
- Modern, sleek UI with animations
- Native SQLite3 database (no ORM)

## Project Structure

```
flask-app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── login.html     # Login form
│   ├── signup.html    # Sign-up form
│   └── dashboard.html # Dashboard (after login)
└── static/
    └── styles.css     # Modern CSS with animations
```

## Setup & Run

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Run the Application

```powershell
python app.py
```

The app will start on `http://127.0.0.1:5000/`

## Usage

1. **Sign Up**: Create a new account with username and password
2. **Login**: Use your credentials to log in
3. **Dashboard**: Access your dashboard after successful login
4. **Logout**: Click logout to exit

## Database

The SQLite database (`users.db`) is created automatically on first run with the following schema:

```
users (id, username, password)
```

- Username must be unique
- Password is hashed using SHA256

## Notes

- Change the `secret_key` in `app.py` for production use
- Minimum username length: 3 characters
- Minimum password length: 6 characters
- The database file is created in the project root directory
