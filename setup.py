import psycopg2
from psycopg2 import sql
import sys

# Define credentials and target database
DB_NAME = "group_project_db"
DB_USER = "hubertpilichowski" # Replace with your actual username
DB_HOST = "localhost"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
    )
    return conn

def create_database_if_missing():
    """Checks if the target DB exists, creates it if not."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        print(f"🔧 Creating database '{DB_NAME}'...")
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
    else:
        print(f"✅ Database '{DB_NAME}' already exists.")

    cur.close()
    conn.close()

def create_tables():
    """Creates the tables in the target DB"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Create accounts table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) NOT NULL,
            department VARCHAR(50)
        );
    """)

    # Create app_settings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            setting VARCHAR(100) PRIMARY KEY,
            value VARCHAR(255)
        );
    """)

    # Create budgets table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id SERIAL PRIMARY KEY,
            year INT NOT NULL,
            department VARCHAR(100) NOT NULL,
            total DOUBLE PRECISION NOT NULL,
            UNIQUE (year, department)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables created successfully in database.")

if __name__ == '__main__':
    try:
        create_database_if_missing()
        create_tables()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
