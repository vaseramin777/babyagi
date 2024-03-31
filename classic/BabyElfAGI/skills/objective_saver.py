from skills.skill import Skill
import os
import openai

class ObjectiveSaver(Skill):
    """
    A skill that saves a new example_objective based on the concepts from skill_saver.py
    """
    name = 'objective_saver'
    description = "A skill that saves a new example_objective based on the concepts from skill_saver.py"
    api_keys_required = []

    def __init__(self, api_keys: dict):
        super().__init__(api_keys)
        self.validate_api_keys()

    def validate_api_keys(self):
        """
        Validates that the required API keys are present in the `api_keys` dictionary
        """
        if not self.api_keys or 'openai' not in self.api_keys:
            raise ValueError("The 'openai' API key is required for this class")

    def execute(self, params: dict, dependent_task_outputs: list, objective: str) -> None:
        """
        Saves a new example_objective based on the concepts from skill_saver.py

        :param params: A dictionary of parameters
        :param dependent_task_outputs: A list of outputs from dependent tasks
        :param objective: The objective to save
        :return: None
        """
        if not self.valid:
            return

        if not params or not dependent_task_outputs or not objective:
            raise ValueError("The 'params', 'dependent_task_outputs', and 'objective' parameters are required")

        code = dependent_task_outputs[2]
        task_prompt = f"Come up with a file name (eg. 'research_shoes.json') for the following objective:{code}\n###\nFILE_NAME:"

        messages = [
            {"role": "user", "content": task_prompt}
        ]

        try:
            response
