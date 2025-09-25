# Apointments


## Overview

- Appointments is a web application for scheduling, viewing, editing, and deleting appointments. Users can create accounts, log in, and manage their appointments through a simple and intuitive interface. The app is built with Flask, SQLite, and Bulma CSS.

## Features

- User registration and authentication
- Secure password hashing
- Schedule new appointments with date and time
- View all appointments in a table
- Edit or cancel existing appointments
- Flash messages for user feedback
- Admin account support
- Responsive UI with Bulma CSS

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Jakekougan/Appointments.git
    cd Appointments
    ```

2. **Set up a virtual environment (optional but recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies:**
    ```sh
    pip install flask python-dotenv werkzeug
    ```

4. **Set up environment variables:**
    - Create a `.env` file with:
      ```
      ADMIN_EMAIL=your_email
      ADMIN_PWD=your_admin_password
      ```

5. **Initialize the database:**
    ```sh
    flask initdb
    flask add_admins
    ```

6. **Run the application:**
    ```sh
    python -m flask run
    ```

## Usage

- Visit `http://localhost:5000` in your browser.
- Register a new account or log in with the admin credentials.
- Schedule, view, edit, or delete appointments as needed.

## Project Structure

- `app.py` — Main Flask application and routes
- `schema.sql` — Database schema
- `tests.py` — Unit tests
- `templates/` — HTML templates (Jinja2)
- `static/` — Static files (CSS)
- `notifications.py` — Email notification logic
- `.env` — Environment variables
- `.yagmail` — Email credentials for notifications

## Running Tests

To run the test suite:
```sh
python tests.py
```

---

*Built with Flask, SQLite, and Bulma CSS.*
