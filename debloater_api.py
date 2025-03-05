"""
This script takes a Python file as input, sends its content to a specified LLM API (ChatGPT by default) 
with a customizable prompt to debloat the code, and writes the response back to the original file.

Usage:
    python debloat_script.py <path_to_python_file>

Requirements:
    - Python 3.x
    - openai and python-dotenv packages (install with pip install openai python-dotenv)
    - A .env file with OPENAI_API_KEY=your-api-key-here

Note:
    This script overwrites the original file. Make sure to back up your code before running it.
"""

import openai
import os
import sys
import re
from dotenv import load_dotenv

def count_loc(code: str) -> int:
    """Count lines of code ignoring comments and blanks"""
    return sum(1 for line in code.split('\n') 
              if line.strip() and not line.strip().startswith(('#', '//')))

# Configuration: Specify LLM provider and API details here
LLM_PROVIDER = "openai"  # Default LLM provider. Change to "other_llm" if extending to another LLM
API_KEY_VAR = "OPENAI_API_KEY"  # Environment variable name for the API key in .env

# Customizable prompt
CUSTOM_PROMPT = (
    "Here is a Python code:\n\n{code}\n\n"
    "Please debloat it by removing unnecessary parts while keeping the functionality the same. "
    "Return only the debloated code wrapped in triple backticks (```python ... ```)."
)

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv(API_KEY_VAR)
if not api_key:
    print(f"Error: {API_KEY_VAR} not found in .env file")
    sys.exit(1)

# Check if the file path is provided
if len(sys.argv) < 2:
    print("Usage: python debloat_script.py <path_to_python_file>")
    sys.exit(1)

file_path = sys.argv[1]

# Check if the file exists
if not os.path.exists(file_path):
    print(f"Error: File {file_path} does not exist")
    sys.exit(1)

# Read the content of the file
print(f"Reading file: {file_path}")
with open(file_path, 'r', encoding='utf-8') as file:
    code = file.read()
    original_loc = count_loc(code)
    print(f"Original LOC: {original_loc}")

# Prepare the prompt with the code
prompt = CUSTOM_PROMPT.format(code=code)

# Set up the LLM client based on the provider
if LLM_PROVIDER == "openai":
    client = openai.OpenAI(api_key=api_key)
    try:
        print("Sending code to ChatGPT for debloating...")
        response = client.chat.completions.create(
            model="gpt-4o",  # You can change to "gpt-4" if available
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2  # Lower temperature for more deterministic output
        )
        # Extract the content from the response
        response_content = response.choices[0].message.content
        # Use regex to extract the code between ```python and ```
        match = re.search(r'```python(.*?)```', response_content, re.DOTALL)
        if match:
            debloated_code = match.group(1).strip()
            new_loc = count_loc(debloated_code)
            reduction = ((original_loc - new_loc) / original_loc) * 100
            
            print("\n=== Code Metrics ===")
            print(f"Original LOC: {original_loc}")
            print(f"New LOC:      {new_loc}")
            print(f"Reduction:    {reduction:.2f}%")
            print("==================")
        else:
            print("Error: Could not extract code from LLM response")
            sys.exit(1)
    except openai.error.OpenAIError as e:
        print(f"Error: API request failed: {e}")
        sys.exit(1)
else:
    # Placeholder for other LLM providers
    print(f"Error: LLM provider '{LLM_PROVIDER}' is not implemented yet")
    sys.exit(1)
    # Example extension for another LLM:
    # elif LLM_PROVIDER == "other_llm":
    #     client = OtherLLMClient(api_key=api_key)
    #     response = client.call(prompt)

# Warn the user before overwriting the file
print("\nWarning: This will overwrite the original file. Make sure to back up your code.")
confirm = input("Proceed? (y/n): ")
if confirm.lower() != 'y':
    print("Aborted.")
    sys.exit(0)

# Create backup of original file
backup_path = f"{file_path}.bak"
print(f"Creating backup at: {backup_path}")
with open(backup_path, 'w', encoding='utf-8') as backup:
    backup.write(code)

# Write the debloated code back to the original file
print(f"Writing debloated code to {file_path}")
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(debloated_code)

print(f"Debloated code has been successfully written to {file_path}")
print(f"Original code backed up to {backup_path}")