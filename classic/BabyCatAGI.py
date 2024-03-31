import openai
import time
import requests
from bs4 import BeautifulSoup
from collections import deque
from typing import Dict, List, Optional
import re
import ast
import json
from serpapi import GoogleSearch

class BabyCatAGI:
    """BabyCatAGI class for managing tasks and tools."""

    def __init__(self, objective: str, first_task: str, openai_api_key: str, serpapi_api_key: Optional[str] = None):
        """
        Initialize BabyCatAGI with the given objective, first task, OpenAI API key, and SerpAPI key (optional).

        :param objective: The main objective of the agent.
        :param first_task: The first task to be executed.
        :param openai_api_key: The OpenAI API key.
        :param serpapi_api_key: The SerpAPI key (optional).
        """
        self.objective = objective
        self.first_task = first_task
        openai.api_key = openai_api_key
        self.serpapi_client = GoogleSearch(api_key=serpapi_api_key) if serpapi_api_key else None
        self.websearch_var = "[web-search] " if serpapi_api_key else ""
        self.task_id_counter = 1
        self.session_summary = ""
        self.task_list = []

    def add_task(self, task: Dict):
        """
        Add a task to the task list.

        :param task: The task to be added.
        :return: None
        """
        self.task_list.append(task)

    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """
        Get a task by its ID.

        :param task_id: The ID of the task.
        :return: The task if found, None otherwise.
        """
        return next((task for task in self.task_list if task["id"] == task_id), None)

    def get_completed_tasks(self) -> List[Dict]:
        """
        Get all completed tasks.

        :return: A list of completed tasks.
        """
        return [task for task in self.task_list if task["status"] == "complete"]

    # ... (other tool functions and agent functions)

    def task_creation_agent(self) -> List[Dict]:
        """
        Create tasks based on the objective.

        :return: A list of tasks.
        """
        # ... (task creation agent implementation)

    def main_loop(self):
        """
        Start the main loop for executing tasks.

        :return: None
        """
        # ... (main loop implementation)

def main():
    """
    Initialize BabyCatAGI and start the main loop.

    :return: None
    """
    objective = "Research experts at scaling NextJS and their Twitter accounts."
    first_task = "Develop a task list."
    openai_api_key = "<your_openai_api_key>"
    serpapi_api_key = "<your_serpapi_api_key>"  # If you include SERPAPI KEY, this will enable web-search. If you don't, it will autoatically remove web-search capability.

    baby_cat_agi = BabyCatAGI(objective, first_task, openai_api_key, serpapi_api_key)
    baby_cat_agi.main_loop()

if __name__ == "__main__":
    main()
