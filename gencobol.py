import streamlit as st
from db.db_init import init_db
from db.job_management import get_jobs, insert_job ,insert_artifact,get_artifacts,get_generated_doc_for_job,update_job_with_generated_doc
from db.prompt_management import get_prompts, insert_prompt, delete_prompt, update_prompt
from authenticator import login_screen, logout
import os
import tempfile
import shutil
from engineering.reverse_engineering_executor import reverse_engineer_cobol_program
from engineering.forward_engineering_executor import forward_engineer_cobol_program


# Initialize the database
init_db()


# Function to display the Home Page
def home_page():
    st.title("Welcome to Code Engineering App")
    st.write("""
    This application uses generative AI for reverse and forward engineering of legacy code.
    - **Reverse Engineering**: Analyze legacy code and generate a high-level representation.
    - **Forward Engineering**: Convert high-level representations into modern code.
    """)
    st.subheader("Quick Start Guide")
    st.markdown("""
    ### Steps
    1. Go to the Engineering tab.
    2. Select a job or upload your mainframe JOB artifacts for reverse engineering.
    3. Choose Reverse or Forward Engineering.
    4. For Reverse Engineering, click 'Generate Reverse Engineering' to begin the process.
    5. For Forward Engineering, choose specific operations (e.g., Generate Skeleton, Core Components) and pass additional parameters.
    6. Click 'Generate' to produce the desired output.

    ### Additional Features
    - Manage AI prompts in the Prompt Management tab.
    - View execution history in the History tab.
    """)
    st.write("Use the tabs above to navigate between different modules.")


