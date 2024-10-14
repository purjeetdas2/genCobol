import streamlit as st
from db.db_init import init_db
from streamlit_option_menu import option_menu
from db.job_management import get_jobs, insert_job ,insert_artifact,get_artifacts,get_generated_doc_for_job,update_job_with_generated_doc
from db.prompt_management import get_prompts, insert_prompt, delete_prompt, update_prompt
from authenticator import login_screen, logout
import os
import base64
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

    st.title("Engineering")
    st.markdown("""
        **Reverse engineer your legacy code, including mainframe COBOL, subroutines, and JCL, to extract valuable insights and facilitate modernization.**
        Select an existing workflow or upload new code artifacts using the options below.
        """)

    # Step 1: Job Selection or Upload
    st.subheader("Step 1: Choose an existing code artifact or upload a new one")
    job_action = st.radio("Choose an Option:", ["Select Existing Code", "Upload New Code Artifacts"])

    selected_job = None
    if job_action == "Select Existing Code":
        selected_job = st.selectbox("Select Code Artifact(s)", get_jobs(), help="Choose from existing code artifact.")
    else:
        with st.expander("Upload New Code Artifacts",expanded=True):
            uploaded_files = st.file_uploader(
                "Upload mainframe Code artifacts",
                type=["jcl", "cob", "proc", "cpy", "sbr"],
                accept_multiple_files=True
            )
            job_name = st.text_input("Enter Job Name")
            if st.button("Upload Artifacts"):
                if uploaded_files and job_name:
                    os.makedirs("uploaded_artifacts", exist_ok=True)
                    job = insert_job(job_name)
                    for file in uploaded_files:
                        file_path = os.path.join("uploaded_artifacts", file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.read())
                        insert_artifact(job[0],job_name, file.name, file_path, "Reverse")
                    st.success(f"Uploaded artifacts for job: {job_name}")
                    selected_job = job_name
                else:
                    st.error("Please upload files and provide a job name.")

    # Step 2: Artifact Selection
    if selected_job:
        st.subheader(f"Step 2: Select Artifacts for '{selected_job}'")
        artifacts = get_artifacts(selected_job)
        if artifacts:
            artifact_options = [artifact['file_name'] for artifact in artifacts]
            selected_artifact_name = st.selectbox("Select an Artifact", artifact_options)
            selected_artifact_content = None
            for artifact in artifacts:
                if artifact['file_name'] == selected_artifact_name:
                    with open(artifact['file_path'], "r") as file:
                        selected_artifact_content = file.read()
                    break

            # Step 3: Engineering Type Selection
            st.subheader("Step 3: Choose Engineering Type")
            engineering_option = st.radio("Engineering Type", ["Reverse Engineering", "Forward Engineering"],
                                          horizontal=True)

            # Step 4: Execution
            if engineering_option == "Reverse Engineering":
                if st.button("Execute Reverse Engineering"):
                    if selected_artifact_content:
                        generate_reverse_engineering(selected_artifact_content, selected_job)
                        st.success(f"Generated BRE for job: {selected_job}")
                    else:
                        st.error("Please select an artifact to process.")
            elif engineering_option == "Forward Engineering":
                forward_tasks = st.multiselect(
                    "Select Forward Engineering Tasks",
                    ["Converted Code (Spring Boot)"]
                )
                additional_params = st.text_area("Additional Parameters (Optional)")
                if st.button("Execute Forward Engineering"):
                    if forward_tasks:
                        for task in forward_tasks:
                            st.write(
                                f"Generating {task} for job: {selected_job} with parameters: {additional_params if additional_params else 'None'}")
                            generate_forward_engineering(selected_job, task, additional_params)
                        st.success(f"Generated specified components for job: {selected_job}")
                    else:
                        st.error("Please select at least one forward engineering task.")

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
    # Check if user is logged in
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        launch_home()
    else:
        login_screen()


