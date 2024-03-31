import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
from urllib.parse import urljoin

import openai
from serpapi import GoogleSearch
from skills.skill import Skill

class WebSearch(Skill):
    name = 'web_search'
    description = 'A tool that performs web searches.'
    api_keys_required = [['openai'], ['serpapi']]

    def __init__(self, api_keys):
        super().__init__(api_keys)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }

    def execute(self, params, dependent_task_outputs, objective):
        query = self._generate_query(params, dependent_task_outputs)
        search_results = self._search(query)
        scraped_results = self._scrape_results(search_results)
        report = self._generate_report(scraped_results, objective)
        return report

    def _generate_query(self, params: str, dependent_task_outputs: str) -> str:
        prompt = f"Generate a Google search query based on the following task: {params}. If the task looks like a search query, return the identical search query as your response. Use the dependent task output below as reference to help craft the correct search query: {dependent_task_outputs}."
        return self._get_openai_response(prompt)

    def _search(self, query: str) -> Dict:
        search_params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_api_key,
            "num": 3
        }
        search_results = GoogleSearch(search_params).get_dict()
        return search_results.get('organic_results', [])

    def _scrape_results(self, search_results: List[Dict]) -> List[str]:
        scraped_results = [self._scrape_result(result) for result in search_results]
        return scraped_results

    def _scrape_result(self, result: Dict) -> str:
        url = result.get('link')
        content = self._fetch_url_content(url)
        if content is None:
            return ""
        text = self._extract_text(content)
        info = self._extract_relevant_info(text, result.get('title'))
        return info

    def _fetch_url_content(self, url: str) -> bytes:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching the URL: {e}")
            return None

    def _extract_text(self, content: bytes) -> str:
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(strip=True)
        return text

    def _extract_relevant_info(self, text: str, title: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are an expert AI research assistant."
            },
            {
                "role": "user",
                "content": f"Extract relevant information from the following text, and create a summary based on the title provided. Title: {title}\n\nText: {text}"
            }
        ]
        response = self._get_openai_response("".join([f"{message['role']}: {message['content']}" for message in messages]))
        return response

    def _generate_report(self, scraped_results: List[str], objective: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are an expert analyst combining the results of multiple web scrapes."
            },
            {
                "role": "user",
                "content": f"Generate a cohesive report based on the following web scrapes. Ignore any reports of not having information, unless all reports say so - in which case explain that the search did not work and suggest other web search queries to try. Objective: {objective}\n\nScraped Results:\n{',\n'.join(scraped_results)}"
            }
        ]
        response = self._get_openai_response("".join([f"{message['role']}: {message['content']}" for message in messages]))
        return response

    def _get_openai_response(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message['content'].strip()
