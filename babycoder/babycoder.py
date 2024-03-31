import os
import openai
import time
import json
import subprocess
from typing import List, Dict, Union, Any, Optional
import sys
from dotenv import load_dotenv

load_dotenv()
current_directory = os.getcwd()
os_version = platform.release()

openai_calls_retried = 0
max_openai_calls_retries = 3

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
assert OPENAI_API_KEY, "OPENAI_API_KEY environment variable is missing from .env"
openai.api_key = OPENAI_API_KEY

OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo")
assert OPENAI_API_MODEL, "OPENAI_API_MODEL environment variable is missing from .env"

if "gpt-4" in OPENAI_API_MODEL.lower():
    print(
        f"\033[91m\033[1m"
        + "\n*****USING GPT-4. POTENTIALLY EXPENSIVE. MONITOR YOUR COSTS*****"
        + "\033[0m\033[0m"
    )

def print_colored_text(text: str, color: str):
    color_mapping = {
        'blue': '\033[34m',
        'red': '\033[31m',
        'yellow': '\033[33m',
        'green': '\033[32m',
    }
    color_code = color_mapping.get(color.lower(), '')
    reset_code = '\033[0m'
    print(color_code + text + reset_code)

def print_char_by_char(text: str, delay: float = 0.00001, chars_at_once: int = 3):
    for i in range(0, len(text), chars_at_once):
        chunk = text[i:i + chars_at_once]
        print(chunk, end='', flush=True) 
        time.sleep(delay) 
    print()

def openai_call(
    prompt: str,
    model: str = OPENAI_API_MODEL,
    temperature: float = 0.5,
    max_tokens: int = 100,
) -> Optional[str]:
    global openai_calls_retried
    if not model.startswith("gpt-"):
        try:
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            openai_calls_retried = 0
            return response.choices[0].text.strip()
        except Exception as e:
            if openai_calls_retried < max_openai_calls_retries:
                openai_calls_retried += 1
                print(f"Error calling OpenAI. Retrying {openai_calls_retried} of {max_openai_calls_retries}...")
                return openai_call(prompt, model, temperature, max_tokens)
    else:
        # Use chat completion API
        messages=[{"role": "user", "content": prompt}]
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stop=None,
            )
            openai_calls_retried = 0
            return response.choices[0].message.content.strip()
        except Exception as e:
            if openai_calls_retried < max_openai_calls_retries:
                openai_calls_retried += 1
                print(f"Error calling OpenAI. Retrying {openai_calls_retried} of {max_openai_calls_retries}...")
                return openai_call(prompt, model, temperature, max_tokens)

def execute_command_json(json_string: str) -> str:
    try:
        command_data = json.loads(json_string)
        full_command = command_data.get('command')
        
        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, cwd='playground')
        stdout, stderr = process.communicate(timeout=60)

        return_code = process.returncode

        if return_code == 0:
            return stdout
        else:
            return stderr

    except json.JSONDecodeError as e:
        return f"Error: Unable to decode JSON string: {str(e)}"
    except subprocess.TimeoutExpired:
        process.terminate()
        return "Error: Timeout reached (60 seconds)"
    except Exception as e:
        return f"Error: {str(e)}"

def execute_command_string(command_string: str) -> str:
    try:
        result = subprocess.run(command_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, cwd='playground')
        output = result.stdout or result.stderr or "No output
