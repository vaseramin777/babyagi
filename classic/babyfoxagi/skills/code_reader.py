import os
import openai

class CodeReader:
    def __init__(self, api_keys, main_loop_function):
        self.api_keys = api_keys
        self.main_loop_function = main_loop_function
        self.valid = True

    @property
    def openai_api_key(self):
        return self.api_keys.get('openai')

    def execute(self, params, dependent_task_outputs, objective):
        if not self.valid or not self.openai_api_key:
            return {'error': 'Invalid configuration.'}

        dir_structure = self.get_directory_structure(self.get_top_parent_path(os.path.realpath(__file__)))
        print(f"Directory structure: {dir_structure}")

        task_prompt = self.generate_task_prompt(dir_structure, params)
        response = self.get_openai_response(task_prompt)

        file_path = response.strip()
        print(f"AI suggested file path: {file_path}")

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                file_content = file.read()
                if file_content:
                    return {'file_content': file_content}
                else:
                    return {'error': 'The file is empty.'}
        else:
            return {'error': 'File not found. Please check the AI\'s suggested file path.'}

    def generate_task_prompt(self, dir_structure, user_input):
        example_params = "Analyze main.py"
        example_response = "main.py"

        task_prompt = (
            f"Find a specific file in a directory and return only the file path, based on the task description below. "
            f"Always return a directory.\n\nDirectory structure: \n{dir_structure}\n\nYour task: {example_params}\n\nRESPONSE: {example_response}\n\nDirectory structure: \n{dir_structure}\n\nYour task: {user_input}\n\nRESPONSE:"
        )
        return task_prompt

    def get_openai_response(self, prompt):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response.choices[0].message['content']

    def get_directory_structure(self, start_path):
        # Unchanged from the original code
        ...

    def get_top_parent_path(self, current_path):
        # Unchanged from the original code
        ...
