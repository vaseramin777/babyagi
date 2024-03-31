from skills.skill import Skill
import openai

class CallBabyagi(Skill):
    name = 'call_babyagi'
    description = 'A skill that rewrites a task description into an objective, and sends it to itself (an autonomous agent) to complete. Helpful for research.'
    api_keys_required = [['openai']]

    def __init__(self, api_keys, main_loop_function):
        super().__init__(api_keys, main_loop_function)
        if 'openai' not in self.api_keys:
            raise ValueError("The 'openai' API key is required for the 'call_babyagi' skill.")
        self.main_loop_function = main_loop_function

    def execute(self, params, dependent_task_outputs, objective):
        try:
            # Generate the new objective by rewriting the task description
            new_objective = self.generate_new_objective(objective)

            # Send the new objective to the main loop
            load_skills = ['web_search','text_completion']
            result = self.main_loop_function(new_objective, load_skills)

            # Return the main loop's output as the result of the skill
            return result

        except Exception as e:
            self.log_error(str(e))
            return {'status': 'error', 'message': str(e)}

    def generate_new_objective(self, task_description):
        prompt = f"You are an AI assistant tasked with rewriting the following task description into an objective, and remove any mention of call_babyagi: {task_description}\nObjective:"

        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0.2,
                max_tokens=1500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            return response.choices[0].text.strip()

        except openai.OpenAIError as e:
            self.log_error(str(e))
            return {'status': 'error', 'message': str(e)}
