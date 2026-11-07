from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = 'super-secret-remote-dev-key'

init_db()

def log_action(conn, action, username):
    conn.execute('INSERT INTO audit_logs (action, performed_by) VALUES (?, ?)', (action, username))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action_type = request.form.get('action_type')
        username = request.form.get('username').strip()
        password = request.form.get('password')
        role = request.form.get('role', 'Member')

        conn = get_db()
        if action_type == 'register':
            try:
                hashed_pw = generate_password_hash(password)
                conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                             (username, hashed_pw, role))
                log_action(conn, f"Registered new {role} account", username)
                conn.commit()
                flash("Account created! Please log in.")
            except Exception:
                flash("Username already exists.")
        elif action_type == 'login':
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('dashboard'))
            flash("Invalid username or password.")
        conn.close()
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    status_filter = request.args.get('status', 'All')
    conn = get_db()

    if status_filter == 'All':
        tickets = conn.execute('''
            SELECT tickets.*, users.username AS creator 
            FROM tickets JOIN users ON tickets.created_by = users.id 
            ORDER BY tickets.id DESC
        ''').fetchall()
    else:
        tickets = conn.execute('''
            SELECT tickets.*, users.username AS creator 
            FROM tickets JOIN users ON tickets.created_by = users.id 
            WHERE tickets.status = ? ORDER BY tickets.id DESC
        ''', (status_filter,)).fetchall()

    logs = conn.execute('SELECT * FROM audit_logs ORDER BY id DESC LIMIT 8').fetchall()
    conn.close()
    return render_template('dashboard.html', tickets=tickets, logs=logs, current_filter=status_filter)

@app.route('/create_ticket', methods=['POST'])
def create_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority')

    conn = get_db()
    conn.execute('INSERT INTO tickets (title, description, priority, created_by) VALUES (?, ?, ?, ?)',
                 (title, description, priority, session['user_id']))
    log_action(conn, f"Created ticket: '{title}' [{priority}]", session['username'])
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/update_status/<int:ticket_id>', methods=['POST'])
def update_status(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    new_status = request.form.get('status')
    conn = get_db()
    conn.execute('UPDATE tickets SET status = ? WHERE id = ?', (new_status, ticket_id))
    log_action(conn, f"Updated Ticket #{ticket_id} to '{new_status}'", session['username'])
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    if session.get('role') != 'Admin':
        flash("Access Denied: Only Admins can delete tickets.")
        return redirect(url_for('dashboard'))

    conn = get_db()
    conn.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
    log_action(conn, f"Deleted Ticket #{ticket_id}", session['username'])
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

app.run(debug=True)