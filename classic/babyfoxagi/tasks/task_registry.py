import openai
import json
import threading
import os
import numpy as np
from datetime import datetime
from collections import defaultdict

class TaskRegistry:
    def __init__(self, objectives_file_path):
        self.tasks = []
        self.lock = threading.Lock()
        self.objectives_loader = ExampleObjectivesLoader(objectives_file_path)

    def load_example_objectives(self, user_objective):
        return self.objectives_loader.load_example_objectives(user_objective)

    def create_tasklist(self, objective, skill_descriptions):
        notes = self.reflect_on_objective(objective, skill_descriptions)
        example_objective, example_tasklist, example_reflection = self.load_example_objectives(objective)

        prompt = self._generate_prompt(objective, skill_descriptions, notes, example_objective, example_tasklist)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0,
            max_tokens=2500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        result = response["choices"][0]["message"]["content"]
        try:
            task_list = json.loads(result)
            self.tasks = task_list
        except Exception as error:
            print(error)

    def reflect_on_objective(self, objective, skill_descriptions):
        example_objective, _, _ = self.load_example_objectives(objective)
        prompt = self._generate_reflection_prompt(objective, skill_descriptions, example_objective)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0,
            max_tokens=250,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        result = response["choices"][0]["message"]["content"]
        return result

    def _generate_prompt(self, objective, skill_descriptions, notes, example_objective, example_tasklist):
        return f"You are an expert task list creation AI. Consider the objective: {objective}, available skills: {skill_descriptions}, notes: {notes}, example objective: {json.dumps(example_objective)}, and example task list: {json.dumps(example_tasklist)}. Generate a task list as a JSON array."

    def _generate_reflection_prompt(self, objective, skill_descriptions, example_objective):
        return f"You are an AI specializing in generating helpful thoughts and ideas on tackling an objective. Consider the objective: {objective}, available skills: {skill_descriptions}, and example objective: {json.dumps(example_objective)}. Generate helpful notes for a task creation AI."

# ... (rest of the code remains the same)

class ExampleObjectivesLoader:
    # ... (rest of the code remains the same)
