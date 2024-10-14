import re
from openai import OpenAI
import streamlit as st



client = OpenAI(api_key=st.secrets["openai_apikey"])

# Configure OpenAI API key
def summarize_cobol_code(cobol_code):
    """Generate a summary of the COBOL code using a language model."""
    template = """
        Understand the Code: - Review the COBOL program thoroughly. Identify the program’s purpose and overall functionality. - If possible, run the code in a test environment and observe how it behaves with sample data. 
	1	State the High-Level Purpose: - Begin by explaining the main goal* of the COBOL program. For instance, is it processing financial transactions, generating reports, or managing records? Clarify what problem or task the code is intended to address. 
	2	Break Down Key Divisions: - COBOL programs typically have four divisions (Identification, Environment, Data, and Procedure). Walk through each section and explain its role:  
	   - Identification Division: What is the program name and purpose as declared here? - Environment Division: Which system configurations and files are used? 
	   - Data Division: Highlight the key data structures (working-storage section, file section). What are the critical files and records the program is working with? 
	   - Procedure Division: Explain the core logic. What steps is the code executing to achieve the goal? 
	3	Explain the Data Flow: - Identify the input files or data the program processes, how the data is read, manipulated, and then written or displayed as output. - Walk through how the data moves through different paragraphs or sections. 
	4	Detail Key Variables and Structures: - Point out important data elements and explain their significance. For example, are there any specific records or fields that the program frequently accesses or modifies? What are the key 88-level conditions? 
	5	Explain Control Flow and Logic: - Explain how the logic is structured. Identify the key PERFORM loops, IF conditions, and any GO TO statements or EXIT points. - Break down major routines or paragraphs and describe their purpose. What are the core processing steps?
	6	Simplify Complex Operations: - For any tricky parts (like advanced file handling, arithmetic calculations, or COBOL-specific constructs), offer a simpler explanation using plain language. What is the intent behind the more complex logic?  
	7	Summarize the Main Functionality: - Conclude by summarizing the key operations and outputs of the code. Mention any risks or areas for improvement related to outdated practices, inefficiencies, or maintainability. 
    """
    prompt = f"{template}:\n{cobol_code}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a natural language expert skilled at mainframe program logic."},
            {"role": "user", "content": prompt}
        ]
    )
    summary = response.choices[0].message.content.strip()
    return summary


def describe_flow_diagram(cobol_code):
    """Conceptually describe the flow diagram of the COBOL code."""
    # This would typically involve parsing the flow and decisions, simplifying it here
    # For an actual diagram, integrating with a visualization library would be necessary
    return """
    1. Start: Initialize the program.
    2. Process: Read input data and validate.
    3. Decision: Check conditions such as 'IF' statements.
    4. Loop: Execute 'PERFORM' for repeated operations.
    5. Action: Update or compute data as needed.
    6. End: Output results and close processes.
    """


def extract_and_explain(cobol_code, patterns, prompt_template):
    """Extract code segments from COBOL and provide detailed explanations."""
    explanations = []
    for label, pattern in patterns.items():
        matches = re.finditer(pattern, cobol_code, re.DOTALL)
        for match in matches:
            code_segment = match.group(0).strip()
            prompt = prompt_template.format(code_segment=code_segment)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a natural language expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            explanation = response.choices[0].message.content.strip()
            explanations.append((label, code_segment, explanation))
    return explanations


def reverse_engineer_cobol_program(cobol_code):
    """Reverse engineers a COBOL program, summarizing and detailing its components."""
    patterns = {
        "IDENTIFICATION": r"IDENTIFICATION\s+DIVISION\..*?(?=(ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION)",
        "ENVIRONMENT": r"ENVIRONMENT\s+DIVISION\..*?(?=(DATA|PROCEDURE)\s+DIVISION)",
        "DATA": r"DATA\s+DIVISION\..*?(?=PROCEDURE\s+DIVISION)",
        "PROCEDURE": r"PROCEDURE\s+DIVISION\..*",
        "IF": r"IF\s+.*?END-IF\.",
        "PERFORM": r"PERFORM\s+[A-Z0-9-]+(?:\s+UNTIL\s+[\w\s=]*)?\.",
        "MOVE": r"MOVE\s+.*?\.",
        "COMPUTE": r"COMPUTE\s+.*?\.",
        "FILE": r"(READ|WRITE|OPEN|CLOSE)\s+.*?\."
    }

    prompt_template = "Explain the following COBOL code segment in detail, focusing on its role in the program's business logic:\n{code_segment}"

    # Generate a summary and describe the flow diagram
    summary = summarize_cobol_code(cobol_code)
    #flow_diagram_description = describe_flow_diagram(cobol_code)

    # Extract and explain each part of the COBOL program
    #detailed_explanations = extract_and_explain(cobol_code, patterns, prompt_template)

    # Compile all components into a comprehensive document
    document = "COBOL Program Documentation\n\n"
    document += f"Summary:\n{summary}\n"
    #document += f"Summary:\n{summary}\n\nFlow Diagram:\n{flow_diagram_description}\n\n"
    """
    for label, code_segment, explanation in detailed_explanations:
        document += f"{label} Segment:\n{code_segment}\nExplanation:\n{explanation}\n\n"
    """
    return document
