# db.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# ========== USERS ==========

def insert_user(username, password, role, family_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (username, password, role, family_id)
        VALUES (%s, %s, %s, %s)
        """,
        (username, password, role, family_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

# ========== EXPENSES ==========

def insert_expense(user_id, family_id, category, expense_type, amount, date, added_by):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO expenses (user_id, family_id, category, expense_type, amount, date, added_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, family_id, category, expense_type, amount, date, added_by)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_expenses_by_family(family_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses WHERE family_id = %s", (family_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ========== BUDGET ==========

def insert_budget(family_id, category, amount):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO budget (family_id, category, amount)
        VALUES (%s, %s, %s)
        """,
        (family_id, category, amount)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_budgets_by_family(family_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM budget WHERE family_id = %s", (family_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_budget_categories(family_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT category FROM budget WHERE family_id = %s", (family_id,))
        categories = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return categories
    except Exception as e:
        print("Error fetching budget categories:", e)
        return []