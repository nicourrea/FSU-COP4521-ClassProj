from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, Response
from functools import wraps
from multiprocessing import Pool, cpu_count
import csv
import io

from db import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

HARDCODED_ADMIN = {
    "username": "admin",
    "password": "admin123"
}

#----------Hardcoded admin credentials---------- 
def is_hardcoded_admin(username, password):
    return username == HARDCODED_ADMIN["username"] and password == HARDCODED_ADMIN["password"]

#----------Require admin login for route---------- 
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.")
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash("Admin access only.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

#----------Display admin dashboard with user and family data----------
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT family_id FROM users ORDER BY family_id ASC")
    families = cur.fetchall()
    cur.execute("SELECT id, username, role, family_id FROM users ORDER BY username ASC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_dashboard.html', families=families, users=users)

#----------Return list of users in a specific family----------
@admin_bp.route('/family_members/<int:family_id>')
@admin_required
def family_members(family_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, role
        FROM users
        WHERE family_id = %s
        ORDER BY username ASC
    """, (family_id,))
    members = cur.fetchall()
    cur.close()
    conn.close()
    members_list = [{'id': m[0], 'username': m[1], 'role': m[2]} for m in members]
    return jsonify(members=members_list)

#----------Display expenses for a given family----------
@admin_bp.route('/family_expenses/<int:family_id>')
@admin_required
def family_expenses(family_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, u.username, e.category, e.amount, e.date, e.expense_type
        FROM expenses e
        JOIN users u ON e.user_id = u.id
        WHERE e.family_id = %s
        ORDER BY e.date DESC
    """, (family_id,))
    expenses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_expenses.html', expenses=expenses, family_id=family_id)

#----------Export all family expenses as a CSV file----------
@admin_bp.route('/export_all_csv')
@admin_required
def export_all_csv():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT family_id FROM users WHERE family_id IS NOT NULL ORDER BY family_id")
    family_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    with Pool(processes=min(cpu_count(), len(family_ids))) as pool:
        results = pool.map(fetch_family_expenses_csv_rows, family_ids)

    all_rows = [row for sublist in results for row in sublist]

    def sort_key(row):
        family_id = int(row[0])
        date = row[4]
        return (family_id, date if date != "NULL" else "")
    all_rows.sort(key=sort_key)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Family ID', 'Username', 'Category', 'Amount', 'Date', 'Expense Type'])
    writer.writerows(all_rows)

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=all_expenses.csv"}
    )

#----------Fetch expense rows for one family----------
def fetch_family_expenses_csv_rows(family_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.family_id, u.username, 
               COALESCE(NULLIF(e.category, ''), 'NULL'),
               COALESCE(CAST(e.amount AS TEXT), 'NULL'),
               COALESCE(TO_CHAR(e.date, 'YYYY-MM-DD'), 'NULL'),
               COALESCE(e.expense_type, 'NULL')
        FROM expenses e
        JOIN users u ON e.user_id = u.id
        WHERE u.family_id = %s
    """, (family_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [list(row) for row in rows]
