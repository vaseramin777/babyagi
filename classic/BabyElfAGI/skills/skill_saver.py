from skills.skill import Skill
import os
import openai

class SkillSaver(Skill):
    name = 'skill_saver'
    description = "A skill that saves code written in a previous step into a file within the skills folder. Not for writing code."
    api_keys_required = []

    def __init__(self, api_keys):
        super().__init__(api_keys)

    def execute(self, params, dependent_task_outputs, objective):
        if not self.valid:
            return

        # Extract the code from the dependent task output
        task_prompt = f"Please extract the code from the following text and return it:\n\n{dependent_task_outputs}\n\n###\nCODE:"
        messages = [
            {"role": "user", "content": task_prompt}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.4,
            max_tokens=3000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        ) 
        code = response.choices[0].message['content'].strip()

        # Generate a file name for the code
        task_prompt = f"Please generate a file name for the following Python code:\n\n{code}\n\n###\nFILE_NAME:"
        messages = [
            {"role": "user", "content": task_prompt}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.4,
            max_tokens=3000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        ) 
        file_name = response.choices[0].message['content'].strip()

        # Ensure the file name has a .py extension
        if not file_name.endswith('.py'):
            file_name += '.py'

        # Construct the file path
        file_path = os.path.join('skills', file_name)

        # Save the code to a file
        try:
            if not os.path.exists('skills'):
                os.makedirs('skills')
            with open(file_path, 'w') as file:
                file.write(code)
                print(f"Code saved successfully: {file_name}")
        except Exception as e:
            print(f"Error saving code: {str
