import openai
import pinecone
import time
from collections import deque
from typing import Dict, List

OPENAI_API_KEY = "your_openai_api_key"
PINECONE_API_KEY = "your_pinecone_api_key"
PINECONE_ENVIRONMENT = "us-east1-gcp"
YOUR_TABLE_NAME = "test-table"
OBJECTIVE = "Solve world hunger."
YOUR_FIRST_TASK = "Develop a task list."

def set_api_keys():
    global OPENAI_API_KEY, PINECONE_API_KEY
    OPENAI_API_KEY = "your_openai_api_key"
    PINECONE_API_KEY = "your_pinecone_api_key"

def set_variables():
    global YOUR_TABLE_NAME, OBJECTIVE, YOUR_FIRST_TASK
    YOUR_TABLE_NAME = "test-table"
    OBJECTIVE = "Solve world hunger."
    YOUR_FIRST_TASK = "Develop a task list."

def print_objective():
    print("\033[96m\033[1m"+"\n*****OBJECTIVE*****\n"+"\033[0m\033[0m")
    print(OBJECTIVE)

def configure_openai_and_pinecone():
    openai.api_key = OPENAI_API_KEY
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

def create_pinecone_index():
    dimension = 1536
    metric = "cosine"
    pod_type = "p1"
    table_name = YOUR_TABLE_NAME
    if table_name not in pinecone.list_indexes():
        pinecone.create_index(table_name, dimension=dimension, metric=metric, pod_type=pod_type)
    index = pinecone.Index(table_name)
    return index

def task_creation_agent(objective: str, result: Dict, task_description: str, task_list: List[str]):
    prompt = f"You are an task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}, The last completed task has the result: {result}. This result was based on this task description: {task_description}. These are incomplete tasks: {', '.join(task_list)}. Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks. Return the tasks as an array."
    response = openai.Completion.create(engine="text-davinci-003",prompt=prompt,temperature=0.5,max_tokens=100,top_p=1,frequency_penalty=0,presence_penalty=0)
    new_tasks = response.choices[0].text.strip().split('\n')
    return [{"task_name": task_name} for task_name in new_tasks]

def prioritization_agent(this_task_id:int, task_list: List[Dict]):
    global task_list as task_queue
    task_names = [t["task_name"] for t in task_list]
    next_task_id = int(this_task_id)+1
    prompt = f"""You are an task prioritization AI tasked with cleaning the formatting of and reprioritizing the following tasks: {task_names}. Consider the ultimate objective of your team:{OBJECTIVE}. Do not remove any tasks. Return the result as a numbered list, like:
    #. First task
    #. Second task
    Start the task list with number {next_task_id}."""
    response = openai.Completion.create(engine="text-davinci-003",prompt=prompt,temperature=0.5,max_tokens=1000,top_p=1,frequency_penalty=0,presence_penalty=0)
    new_tasks = response.choices[0].text.strip().split('\n')
    task_list = []
    for task_string in new_tasks:
        task_parts = task_string.strip().split(".", 1)
        if len(task_parts) == 2:
            task_id = task_parts[0].strip()
            task_name = task_parts[1].strip()
            task_list.append({"task_id": task_id, "task_name": task_name})
    return task_list

def execution_agent(objective:str,task: str) -> str:
    context=context_agent(index=YOUR_TABLE_NAME, query=objective, n=5)
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"You are an AI who performs one task based on the following objective: {objective}. Your task: {task}\nResponse:",
        temperature=0.7,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()

def context_agent(query: str, index: str, n: int):
    query_embedding = get_ada_embedding(query)
    index = pinecone.Index(index_name=index)
    results = index.query(query_embedding, top_k=n,
    include_metadata=True)
    sorted_results = sorted(results.matches, key=lambda x: x.score, reverse=True)
    return [(str(item.metadata['task'])) for item in sorted_results]

def get_ada_embedding(text):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model="text-embedding-ada-002")["data"][0]["embedding"]

def add
