import re
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["openai_apikey"])
# Configure OpenAI API key

def generate_code(business_rules_text, prompt_template):
    prompt = prompt_template.format(business_rules_text=business_rules_text)
    response = client.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=[
                                                  {"role": "system",
                                                   "content": "You are a programming expert with expertise in translating business rules into Java applications."},
                                                  {"role": "user", "content": prompt}
                                              ]
                                              )
    generation = response.choices[0].message.content.strip()
    return generation

def forward_engineer_cobol_program(business_rules_text):
    # Prompt template for OpenAI, structured to guide the transformation of COBOL rules into Java
    prompt_template = (
        "You are tasked with generating Java code from the following COBOL business rules. \n"
        "The Java application should utilize best practices and reflect efficient logic translation. Here's how to proceed:\n"
        "- Convert COBOL file operations to Java file handling.\n"
        "- Establish equivalent Java data structures (use classes like Order, Item).\n"
        "- Implement Java methods to replace COBOL procedures (e.g., Validate-Record, Transform-Record).\n"
        "- Conduct validity checks using Java conditions and handle exceptions.\n"
        "- Compose a simple example illustrating how part of the logic may be implemented in Java.\n\n"
        "Given COBOL rules:\n"
        "{business_rules_text}\n\n"
        "Generate the corresponding Java code. Begin with the primary class structure:"
    )

    print("Business rules sent for forward engineering:\n", business_rules_text)

    generated_code_text = generate_code(business_rules_text, prompt_template)

    # Compile all information into a comprehensive document
    document = (
        "Generated Forward Engineering Documentation\n\n"
        f"{generated_code_text}\n"
    )
    print(document)
    return document