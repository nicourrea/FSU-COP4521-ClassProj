from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import random
import io
import csv
from db import get_db_connection, insert_user, get_user_by_username, get_budget_categories

app = Flask(__name__)
app.secret_key = 'COP4521'

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

# ========== Route Landing/Home ==========

@app.route('/')
def index():
    if 'username' in session:
        return render_template('home.html')  # Authenticated dashboard
    else:
        return render_template('landing.html')  # Public-facing page

# ========== Home ==========
@app.route('/home')
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

# ========== View Accounts ==========
@app.route('/accounts')
@login_required
def accounts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT username, role
        FROM users
        WHERE family_id = %s
        ORDER BY username ASC
    """, (session['family_id'],))
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('accounts.html', users=users)

# ========== Edit Accounts (Parents Only) ==========
@app.route('/edit_accounts')
@role_required('parent')
def edit_accounts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT username, role
        FROM users
        WHERE family_id = %s
        ORDER BY username ASC
    """, (session['family_id'],))
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('edit_accounts.html', users=users)

# ========== Deleting Users(Parent Only) ==========

@app.route('/delete_user/<username>', methods=['POST'])
@role_required('parent')
def delete_user(username):
    conn = get_db_connection()
    cur = conn.cursor()

    # Make sure the user is a child in the same family
    cur.execute("""
        SELECT role FROM users
        WHERE username = %s AND family_id = %s
    """, (username, session['family_id']))
    user = cur.fetchone()

    if not user:
        flash("User not found or not in your family.")
    elif user[0] == 'parent':
        flash("You cannot delete parent accounts.")
    else:
        cur.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        flash(f"Deleted user: {username}")

    cur.close()
    conn.close()
    return redirect('/accounts')

# ========== Show Expenses ==========

@app.route('/open_expenses')
@login_required
def open_expenses():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT category FROM expenses WHERE family_id = %s ORDER BY category ASC",
        (session['family_id'],)
    )
    categories = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template('open_expenses.html', categories=categories)  

# ========== Editing/Deleting in Expenses ==========

@role_required('parent')
@app.route('/delete_expense', methods=['POST'])
@role_required('parent')
def delete_expense():
    data = request.get_json()
    expense_id = data.get('id')

    if not expense_id:
        return jsonify({'success': False, 'error': 'Missing expense ID'})

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id = %s AND family_id = %s", (expense_id, session['family_id']))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# ========== Adding Expense With Category (Parents Only) ==========

@app.route('/add_expense', methods=['GET', 'POST'])
@role_required('parent')
def add_expense():
    if session.get('role') != 'parent':
        flash("Access denied.")
        return redirect('/open_expenses')

    if request.method == 'POST':
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')
        expense_type = request.form.get('expense_type')
        user_id = session.get('user_id')
        family_id = session.get('family_id')

        if not (category and amount and date and expense_type):
            flash("All fields are required.")
            return redirect('/add_expense')

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO expenses (user_id, family_id, category, amount, date, expense_type, added_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, family_id, category, amount, date, expense_type, user_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Expense added under new category!")
            return redirect('/open_expenses')

        except Exception as e:
            flash(f"Error: {str(e)}")
            return redirect('/add_expense')

    return render_template('add_expense.html')

# ========== Adding Expense With Budget Lock(Children) ==========

@app.route('/submit_expense', methods=['GET', 'POST'])
@login_required
def submit_expense():
    if request.method == 'POST':
        data = request.form
        amount = data.get('amount')
        category = data.get('category')
        expense_type = data.get('expense_type')
        date = data.get('date')

        user_id = session.get('user_id')
        family_id = session.get('family_id')

        if not (amount and category and date):
            flash("Missing required fields.")
            return redirect('/submit_expense')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
           INSERT INTO expenses (user_id, family_id, category, expense_type, amount, date, added_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, family_id, category, expense_type, amount, date, user_id))  # added_by = user_id
        conn.commit()
        cur.close()
        conn.close()
        flash("Expense submitted!")
        return redirect('/open_expenses')

    categories = get_budget_categories(session['family_id'])
    return render_template('submit_expense.html', categories=categories)

 # ========== Tab For Child Only Expenses (Parents Only) ==========

@app.route('/view_child_expenses', methods=['POST'])
@login_required
def view_child_expenses():
    family_id = session.get('family_id')
    user_id = session.get('user_id')

    if not family_id or not user_id:
        return jsonify({'success': False, 'error': 'Missing session data'})

    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Join with users to get the username to show name instead of ID
        cur.execute("""
            SELECT e.id, e.category, e.amount, e.expense_type, e.date, u.username AS added_by
            FROM expenses e
            JOIN users u ON e.added_by = u.id
            WHERE e.family_id = %s AND e.added_by != %s
            ORDER BY e.date DESC
        """, (family_id, user_id))

        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description] if cur.description else []
        table_data = [dict(zip(column_names, row)) for row in rows]

        return jsonify(success=True, column_names=column_names, table_data=table_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
# ========== Main ==========

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)