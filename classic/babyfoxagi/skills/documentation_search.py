import requests
from bs4 import BeautifulSoup
import re
from serpapi import GoogleSearch
import openai

class DocumentationSearch:
    def __init__(self, serpapi_api_key, openai_api_key):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }
        self.serpapi_api_key = serpapi_api_key
        self.openai_api_key = openai_api_key

    def text_completion_tool(self, prompt: str):
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=0.2,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message['content'].strip()

    def simplify_search_results(self, search_results):
        simplified_results = []
        for result in search_results:
            simplified_result = {
                "position": result.get("position"),
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet")
            }
            simplified_results.append(simplified_result)
        return simplified_results

    def fetch_url_content(self, url: str):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching the URL: {e}")
            return ""

    def extract_links(self, content: str):
        soup = BeautifulSoup(content, "html.parser")
        links = [link.get('href') for link in soup.findAll('a', attrs={'href': re.compile("^https?://")})]
        return links

    def extract_text(self, content: str):
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(strip=True)
        return text

    def extract_relevant_info(self, objective, large_string, task):
        chunk_size = 12000
        overlap = 500
        notes = ""

        if len(large_string) == 0:
            return "Error scraping."

        for i in range(0, len(large_string), chunk_size - overlap):
            chunk = large_string[i:i + chunk_size]
            messages = [
                {"role": "system", "content": f"You are an AI assistant."},
                {"role": "user", "content": f"You are an expert AI research assistant tasked with creating or updating the current notes. If the current note is empty, start a current-notes section by extracting relevant data to the task and objective from the chunk of text to analyze. Any chance you get, make sure to capture working or good example code examples. If there is a current note, add new relevant info from the chunk of text to analyze. Make sure the new or combined notes is comprehensive and well written. Here's the current chunk of text to analyze: {chunk}. ### Here is the current task: {task}.### For context, here is the objective: {objective}.### Here is the data we've extracted so far that you need to update: {notes}.### new-or-updated-note:"}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k-0613",
                messages=messages,
                max_tokens=1500,
                n=1,
                stop="###",
                temperature=0.7,
            )

            notes += response.choices[0].message['content'].strip() + ". "
        
        return notes

    def search(self, query, params, objective):
        search_params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_api_key,
            "num": 3
        }
        search_results = GoogleSearch(search_params).get_dict()
        search_results = self.simplify_search_results(search_results.get('organic_results', []))

        results = ""
        for result in search_results:
            url = result.get('link')
            content = self.fetch_url_content(url)
            if content:
                text = self.extract_text(content)
                info = self.extract_relevant_info(objective, text, params)
                results += f"URL: {url}\nCONTENT: {info}\n\n"

        return results

if __name__ == "__main__":
    # Initialize the DocumentationSearch class with your SerpApi and OpenAI API keys
    documentation_search = DocumentationSearch("your_serpapi_api_key", "your_openai_api_key")

    # Perform a search
    query = "example query"
    params = "example params"
    objective = "example objective"
    results = documentation_search.search(query, params, objective)
    print(results)
