import openai
import logging
from skills.skill import Skill
import os

class PrettyMe(Skill):
    name = 'pretty_me'
    description = "A tool to update the current website UI by generating JavaScript that will execute upon load to change the front-end interface of the website it's on. The code response will be directly wrapped in a window.onload function and executed on the front-end. Use for any requests related to updating the UI (background, theme, etc.)"
    api_keys_required = ['openai']

    def __init__(self, api_keys, main_loop_function):
        super().__init__(api_keys, main_loop_function)

    def execute(self, params, dependent_task_outputs, objective):
        try:
            if not self.valid:
                return "API keys not configured properly."

            css_path = os.path.join("public", "static", "style.css")
            html_path = os.path.join("templates", "index.html")

            with open(css_path, 'r') as css_file, open(html_path, 'r') as html_file:
                css_content = css_file.read()
                html_content = html_file.read()

            task_prompt = f"Generate JavaScript code to execute based on the following user input: {objective} {params}\nCSS Content: {css_content}\nHTML Content: {html_content}\nInstructions: only provide Javascript code that would go between the script tags, but do not provide the script tags.\n### Code:"

            messages = [
                {"role": "system", "content": "You are a helpful assistant that generates JavaScript code to update the UI of a website."},
                {"role": "user", "content": f"{params}\n{objective}\nCSS Content: {css_content}\nHTML Content: {html_content}\nInstructions: only provide Javascript code that would go between the script tags, but do not provide the script tags."},
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=messages,
                temperature=0,
                max_tokens=4000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            generated_code = response.choices[0].message['content'].strip()

            wrapped_code = f'''
            <script>
                var script = document.createElement("script");
                script.type = "text/javascript";
                script.innerHTML = `{generated_code}`;
                document.head.appendChild(script);
            </script>
            '''
            return "\n\n" + wrapped_code
        except Exception as exc:
            logging.error(f"Error in PrettyMe skill: {exc}")
            return "An error occurred while processing your request."
