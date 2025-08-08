# College Grievance & Exam Request Portal

This project is a full-stack web application for a college grievance, appeals, and exam request portal. It provides a role-based system for students, faculty, and administrators to manage various academic and administrative requests.

## Tech Stack

- **Frontend:** HTML, CSS
- **Backend:** Python (Flask)
- **Database:** MySQL

## Features

- Role-Based Access Control (Student, Faculty, Admin, etc.)
- Grievance and Request Submission
- Status Tracking
- Automated Escalation Workflow
- Audit Trail for all actions

---

## How to Run

Follow these steps to set up and run the application on your local machine.

**1. Set Up a Virtual Environment & Install Dependencies**
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`

# Install the required packages
pip install -r requirements.txt
```

**2. Configure the Environment and Database**
The application uses SQLite for local development by default.

```bash
# Set the FLASK_APP environment variable
export FLASK_APP=run.py  # On Windows, use `set FLASK_APP=run.py`

# Apply the database migrations to create the database schema
flask db upgrade
```

**3. Create Your First User**
You can create a user with a specific role using the `create-user` command. Roles are case-sensitive (e.g., 'Admin', 'Student', 'Faculty').

To create an admin user:
```bash
flask create-user "Your Name" "admin@example.com" "your_password" "Admin"
```
To create a student user:
```bash
flask create-user "Student Name" "student@example.com" "your_password" "Student"
```
To create a faculty user (who can handle requests):
```bash
flask create-user "Faculty Name" "faculty@example.com" "your_password" "Faculty"
```

**4. Run the Application**
```bash
# Run the Flask development server
flask run
```
Once the server is running, you can access the application by opening your web browser and navigating to **http://127.0.0.1:5000**.

---
*This project is being built by an AI software engineer.*
