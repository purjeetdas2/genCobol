import sqlite3
from .database import get_connection

def insert_prompt(name, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO prompts (name, content) VALUES (?, ?)", (name, content))
    conn.commit()
    conn.close()

def get_prompts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM prompts")
    prompts = cursor.fetchall()
    conn.close()
    return [prompt[0] for prompt in prompts]

def delete_prompt(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prompts WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def update_prompt(name, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE prompts SET content = ? WHERE name = ?", (content, name))
    conn.commit()
    conn.close()