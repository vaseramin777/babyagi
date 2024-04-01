import os
import requests
from urllib.parse import urlparse
from typing import Dict, Any

import openai
from skills.skill import Skill

class ImageGeneration(Skill):
    name = 'image_generation'
    description = "A drawing tool that uses OpenAI's DALL-E API to generate images."
    api_keys_required = ['openai']

    def __init__(self, api_keys: Dict[str, str], main_loop_function):
        super().__init__(api_keys, main_loop_function)

    def download_and_save_image(self, url: str, folder_path: str = "public/static/images") -> str:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error while downloading image: {e}")
            return None

        file_name = os.path.basename(urlparse(url).path)
        file_path = os.path.join(folder_path, file_name)

        try:
            with open(file_path, 'wb') as f:
                f.write(response.content)
        except OSError as e:
            print(f"Error while saving image: {e}")
            return None

        return file_path

    def generate_prompt(self, objective: str) -> str:
        if not objective:
            print("Error: Objective is empty.")
            return None

        prompt_generation_messages = [
            {"role": "system", "content": "You are a helpful assistant specialized in generating creative and descriptive prompts for image generation. Your response is always one sentence with no line breaks. If the input is already detailed, do not change it."},
            {"role": "user", "content": f"Generate a prompt for image creation based on the following objective: {objective}"}
        ]

        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo",
                messages=prompt_generation_messages,
                temperature=0.7,
                max_tokens=100
            )
        except openai.error.OpenAIError as e:
            print(f"Error while generating prompt: {e}")
            return None

        return response.choices[0].text.strip()

    def execute(self, params: dict, dependent_task_outputs: dict, objective: str) -> str:
        if not self.valid:
            return

        print(f"Objective: {objective}")

        generated_prompt = self.generate_prompt(objective)
        print(f"generated_prompt: {generated_prompt}")

        if not generated_prompt:
            return None

        try:
            response = openai.Image.create(
                prompt=generated_prompt,
                n=1,
                size="512x512",
                response_format="url"
            )
        except openai.error.OpenAIError as e:
            print(f"Error while generating image: {e}")
            return None

        image_url = response.data[0]['url']
        print(f"image_url: {image_url}")

        saved_image_path = self.download_and_save_image(image_url)
        print(f"saved_image_path: {saved_image_path}")

        if not saved_image_path:
            return None

        relative_image_path = os.path.relpath(saved_image_path, start="public")
        print(f"relative_image_path: {relative_image_path}")

        html_code = f'<img src="static/images/{os.path.basename(saved_image_path)}" alt="Generated Image">'
        print(f"html_code: {html_code}")

        return html_code
