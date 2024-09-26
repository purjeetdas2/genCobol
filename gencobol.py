import streamlit as st
from db.database import (
    init_db, get_jobs, insert_job, insert_artifact, get_prompts, insert_prompt, delete_prompt, update_prompt
)
from authenticator import login_screen, logout
import os

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
        ### Reverse Engineering
        This module supports artifacts like JCL, COBOL, PROC, COPYBOOK, and SUBROUTINE. Follow the steps below:
        1. Go to [Reverse Engineering](#reverse_engineering) using the sidebar.
        2. Choose to upload your mainframe JOB artifacts or select a job name from the local directory.
        3. Upload files or select the job name.
        4. Click 'Generate' to begin the reverse engineering process.

        ### Forward Engineering
        1. Go to [Forward Engineering](#forward_engineering) using the sidebar.
        2. Upload the reverse-engineered file.
        3. Configure settings.
        4. Click 'Generate' to produce modern code.

        ### Additional Features
        - Manage AI prompts in the [Prompt Management](#prompt_management) section.
        - View execution history in the [History](#history) section.
    """)
    st.write("Use the sidebar to navigate between different modules.")


# Function to display Reverse Engineering Page
def reverse_engineering_page():
    st.title("Reverse Engineering :mag_right:")
    st.write(
        "Analyze mainframe JOB artifacts (JCL, COBOL, PROC, COPYBOOK, SUBROUTINE) and generate a high-level representation.")

    # Option to upload files or select from local directory
    upload_method = st.radio("Choose how to provide job artifacts", ["Upload Files", "Select from Local Directory"])

    if upload_method == "Upload Files":
        uploaded_files = st.file_uploader("Upload mainframe JOB artifacts", type=["jcl", "cob", "proc", "cpy", "sbr"],
                                          accept_multiple_files=True)
        job_name = st.text_input("Enter job name")

        if uploaded_files and job_name:
            insert_job(job_name)
            for file in uploaded_files:
                file_path = os.path.join("uploaded_artifacts", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                engineering_type = "Reverse"
                insert_artifact(job_name, file.name, file_path, engineering_type)
            st.success(f"Uploaded artifacts for job: {job_name}")

        if st.button("Generate"):
            generate_reverse_engineering(job_name)
            st.success(f"Generated high-level representation for job: {job_name}")
            """
            # Display a preview option for each artifact
            artifacts = get_artifacts(job_name)
            for artifact in artifacts:
                if st.checkbox(f"Preview {artifact['file_name']}"):
                    with open(artifact['file_path'], "r") as file:
                        st.code(file.read())
            """

    elif upload_method == "Select from Local Directory":
        local_job_names = get_jobs()
        selected_job = st.selectbox("Select the job name", local_job_names)

        if selected_job and st.button("Generate"):
            generate_reverse_engineering(selected_job)


# Function to display Forward Engineering Page
def forward_engineering_page():
    st.title("Forward Engineering :fast_forward:")
    st.write("Convert high-level representations into modern code.")

    uploaded_file = st.file_uploader("Upload reverse-engineered code", type=["txt", "py", "java"])
    configurations = st.text_area("Configurations")

    if uploaded_file:
        file_path = os.path.join("uploaded_artifacts", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        job_name = "Forward_Job_" + os.path.splitext(uploaded_file.name)[0]
        insert_job(job_name)
        engineering_type = "Forward"
        insert_artifact(job_name, uploaded_file.name, file_path, engineering_type)
        st.success(f"Uploaded artifact and generated modern code for job: {job_name}")

    if st.button("Generate"):
        generate_forward_engineering(uploaded_file, configurations)


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

    prompt_action = st.radio("Choose an action", ("Add New Prompt", "Edit Prompt", "Delete Prompt"))

    if prompt_action == "Add New Prompt":
        prompt_name = st.text_input("Enter prompt name")
        prompt_content = st.text_area("Enter prompt content")

        if st.button("Add Prompt"):
            insert_prompt(prompt_name, prompt_content)
            st.success("Prompt added successfully")

    elif prompt_action == "Edit Prompt":
        prompt_names = get_prompts()
        selected_prompt = st.selectbox("Select Prompt to Edit", prompt_names)
        prompt_content = st.text_area("Enter new prompt content")

        if st.button("Update Prompt"):
            update_prompt(selected_prompt, prompt_content)
            st.success("Prompt updated successfully")

    elif prompt_action == "Delete Prompt":
        prompt_names = get_prompts()
        selected_prompt = st.selectbox("Select Prompt to Delete", prompt_names)

        if st.button("Delete Prompt"):
            delete_prompt(selected_prompt)
            st.success("Prompt deleted successfully")


# Function to display Settings Page
def settings_page():
    st.title("Settings :gear:")
    st.write("User preferences and settings")

    # Notification preferences
    st.subheader("Notification Preferences")
    email_notifications = st.checkbox("Enable Email Notifications", value=True)
    app_notifications = st.checkbox("Enable In-App Notifications", value=True)



def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        st.sidebar.title("Navigation")

        pages = {
            "Home": home_page,
            "Reverse Engineering": reverse_engineering_page,
            "Forward Engineering": forward_engineering_page,
            "History": history_page,
            "Prompt Management": prompt_management_page,
            "Settings": settings_page
        }

        choice = st.sidebar.selectbox("Select a page", list(pages.keys()))

        if choice and pages.get(choice):
            pages[choice]()
        logout()
    else:
        login_screen()




# Placeholder functions to avoid errors
def generate_reverse_engineering(job_name):
    st.code(f"Generated high-level representation for job: {job_name}")



def generate_forward_engineering(file, configurations):
    st.code("Generated modern code based on reverse-engineered file and configurations.")


if __name__ == "__main__":
    main()