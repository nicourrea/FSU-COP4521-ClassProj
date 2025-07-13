from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from functools import wraps
import random
import io
import csv
from db import get_db_connection, insert_user, get_user_by_username, get_budget_categories

app = Flask(__name__)
app.secret_key = 'COP4521'  # Change this in production

# ========== Login Required Decorator ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to view this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== Role Required Decorator ==========
def role_required(role):
    """Restrict route access based on user role (e.g., 'parent')"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') != role:
                return "Access denied", 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ========== Home ==========
@app.route('/')
@login_required
def home():
    return render_template('home.html')

# ========== Register ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # 'parent' or 'child'

        # Check if username already exists
        if get_user_by_username(username):
            flash("Username already exists.")
            return redirect('/register')

        # Hash password
        hashed_password = generate_password_hash(password)

        # Determine family_id
        if role == 'parent':
            parent_option = request.form.get('parent_option')
            if parent_option == 'join':
                try:
                    family_id = int(request.form['existing_family_id'])
                except (ValueError, KeyError):
                    flash("Invalid family ID for joining an existing family.")
                    return redirect('/register')
            else:
                # Default to creating a new family
                family_id = random.randint(1000, 9999)
        else:  # role == 'child'
            try:
                family_id = int(request.form['family_id'])
            except (ValueError, KeyError):
                flash("Missing or invalid family ID for child account.")
                return redirect('/register')

        # Insert into DB
        insert_user(username, hashed_password, role, family_id)

        flash("Registration successful! Please log in.")
        return redirect('/login')

    return render_template('register.html')

# ========== Login ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            session['family_id'] = user[4]
            flash("Logged in successfully.")
            return redirect('/')

        flash("Invalid username or password.")
    return render_template('login.html')

# ========== Logout ==========
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect('/')