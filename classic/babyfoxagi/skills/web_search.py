import time
from typing import Dict, List, Union

import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import openai

class WebSearch:
    """A tool that performs web searches."""

    def __init__(self, api_keys: Dict[str, str], main_loop_function):
        self.api_keys = api_keys
        self.main_loop_function = main_loop_function
        self.openai_api_key = api_keys["openai"]
        self.serpapi_api_key = api_keys["serpapi"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }

    def text_completion_tool(self, prompt: str) -> str:
        """Generate a text completion using the OpenAI API."""
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=0,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message["content"].strip()

    def simplify_search_results(self, search_results: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int]]]:
        """Simplify the search results."""
        simplified_results = []
        for result in search_results:
            simplified_result = {
                "position": result.get("position"),
                "title": result.get("title"),
                "link": result.get("link"),
              
