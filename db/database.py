import sqlite3
import os
import hashlib
DATABASE = 'job_artifacts.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS users (
               username TEXT PRIMARY KEY,
               password TEXT NOT NULL
           )
       ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artifacts (
            id INTEGER PRIMARY KEY,
            job_id INTEGER,
            filename TEXT,
            filepath TEXT,
            generated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            engineering_type TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    create_admin_user()

def create_admin_user():
    admin_username = 'admin'
    admin_password = 'admin'  # In a real-world scenario, use a more secure password
    if not verify_user(admin_username, admin_password):
        create_user(admin_username, admin_password)
def get_jobs():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    return [job[0] for job in jobs]

def insert_job(name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO jobs (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def insert_artifact(job_name, filename, filepath, engineering_type):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM jobs WHERE name = ?", (job_name,))
    job_id = cursor.fetchone()
    if job_id:
        job_id = job_id[0]
        cursor.execute(
            "INSERT INTO artifacts (job_id, filename, filepath, engineering_type) VALUES (?, ?, ?, ?)",
            (job_id, filename, filepath, engineering_type)
        )
        conn.commit()
    conn.close()

def get_prompts():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM prompts")
    prompts = cursor.fetchall()
    conn.close()
    return [prompt[0] for prompt in prompts]

def insert_prompt(name, content):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO prompts (name, content) VALUES (?, ?)", (name, content))
    conn.commit()
    conn.close()

def delete_prompt(name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prompts WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def update_prompt(name, content):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE prompts SET content = ? WHERE name = ?", (content, name))
    conn.commit()
    conn.close()

def create_user(username, password):
    hashed_password = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()

def verify_user(username, password):
    hashed_password = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()