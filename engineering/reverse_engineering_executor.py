import re
from openai import OpenAI
import streamlit as st



client = OpenAI(api_key=st.secrets["openai_apikey"])

# Configure OpenAI API key

def extract_and_explain(cobol_code, patterns, prompt_template):
    explanations = []
    for label, pattern in patterns.items():
        matches = re.finditer(pattern, cobol_code, re.DOTALL)
        for match in matches:
            code_segment = match.group(0).strip()
            prompt = prompt_template.format(code_segment=code_segment)
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a natural language expert."},
                {"role": "user", "content": prompt}
            ])

            explanation = response.choices[0].message.content.strip()
            explanations.append((label, code_segment, explanation))
    return explanations

def reverse_engineer_cobol_program(cobol_code):
    # Define regex patterns for COBOL divisions and constructs
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

    # Prompt template for OpenAI
    prompt_template = "Explain the following COBOL code segment in detail, focusing on its role in the program's business logic:\n{code_segment}"

    # Extract and explain each part of the COBOL program
    detailed_explanations = extract_and_explain(cobol_code, patterns, prompt_template)

    # Compile all explanations into a comprehensive document
    document = "COBOL Program Detailed Documentation\n\n"
    for label, code_segment, explanation in detailed_explanations:
        document += f"{label} Segment:\n{code_segment}\nExplanation:\n{explanation}\n\n"


    return document