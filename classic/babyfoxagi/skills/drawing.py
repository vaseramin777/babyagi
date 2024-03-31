from skills.skill import Skill
import openai
from typing import Dict, Any, Optional

class Drawing(Skill):
    name = 'drawing'
    description = "A tool that draws on an HTML canvas using OpenAI."
    api_keys_required = ['openai']

    def __init__(self, api_keys: Dict[str, str], main_loop_function):
        super().__init__(api_keys, main_loop_function)
        self.openai = openai.ChatCompletion(engine="gpt-3.5-turbo-16k", api_key=self.api_keys['openai'])

    def execute(self, params: str, dependent_task_outputs: Optional[Dict[str, Any]] = None, objective: str = "") -> str:
        if not self.valid:
            return

        task_prompt = f"Do a detailed HTML canvas drawing of the user request: {params}. Start with <canvas> and end with </canvas>. Only provide code.:"

        try:
            response = self.openai.create(
                model="gpt-3.5-turbo-16k",
                messages=[{"role": "user", "content": task_prompt}],
                temperature=0.4,
                max_tokens=4000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            content = response['choices'][0]['message']['content'].strip()
            if not content.startswith('<canvas>') or not content.endswith('</canvas>'):
                raise ValueError("Generated HTML must start with <canvas> and
