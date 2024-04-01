from skills.skill import Skill
import openai
import os

class CodeReader(Skill):
    name = 'code_reader'
    description = "A skill that finds a file's location in its own program's directory and returns its contents."
    api_keys_required = ['openai']

    def __init__(self, api_keys: dict):
        super().__init__(api_keys)

    def execute(self, params: str, dependent_task_outputs: dict, objective: dict) -> str:
        if not self.valid:
            return

        directory_structure = self.get_directory_structure(self.get_current_script_directory())
        print(f"Directory structure: {directory_structure}")

        task_prompt = self.generate_task_prompt(directory_structure, params)
        response = self.get_completion(task_prompt)
        file_path = response.choices[0].message['content'].strip()

        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
                print(f"File content:\n{file_content}")
                return file_content
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None

    def get_current_script_directory(self) -> str:
        return os.path.dirname(os.path.realpath(__file__))

    def get_directory_structure(self, start_path: str) -> dict:
        # Unchanged function

    def generate_task_prompt(self, example_dir_structure: dict, params: str) -> str:
        example_params = "Analyze main.py"
        example_response = "main.py"

        task_prompt = f"Find a specific file in a directory and return only the file path, based on the task description below. Always return a directory.###The directory structure is as follows: \n{example_dir_structure}\nYour task: {example_params}\n###\nRESPONSE:{example_response} ###The directory structure is as follows: \n{directory_structure}\nYour task: {params}\n###\nRESPONSE:"

        return task_prompt

    def get_completion(self, prompt: str) -> dict:
        # Unchanged function
