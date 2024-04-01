from flask import Flask, render_template, request, jsonify, send_from_directory
import openai
import os
import json
import threading
from babyagi import get_skills, execute_skill, execute_task_list, api_keys, LOAD_SKILLS
from ongoing_tasks import ongoing_tasks

app = Flask(__name__, static_folder='public/static')
openai.api_key = os.getenv('OPENAI_API_KEY')

FILES = {
    "forever_cache": "forever_cache.ndjson",
    "overall_summary": "overall_summary.ndjson",
    "ongoing_tasks": "ongoing_tasks.py"
}

def get_messages(file_name):
    messages = []
    with open(file_name, "r") as file:
        for line in file:
            messages.append(json.loads(line))
    return messages

def append_to_file(file_name, data):
    try:
        with open(file_name, 'a') as file:
            file.write(json.dumps(data) + '\n')
    except Exception as e:
        print(f"Error in append_to_file: {str(e)}")

def update_summary(messages):
    messages_text = " ".join([msg['content'] for msg in messages])
    latest_summary = summarize_text(messages_text)

    overall = get_latest_summary()
    combined_summary = combine_summaries(overall, latest_summary)
    append_to_ndjson(FILES["overall_summary"], {"summary": combined_summary})

def get_latest_summary():
    try:
        with open(FILES["overall_summary"], 'r') as file:
            lines = file.readlines()
        if lines:
            return json.loads(lines[-1])["summary"]
    except:
        return ""

def summarize_text(text):
    system_message = (
        "Your task is to generate a concise summary for the provided conversation, this will be fed to a separate AI call as context to generate responses for future user queries."
        " The conversation contains various messages that have been exchanged between participants."
        " Please ensure your summary captures the main points and context of the conversation without being too verbose."
        " The summary should be limited to a maximum of 500 tokens."
        " Here's the conversation you need to summarize:")

    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                            messages=[{
                                              "role": "system",
                                              "content": system_message
                                            }, {
                                              "role": "user",
                                              "content": text
                                            }])

    return completion.choices[0]['message']['content'].strip()

def combine_summaries(overall, latest):
    system_message = (
        "Your task is to generate a concise summary for the provided conversation, this will be fed to a separate AI call as context to generate responses for future user queries."
        "You will do this by combining two given summaries into one cohesive summary."
        " Make sure to retain the key points from both summaries and create a concise, unified summary."
        " The combined summary should not exceed 500 tokens."
        " Here are the summaries you need to combine:")

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{
            "role": "system",
            "content": system_message
        }, {
            "role":
            "user",
            "content":
            f"Overall summary: {overall}\nLatest summary: {latest}"
        }])

    return completion.choices[0]['message']['content'].strip()

def openai_function_call(user_message):
    global ongoing_tasks
    global global_skill_registry
    global_skill_registry = LOAD_SKILLS

    user_entry = {"role": "user", "content": user_message}
    append_to_ndjson(FILES["forever_cache"], user_entry)

    last_20_messages = get_messages(FILES["forever_cache"])[-20:]

    threading.Thread(target=update_summary, args=(last_20_messages, )).start()

    overall_summary = get_latest_summary()

    system_message = (
        f"You are a fun happy and quirky AI chat assistant that uses Gen Z language and lots of emojis named BabyAGI with capabilities beyond chat. For every user message, you quickly analyze whether this is a request that you can simply respond via ChatCompletion, whether you need to use one of the skills provided, or whether you should create a task list and chain multiple skills together. You will always provide a message_to_user. If path is Skill or TaskList, always generate an objective. If path is Skill, ALWAYS include skill_used from one of the available skills. ###Here are your available skills: {global_skill_registry}.###For context, here is the overall summary of the chat: {overall_summary}."
    )

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system","content": system_message},
            *last_20_messages,
            {"role": "user","content": user_message},
        ],
        functions=[{
            "name": "determine_response_type",
            "description":
            "Determine whether to respond via ChatCompletion, use a skill, or create a task list. Always provide a message_to_user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_to_user": {
                        "type":
                        "string",
                        "description":
                        "A
