import sqlite3  # Imports Python's built-in SQLite tool so we can write SQL

def get_db():
    # Opens (or creates) a database file named 'tracker.db' in your project folder
    conn = sqlite3.connect('tracker.db')
    # Allows us to read columns by name (e.g., user['username']) instead of numbers
    conn.row_factory = sqlite3.Row
    # Enforces SQL relationship rules so linked tables stay valid
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()  # A cursor is the tool that runs SQL commands

    # Table 1: Stores registered users, encrypted passwords, and roles (Admin/Member)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Member'
        )
    ''')

    # Table 2: Stores issues/tickets and links 'created_by' to a specific user's ID
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # Table 3: Stores a permanent history of who did what and when
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            performed_by TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()  # Saves the newly created tables permanently to tracker.db
    conn.close()   # Safely closes the database file

# Runs only when you execute 'python database.py' directly
if __name__ == '_main_':
    init_db()
    print("Success! tracker.db and all 3 SQL tables were created.")