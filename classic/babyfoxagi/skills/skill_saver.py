from skills.skill import Skill
import os
import openai

class SkillSaver(Skill):
    name = 'skill_saver'
    description = "A skill that saves code written in a previous step into a file within the skills folder. Not for writing code."
    api_keys_required = []

    def __init__(self, api_keys, main_loop_function):
        super().__init__(api_keys, main_loop_function)

    def execute(self, params, dependent_task_outputs, objective):
        if not self.valid:
            return

        task_prompt = f"Extract the code and only the code from the dependent task output here: {dependent_task_outputs}  \n###\nCODE:"

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
