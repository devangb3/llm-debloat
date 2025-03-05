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
import requests
import argparse
from dotenv import load_dotenv

def count_loc(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return len(lines)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading file: {e}")

# LLM Provider configurations
LLM_PROVIDERS = [
    "openai",
    "deepseek"
]

class LLMConfig:
    OPENAI_MODEL = "gpt-4"
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    TEMPERATURE = 0.2

def setup_environment():
    """Setup environment variables and API keys"""
    load_dotenv()
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "deepseek": os.getenv("DEEPSEEK_API_KEY")
    }
    
    if not all(api_keys.values()):
        missing = [k for k, v in api_keys.items() if not v]
        raise EnvironmentError(f"Missing API keys for: {', '.join(missing)}")
    
    return api_keys

def process_with_openai(code: str, api_key: str) -> str:
    """Process code using OpenAI API"""
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=LLMConfig.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a code optimization assistant."},
            {"role": "user", "content": f"Debloat this code while maintaining functionality:\n\n{code}"}
        ],
        temperature=LLMConfig.TEMPERATURE
    )
    return response.choices[0].message.content

def process_with_deepseek(code: str, api_key: str) -> str:
    """Process code using DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-coder",
        "messages": [{
            "role": "user",
            "content": f"Refactor this code to remove bloat while maintaining functionality:\n{code}"
        }],
        "temperature": LLMConfig.TEMPERATURE
    }
    
    response = requests.post(LLMConfig.DEEPSEEK_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def process_file(file_path: str, llm_provider: str, api_keys: dict) -> dict:
    """Process a file using specified LLM provider"""
    print(f"\n🔧 Processing with {llm_provider.upper()}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
        original_loc = count_loc(file_path)
    
    try:
        if llm_provider == "openai":
            response = process_with_openai(code, api_keys["openai"])
        elif llm_provider == "deepseek":
            response = process_with_deepseek(code, api_keys["deepseek"])
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        debloated_code = extract_code(response)
        
        # Create backup and save results
        backup_path = f"{file_path}.bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(code)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(debloated_code)
            
        new_loc = count_loc(file_path)
        return {
            'original_loc': original_loc,
            'new_loc': new_loc,
            'reduction': ((original_loc - new_loc)/original_loc)*100,
            'backup_path': backup_path
        }
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise

def extract_code(response_content):
    """Extract code from LLM response"""
    match = re.search(r'```python(.*?)```', response_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        raise ValueError("Error: Could not extract code from LLM response")

def main():
    parser = argparse.ArgumentParser(description='Code Debloater')
    parser.add_argument('file_path', help='Path to code file')
    parser.add_argument('--llm', type=int, default=0,
                      help=f'LLM provider index {list(enumerate(LLM_PROVIDERS))}')
    args = parser.parse_args()
    
    if not (0 <= args.llm < len(LLM_PROVIDERS)):
        print(f"Invalid LLM index. Choose from: {list(enumerate(LLM_PROVIDERS))}")
        sys.exit(1)
        
    try:
        api_keys = setup_environment()
        llm_provider = LLM_PROVIDERS[args.llm]
        metrics = process_file(args.file_path, llm_provider, api_keys)
        
        print(f"\n=== Code Metrics ===")
        print(f"Original LOC: {metrics['original_loc']}")
        print(f"New LOC:      {metrics['new_loc']}")
        print(f"Reduction:    {metrics['reduction']:.2f}%")
        print(f"Backup saved: {metrics['backup_path']}")
        print("====================")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

