-- Drop enum and tables if they already exist
DROP TYPE IF EXISTS family_role CASCADE;
DROP TABLE IF EXISTS background_tasks, expenses, budget, users CASCADE;

-- Create enum for user roles
CREATE TYPE family_role AS ENUM ('parent', 'child');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role family_role NOT NULL,
    family_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Budget table
CREATE TABLE budget (
    id SERIAL PRIMARY KEY,
    family_id INT NOT NULL,
    category VARCHAR(50),
    amount NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Expenses table (supports both manual and CSV submission)
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,     -- optional, for filtering by account
    family_id INT NOT NULL,
    category VARCHAR(100),                                 -- from CSV or manual input
    amount NUMERIC(10, 2),                                 -- from CSV or manual input
    date DATE,                                             -- from CSV or manual input
    expense_type VARCHAR(100),                             -- from CSV or manual input
    added_by INT REFERENCES users(id) ON DELETE SET NULL,  -- who submitted the expense
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Background tasks table (optional for async or scheduled work)
CREATE TABLE background_tasks (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(100),
    status TEXT CHECK (status IN ('queued', 'running', 'done', 'failed')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);