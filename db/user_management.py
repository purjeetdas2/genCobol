
import hashlib
from .database import get_connection


def create_user(username, password, role):
    hashed_password = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password,role) VALUES (?, ? ,?)', (username, hashed_password,role))
    conn.commit()
    conn.close()

def verify_user(username, password):
    hashed_password = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    admin_username = 'admin'
    admin_password = 'admin'  # In a real-world scenario, use a more secure password
    if not verify_user(admin_username, admin_password):
        create_user(admin_username, admin_password,'ADMIN')



