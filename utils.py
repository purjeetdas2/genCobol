import os

def save_uploaded_file(uploaded_file, task_type):
    save_path = f"./uploaded_files/{task_type}_{uploaded_file.name}"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

def render_header():
    return """
        <style>
            .header {
                background-color: #f8f9fa;
                padding: 10px 15px;
                border-bottom: 2px solid #e0e0e0;
            }
            .header-text {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        </style>
        <div class="header"><div class="header-text">Legacy Modernization Dashboard</div></div>
    """

def render_footer():
    return """
        <style>
            .footer {
                background-color: #f8f9fa;
                padding: 10px 15px;
                border-top: 2px solid #e0e0e0;
                left: 0;
                bottom: 0;
                width: 100%;
                text-align: center;
            }
            .footer-text {
                color: #777;
            }
        </style>
        <div class="footer"><div class="footer-text">© 2023 Legacy Modernization. All Rights Reserved.</div></div>
    """