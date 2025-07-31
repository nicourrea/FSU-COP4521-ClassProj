Family Budgeting System:

A web-based family budgeting application built with Flask that helps parents and children manage household expenses,
set budgets, and track spending. The system supports user roles (parent and child), CSV expense uploads, dynamic expense
and budget management, and secure session-based authentication.


Features

User Roles: Parent and child accounts with different permissions.
Authentication: Secure session-based login/logout using Flask-Login.
Expense Tracking: Add, edit, and categorize expenses.
Budget Management: Parents can set budgets; children can view and log expenses.
CSV Import: Bulk import expenses via CSV uploads.
Hardcoded Admin Role: view all families/users and export all expense data to CSV.

Technology Stack

Backend Libraries: Python, Flask, psycopg2, werkzeug (security), functools, random, io, csv, os, dotenv, multiprocessing
Database: PostgreSQL
Frontend: HTML5, Jinja2 Templates
File Handling: Python’s csv module for imports

Non-Obvious Instructions:

Admin username: "admin"
Admin password: "admin123"

Workload Breakdown

Hubert - Did the initial skeleton work. Created schema.sql and db.py files and filled
with whatever functions thought were necessary to the project. Created intial login page
with app.py functions for register and login functions, with subsequent html files for
each.

Nico - Designed the overall user flow of the website. Created HTML templates for open_expenses,
add_expense, submit_expense, accounts, edit_accounts, and landing. Primarily responsible for
API route implementation and testing in app.py, ensuring full CRUD functionality and RBAC
enforcement across the application.

Maxwell - Implemented backend data access and editing logic in app.py, with complementary
JavaScript and HTML layers to provide a seamless, interactive user experience.

Isiaq - Implemented dynamic table template creation and deletion, complete with dedicated
Flask routes.

Joseph - Implemented the bulk import of expenses via CSV upload, and developed the admin role, 
including admin.py and all associated HTML templates.
