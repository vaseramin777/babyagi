###### This is a modified version of OG BabyAGI, called BabyDeerAGI (modifications will follow the pattern "Baby<animal>AGI").######
######IMPORTANT NOTE: I'm sharing this as a framework to build on top of (with lots of room for improvement), to facilitate discussion around how to improve these. This is NOT for people who are looking for a complete solution that's ready to use. ######

import openai
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from collections import deque
from typing import Dict, List
import re
import ast
import json
from serpapi import GoogleSearch
from concurrent.futures import ThreadPoolExecutor
import time

# Configure OpenAI and SerpAPI client
OPENAI_API_KEY = "your_openai_api_key"
SERPAPI_API_KEY = "your_serpapi_api_key"
openai.api_key = OPENAI_API_KEY
serpapi_client = GoogleSearch({"api_key": SERPAPI_API_KEY})

class Task:
    def __init__(self, id: int, task: str, tool: str, dependent_task_ids: List[int], status: str = "incomplete"):
        self.id = id
        self.task = task
        self.tool = tool
        self.dependent_task_ids = dependent_task_ids
        self.status = status
        self.output = None

def get_task_by_id(task_list: List[Task], task_id: int):
    for task in task_list:
        if task.id == task_id:
            return task
    return None

def print_tasklist(task_list: List[Task]):
    print("\033[95m\033[1m" + "*****TASK LIST*****\n" + "\033[0m")
    for t in task_list:
        dependent_task = ""
        if t.dependent_task_ids:
            dependent_task = f"\033[31m<dependencies: {', '.join([f'#{dep_id}' for dep_id in t.dependent_task_ids])}>\033[0m"
        status_color = "\033[32m" if t.status == "complete" else "\033[31m"
        print(f"\033[1m{t.id}\033[0m: {t.task} {status_color}[{t.status}]\033[0m \033[93m[{t.tool}] {dependent_task}\033[0m")

def text_completion_tool(prompt: str):
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.2,
        max_tokens=1500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message['content'].strip()

def user_input_tool(prompt: str):
    val = input(f"\n{prompt}\nYour response: ")
    return str(val)

def web_search_tool(query: str, dependent_tasks_output: str):
    if dependent_tasks_output:
        dependent_task = f"Use the dependent task output below as reference to help craft the correct search query for the provided task above. Dependent task output:{dependent_tasks_output}."
    else:
        dependent_task = "."
    query = text_completion_tool("You are an AI assistant tasked with generating a Google search query based on the following task: " + query + ". If the task looks like a search query, return the identical search query as your response. " + dependent_task + "\nSearch Query:")
    search_params = {
        "engine": "google",
        "q": query,
        "num": 3
    }
    search_results = serpapi_client.get_json(search_params)
    search_results = search_results.get("organic_results", [])
    return search_results

def simplify_search_results(search_results):
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

def web_scrape_tool(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(strip=True)
        return text
    else:
        return None

def extract_relevant_info(objective: str, text: str, task: str):
    messages = [
        {"role": "system", "content": f"You are an AI assistant."},
        {"role": "user", "content": f"You are an expert AI research assistant tasked with creating or updating the current notes. If the current note is empty, start a current-notes section by exracting relevant data to the task and objective from the text to analyze. If there is a current note, add new relevant info from the text to analyze. Make sure the new or combined notes is comprehensive and well written. Here's the current text to analyze: {text}. ### Here is the current task: {task}.### For context, here is the objective: {objective}."}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=800,
        n=1,
        stop="###",
        temperature=0.7,
    )

    return response
