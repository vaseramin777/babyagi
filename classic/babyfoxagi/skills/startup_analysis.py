from skills.skill import Skill
import openai
import json
from typing import Dict

class StartupAnalysis(Skill):
    name = 'startup_analysis'
    description = "A tool specialized in providing a detailed analysis of startups using OpenAI's text completion API. Analyzes parameters like customers, ICP, pain points, competitors, etc."
    api_keys_required = ['openai']

    def __init__(self, api_keys, main_loop_function):
        super().__init__(api_keys, main_loop_function)

    def execute(self, params: Dict, dependent_task_outputs, objective):
        if not self.valid:
            return

        if 'openai' not in self.api_keys or not self.api_keys['openai']:
            return "Missing or invalid OpenAI API key"

        openai.api_key = self.api_keys['openai']

        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=self.generate_prompt(params),
            functions=[
                {
                    "name": "analyze_startup",
                    "description": "Analyze the startup based on various parameters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customers": {
                                "type": "string",
                                "description": "Who are the startup's primary customers. Describe in detail in the third person."
                            },
                            # ... other properties
                        },
                        "required": [
                            "customers", "ICP", "pain_points", "alternate_solutions",
                            "competitors", "potential_partners", "key_incumbents",
                            "history_of_innovation", "key_risks", "legal_considerations",
                            "important_figures", "recent_trends"
                        ],
                    },
                },
            ],
            function_call={"name": "analyze_startup"}
        )

        if 'function_call' not in completion or not completion['function_call']:
            return "No function call in the completion response"

        response_data = completion['function_call']['arguments']
        html_content = self.format_response_data(response_data)

        return html_content

    def generate_prompt(self, params: Dict):
        return f"""You are a great AI analyst specialized in writing VC investment memos. Write one paragraph each in the third person on customers, ICP, pain points, alternate solutions, competitors, potential partners, key incumbents, history of innovation in the industry, key risks, legal considerations, important figures or influencers, and other recent trends in the space. The user will provide a detailed description of their startup: {json.dumps(params)}"""

    def format_response_data(self, response_data: Dict):
        html_content = ""
        for key, value in response_data.items():
            html_content += f"<strong>{key.capitalize()}</strong>: {value}</br>\n"
        return html_content
