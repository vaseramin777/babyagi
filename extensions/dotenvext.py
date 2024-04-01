import os
from dotenv import find_dotenv, load_dotenv

def load_dotenv_extensions(dotenv_files):
    for dotenv_file in dotenv_files:
        try:
            load_dotenv(dotenv_file)
        except Exception as e:
            print(f"Error loading {dotenv_file}: {e}")

# Load .env files in the following order, with later files overwriting earlier ones
load_dotenv_extensions([
    find_dotenv(".env.local", raise_error_if_not_found=False),
    find_dotenv(".env.development.local", raise_error_if_not_found=False),
    find_dotenv(".env.development"),
    find_dotenv(".env.local"),
    find_dotenv(".env"),
])

# Set environment variables with a prefix of REACT_APP_
os.environ["REACT_APP_API_KEY"] = "your-api-key"
