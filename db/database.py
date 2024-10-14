import sqlite3

DATABASE = 'job_artifacts.db'

def get_connection():
    return sqlite3.connect(DATABASE)

def create_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(''' CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    ) ''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    ) ''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS artifacts (
        id INTEGER PRIMARY KEY,
        job_id INTEGER,
        job_name TEXT,
        filename TEXT,
        filepath TEXT,
        generated_doc TEXT,
        generated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        engineering_type TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    ) ''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        content TEXT NOT NULL
    ) ''')
    conn.commit()
    conn.close()