def launch_home():
    # Place option menu in the sidebar
    with st.sidebar:
        selected_tab = option_menu(
            "Navigation",
            ["Home", "Engineering", "History", "Prompt Management", "Settings"],
            icons=['house', 'gear', 'clock-history', 'journal-text', 'gear'],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "5!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )

        st.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
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


# Check if Pandoc is installed
def is_pandoc_installed():
    return shutil.which('pandoc') is not None

# Placeholder functions to avoid errors
def generate_reverse_engineering(cobol_code,job_name):
    # Check if a document has already been generated
    generated_doc = None
    #generated_doc = get_generated_doc_for_job(job_name)
    response = None
    if generated_doc:
        file_path = os.path.join(os.getcwd(),generated_doc[0])
        if file_path:
            with open(file_path, "rb") as f:
                response = f.read()
    else:
        with st.spinner("Wait for it..."):
            response = reverse_engineer_cobol_program(cobol_code)
            file_path = os.path.join("uploaded_artifacts", f"{job_name}-reverse-engineering.txt")
            with open(file_path, "wb") as f:
                f.write(response.encode('utf-8'))
            update_job_with_generated_doc(job_name,file_path)
            print("Done with reverse engineering")
    # Display an icon alongside a download button using Streamlit components
    # Image URL or path to use as the button]
    # Encode the response for download
    b64 = base64.b64encode(response.encode()).decode()

    # Define the download filename
    file_name = 'summary.txt'
    button_image_url = "https://img.icons8.com/material-outlined/48/000000/download.png"  # You can replace this with your own image URL

    # Creating a clickable image link to act as a download button
    button_html = f"""
        <a href="data:file/txt;base64,{b64}" download="{file_name}">
            <img src="{button_image_url}" alt="Download Summary" style="cursor: pointer;"/>
        </a>
    """

    # Display the image as a button
    st.markdown(button_html, unsafe_allow_html=True)

    # Use an expander to show the summary preview
    with st.expander("View SUMMARY",expanded=True):
        st.markdown(response)


def generate_forward_engineering(job_name, task, configurations):

    generated_doc = get_generated_doc_for_job(job_name)
    response = None
    if generated_doc:
        file_path = os.path.join(generated_doc[0])
        if file_path:
            with open(file_path, "rb") as f:
                response = f.read()
        with st.spinner("Wait for it..."):
            response = forward_engineer_cobol_program(response)
            file_path = os.path.join("uploaded_artifacts", f"{job_name}-forward-engineering.txt")
            with open(file_path, "wb") as f:
                f.write(response.encode('utf-8'))
            update_job_with_generated_doc(job_name, file_path)
            print("Done with forward engineering")

    b64 = base64.b64encode(response.encode()).decode()

    # Define the download filename
    file_name = 'summary.txt'
    button_image_url = "https://img.icons8.com/material-outlined/48/000000/download.png"  # You can replace this with your own image URL

    # Creating a clickable image link to act as a download button
    button_html = f"""
          <a href="data:file/txt;base64,{b64}" download="{file_name}">
              <img src="{button_image_url}" alt="Download Summary" style="cursor: pointer;"/>
          </a>
      """

    # Display the image as a button
    st.markdown(button_html, unsafe_allow_html=True)

    # Use an expander to show the summary preview
    with st.expander("View Generated Code"):
        st.code(response)


def add_custom_css():
    st.markdown("""
        <style>
            /* Customize font and other styles here */
            .main {
                font-family: "Arial", sans-serif;
            }
            header, footer {
                visibility: hidden;
            }
            .css-10trblm {
                border-radius: 5px !important;
                border: 1px solid #ddd !important;
                padding: 15px;
            }
            h1, h2, h3, h4 {
                font-weight: 600 !important;
            }
             /* Adjust the font size of subheaders */
            h3 {
              font-size: 20px; /* Example font size */
              color: #333333;  /* Ensure color visibility based on theme */
            }
            .stRadio > div {
                flex-direction: row;
            }
            .stButton > button {
                background-color: #1E90FF !important;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            /* Add more styles as needed */
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    add_custom_css()
    main()