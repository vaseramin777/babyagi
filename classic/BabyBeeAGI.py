###### This is a modified version of OG BabyAGI, called BabyBeeAGI (future modifications will follow the pattern "Baby<animal>AGI"). This version requires GPT-4, it's very slow, and often errors out.######
######IMPORTANT NOTE: I'm sharing this as a framework to build on top of (with lots of errors for improvement), to facilitate discussion around how to improve these. This is NOT for people who are looking for a complete solution that's ready to use. ######

import openai
import pinecone
import time
import requests
from bs4 import BeautifulSoup
from collections import deque
from typing import Dict, List
import re
import ast
import json
from serpapi import GoogleSearch

### SET THESE 4 VARIABLES ##############################

# Add your API keys here
OPENAI_API_KEY = "your_openai_api_key"
SERPAPI_API_KEY = "your_serpapi_api_key"  # If you include SERPAPI KEY, this will enable web-search. If you don't, it will automatically remove web-search capability.

# Set variables
OBJECTIVE = "You are an AI. Make the world a better place."
YOUR_FIRST_TASK = "Develop a task list."

### UP TO HERE ##############################

# Configure OpenAI and SerpAPI client
openai.api_key = OPENAI_API_KEY
if SERPAPI_API_KEY:
    serpapi_client = GoogleSearch({"api_key": SERPAPI_API_KEY})
    websearch_var = "[web-search] "
else:
    websearch_var = ""

# Initialize task list
task_list = []

# Initialize session_summary
session_summary = ""

### Task list functions ##############################
def add_task(task: Dict):
    task_list.append(task)

def get_task_by_id(task_id: int):
    for task in task_list:
        if task["id"] == task_id:
            return task
    return None

def get_completed_tasks():
    return [task for task in task_list if task["status"] == "complete"]

### Tool functions ##############################
def text_completion_tool(prompt: str):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=1500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()

def web_search_tool(query: str):
    search_params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num":3
    }
    search_results = GoogleSearch(search_params)
    results = search_results.get_dict()

    return str(results["organic_results"])

def web_scrape_tool(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    result = soup.get_text(strip=True)+"URLs: "
    for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
      result+= link.get('href')+", "
    return result

### Agent functions ##############################
def execute_task(task, task_list, OBJECTIVE):
    global task_id_counter
    # Check if dependent_task_id is complete
    if task["dependent_task_id"]:
        dependent_task = get_task_by_id(task["dependent_task_id"])
        if not dependent_task or dependent_task["status"] != "complete":
            return

    # Execute task
    print("\033[92m\033[1m"+"\n*****NEXT TASK*****\n"+"\033[0m\033[0m")
    print(str(task['id'])+": "+str(task['task'])+" ["+str(task['tool']+"]"))
    task_prompt = f"Complete your assigned task based on the objective: {OBJECTIVE}. Your task: {task['task']}"
    if task["dependent_task_id"]:
        dependent_task_result = dependent_task["result"]
        task_prompt += f"\nThe previous task ({dependent_task['id']}. {dependent_task['task']}) result: {dependent_task_result}"

    task_prompt += "\nResponse:"
    ##print("###task_prompt: "+task_prompt)
    if task["tool"] == "text-completion":
        result = text_completion_tool(task_prompt)
    elif task["tool"] == "web-search":
        result = web_search_tool(task_prompt)
    elif task["tool"] == "web-scrape":
        result = web_scrape_tool(task['task'])
    else:
        result = "Unknown tool"

    print("\033[93m\033[1m"+"\033[1m*****TASK RESULT*****\n"+"\033[0m\033[0m")
    print_result = result[0:2000]
    if result != result[0:2000]:
      print(print_result+"...")
    else:
      print(result)
    # Update task status and result
    task["status"] = "complete"
    task["result"] = result
    task["result_summary"] = summarizer_agent(result)

    # Update session_summary
    session_summary = overview_agent(task["id"])

    # Increment task_id_counter
    task_id_counter += 1

    # Update task_manager_agent of tasks
    task_manager_agent(
        OBJECTIVE,
        result,
       
