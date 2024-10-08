from db.database import create_db
from db.user_management import create_admin_user
from db.job_management import insert_job,insert_artifact

from db.prompt_management import insert_prompt

def create_dummy_job():
    insert_job("dummy")
    insert_artifact("dummy", "order.cbl", "cobol/", "reverse")

def create_dummy_prompts():
    insert_prompt("example-prompt-1", "This is an example content for prompt 1.")
    insert_prompt("example-prompt-2", "This is an example content for prompt 2.")

def init_db():
    create_db()
    create_admin_user()
    create_dummy_prompts()