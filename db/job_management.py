import sqlite3
from .database import get_connection


def insert_job(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO jobs (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def update_job_with_generated_doc(name,generated_doc):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("update artifacts set generated_doc = ? where job_id = ? ", (name,generated_doc))
    conn.commit()
    conn.close()

def get_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    print(jobs)
    return [job[0] for job in jobs]

def get_job(job_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_name,))
    job = cursor.fetchone()
    conn.close()
    return job

def get_generated_doc_for_job(job_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT art.generated_doc FROM jobs jb JOIN artifacts art ON jb.name = art.job_id WHERE jb.name = ? ", (job_name,))
    generated_doc = cursor.fetchone()
    conn.close()
    return generated_doc

def insert_artifact(job_name, filename, filepath, engineering_type):
    artifacts = get_artifacts(job_name)
    job = None;
    for artifact in artifacts:
        job=artifact['job_name']
        if filename == artifact['filename']:
            return

    if job is None:
        print(f"inserting the artifacts: {filename}")
        job_id = job_name
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO artifacts (job_id, filename, filepath,generated_doc, engineering_type) VALUES (?, ?, ?, ?,?)",
            (job_id, filename, filepath,"", engineering_type)
        )
        conn.commit()
        conn.close()


def get_artifacts(job_name):
    try:
        print(f"fetching the artifact for Job: {job_name}")
        conn = get_connection()
        cursor = conn.cursor()
        sql_query = """
            SELECT art.filename, art.filepath, jb.name 
            FROM jobs jb 
            JOIN artifacts art ON jb.name = art.job_id 
            WHERE jb.name = ?
        """
        cursor.execute(sql_query, (job_name,))
        artifacts = cursor.fetchall()
        print("Fetched artifacts:", artifacts)

        artifacts_response = []
        for artifact in artifacts:
            art = {
                "file_name": artifact[0],
                "file_path": artifact[1],
                "job_name": artifact[2]
            }
            artifacts_response.append(art)

        return artifacts_response

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        cursor.close()
        conn.close()


def create_dummy_job():
    insert_job("dummy")
    insert_artifact("dummy", "order.cbl", "cobol/", "reverse")