# Function to display Engineering Page (both Reverse and Forward)
def engineering_page():
    st.title("Engineering :gear:")
    st.write("Perform Reverse and Forward Engineering on your mainframe JOB artifacts.")

    job_action = st.radio("Select or Upload Job", ["Select Job", "Upload Job Artifacts"])
    selected_job = None

    if job_action == "Select Job":
        selected_job = st.selectbox("Select a job", get_jobs())

    elif job_action == "Upload Job Artifacts":
        uploaded_files = st.file_uploader("Upload mainframe JOB artifacts", type=["jcl", "cob", "proc", "cpy", "sbr"],
                                          accept_multiple_files=True)
        job_name = st.text_input("Enter job name")
        if uploaded_files and job_name and st.button("Upload Artifacts"):
            os.makedirs("uploaded_artifacts", exist_ok=True)
            insert_job(job_name)
            for file in uploaded_files:
                file_path = os.path.join("uploaded_artifacts", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                insert_artifact(job_name, file.name, file_path, "Reverse")
            st.success(f"Uploaded artifacts for job: {job_name}")
            selected_job = job_name

    if selected_job:
        st.subheader(f"Job: {selected_job}")

        artifacts = get_artifacts(selected_job)
        selected_artifact_content= None
        if artifacts:
         for artifact in artifacts:
            if st.checkbox(f" {artifact['file_name']}"):
                with open(artifact['file_path'], "r") as file:
                    selected_artifact_content= file.read()


        engineering_option = st.radio("Choose Engineering Type", ["Reverse Engineering", "Forward Engineering"])

        if engineering_option == "Reverse Engineering":
            if st.button("Execute Reverse Engineering"):
                if selected_artifact_content:
                    generate_reverse_engineering(selected_artifact_content,selected_job)
                    st.success(f"Generated BRE for job: {selected_job}")

        elif engineering_option == "Forward Engineering":
            forward_tasks = st.multiselect(
                "Select Forward Engineering Tasks",
                ["Generate Skeleton", "Generate Core Components", "Generate Units", "Generate Entities"]
            )
            additional_params = st.text_area("Additional Parameters (Optional)")

            if st.button("Execute Forward Engineering"):
                for task in forward_tasks:
                    st.write(f"Generating {task} for job: {selected_job} with parameters: {additional_params}")
                    generate_forward_engineering(selected_job, task, additional_params)
                st.success(f"Generated specified components for job: {selected_job}")


# Function to display Execution History Page
def history_page():
    st.title("Execution History :notebook:")
    st.write("View the history of reverse and forward engineering executions.")
    history_type = st.selectbox("Select History Type", ["Reverse", "Forward"])
    if history_type == "Reverse":
        st.write("Displaying Reverse Engineering History ...")
    else:
        st.write("Displaying Forward Engineering History ...")


# Function to display Prompt Management Page
def prompt_management_page():
    st.title("Prompt Management :spiral_notepad:")
    st.write("Manage AI prompts for custom code generation.")

    prompt_action = st.radio("Choose an action", ["Add New Prompt", "Edit Prompt", "Delete Prompt"])
    prompt_names = get_prompts() if prompt_action != "Add New Prompt" else None

    if prompt_action == "Add New Prompt":
        prompt_name = st.text_input("Enter prompt name")
        prompt_content = st.text_area("Enter prompt content")
        if st.button("Add Prompt"):
            insert_prompt(prompt_name, prompt_content)
            st.success("Prompt added successfully")
    elif prompt_action == "Edit Prompt":
        selected_prompt = st.selectbox("Select Prompt to Edit", prompt_names)
        prompt_content = st.text_area("Enter new prompt content")
        if st.button("Update Prompt"):
            update_prompt(selected_prompt, prompt_content)
            st.success("Prompt updated successfully")
    elif prompt_action == "Delete Prompt":
        selected_prompt = st.selectbox("Select Prompt to Delete", prompt_names)
        if st.button("Delete Prompt"):
            delete_prompt(selected_prompt)
            st.success("Prompt deleted successfully")


# Function to display Settings Page
def settings_page():
    st.title("Settings :gear:")
    st.write("User preferences and settings")
    st.subheader("Notification Preferences")
    email_notifications = st.checkbox("Enable Email Notifications", value=True)
    app_notifications = st.checkbox("Enable In-App Notifications", value=True)


def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        tabs = ["Home", "Engineering", "History", "Prompt Management", "Settings"]
        selected_tab = st.sidebar.radio("Navigation", tabs)

        if selected_tab == "Home":
            home_page()
        elif selected_tab == "Engineering":
            engineering_page()
        elif selected_tab == "History":
            history_page()
        elif selected_tab == "Prompt Management":
            prompt_management_page()
        elif selected_tab == "Settings":
            settings_page()

        st.sidebar.button("Logout", on_click=logout)
    else:
        login_screen()

# Check if Pandoc is installed
def is_pandoc_installed():
    return shutil.which('pandoc') is not None

# Placeholder functions to avoid errors
def generate_reverse_engineering(cobol_code,job_name):
    # Check if a document has already been generated

    generated_doc = get_generated_doc_for_job(job_name)
    response = None
    if generated_doc:
        file_path = os.path.join(os.getcwd(),generated_doc[0])


        if file_path:
            with open(file_path, "rb") as f:
                response = f.read()
    else:
        response = reverse_engineer_cobol_program(cobol_code)
        file_path = os.path.join("uploaded_artifacts", f"{job_name}-reverse-engineering.txt")
        st.write("Contents of the directory:", os.listdir())
        st.write("Attempting to open:", file_path)
        with open(file_path, "wb") as f:
            f.write(response.encode('utf-8'))
        update_job_with_generated_doc(job_name,file_path)
        print("Done with reverse engineering")

    st.markdown(response.decode('utf-8'))
    """
    if is_pandoc_installed():
        import pypandoc
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
            pypandoc.convert_text(response, 'docx', format='md', outputfile=tmp_docx.name)
            with open(tmp_docx.name, 'rb') as file:
                st.download_button(
                    label="Download BRE",
                    data=file,
                    file_name='document.docx',
                    mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
        os.unlink(tmp_docx.name)
    else:
        st.error("Pandoc is not installed. Please install Pandoc to enable DOCX download.")
    """


def generate_forward_engineering(job_name, task, configurations):

    generated_doc = get_generated_doc_for_job(job_name)
    response = None
    if generated_doc:
        file_path = os.path.join(generated_doc[0])
        if file_path:
            with open(file_path, "rb") as f:
                response = f.read()

        response = forward_engineer_cobol_program(response)
        file_path = os.path.join("uploaded_artifacts", f"{job_name}-forward-engineering.txt")
        with open(file_path, "wb") as f:
            f.write(response.encode('utf-8'))
        update_job_with_generated_doc(job_name, file_path)
        print("Done with forward engineering")
    st.markdown(response)
    """
    if is_pandoc_installed():
        import pypandoc
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
            pypandoc.convert_text(response, 'docx', format='md', outputfile=tmp_docx.name)
            with open(tmp_docx.name, 'rb') as file:
                st.download_button(
                    label="Download Generated Code",
                    data=file,
                    file_name='document.docx',
                    mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
        os.unlink(tmp_docx.name)
    else:
        st.error("Pandoc is not installed. Please install Pandoc to enable DOCX download.")
    """

if __name__ == "__main__":
    main()