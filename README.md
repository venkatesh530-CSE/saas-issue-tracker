 # IssueFlow SaaS — Multi-User Issue & Project Tracker

A full-stack collaborative issue-tracking web application built with **Python (Flask)**, **SQLite**, and **HTML/CSS**, designed for remote engineering teams.

## Key Features
- **Relational SQL Database:** Structured `users`, `tickets`, and `audit_logs` tables linked via `FOREIGN KEY` constraints and queried with SQL `JOIN` operations.
- **Role-Based Access Control (RBAC):** Separates `Admin` and `Member` permissions—restricting ticket deletion exclusively to Admins.
- **Authentication & Security:** Uses `Werkzeug` password hashing (`generate_password_hash`) and server-side session management.
- **Live Audit Trail:** Automatically logs every ticket creation, status transition, and deletion with timestamps for asynchronous team accountability.

## How to Run Locally
1. Clone the repository and navigate into the folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open `http://127.0.0.1:5000` in your browser.