import os
import sys
from dotenv import load_dotenv
import importlib.util
import json
import openai
import concurrent.futures
import time
from datetime import datetime
from skills.skill import Skill
from skills.skill_registry import SkillRegistry
from tasks.task_registry import TaskRegistry

load_dotenv()  # Load environment variables from .env file

# Retrieve all API keys
api_keys = {
    "openai": os.environ.get("OPENAI_API_KEY"),
    "serpapi": os.environ.get("SERPAPI_API_KEY"),
    # Add more keys here as needed
}

if not all(api_key for api_key in api_keys.values()):
    print("Missing API keys. Please set the required environment variables.")
    sys.exit(1)

# Check for required packages
required_packages = ["openai", "dotenv", "concurrent.futures", "json", "datetime"]
installed_packages = {pkg.split(".")[0] for pkg in importlib.util.find_spec("sys").submodule_search_locations()}
missing_packages = set(required_packages) - installed_packages
if missing_packages:
    print(f"Missing required packages: {missing_packages}")
    sys.exit(1)

# Set objective and load skills
OBJECTIVE = "Create an example objective and tasklist for 'write a poem', which only uses text_completion in the tasks. Do this by using code_reader to read example1.json, then writing the JSON objective tasklist pair using text_completion, and saving it using objective_saver."
LOAD_SKILLS = ["text_completion", "code_reader", "objective_saver"]


def main():
    # Initialize the SkillRegistry and TaskRegistry
    skill_registry = SkillRegistry(api_keys=api_keys, skill_names=LOAD_SKILLS)
    skill_descriptions = ", ".join(f"[{skill.name}: {skill.description}]" for skill in skill_registry.skills.values())
    task_registry = TaskRegistry()

    # Create the initial task list based on an objective
    task_registry.create_tasklist(OBJECTIVE, skill_descriptions)

    # Initialize task outputs
    task_outputs = {i: {"completed": False, "output": None} for i, _ in enumerate(task_registry.get_tasks())}

    # Create a thread pool for parallel execution
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while not all(task["completed"] for task in task_outputs.values()):
            # Get the tasks that are ready to be executed (i.e., all their dependencies have been completed)
            tasks = task_registry.get_tasks()

            # Print the updated task list
            task_registry.print_tasklist(tasks)

            # Update task_outputs to include new tasks
            for task in tasks:
                if task["id"] not in task_outputs:
                    task_outputs[task["id"]] = {"completed": False, "output": None}

            ready_tasks = [(task["id"], task) for task in tasks
                           if all((dep in task_outputs and task_outputs[dep]["completed"]) 
                                  for dep in task.get('dependent_task_ids', [])) 
                           and not task_outputs[task["id"]]["completed"]]

            for task_id, task in ready_tasks:
                try:
                    output = executor.submit(task_registry.execute_task, task_id, task, skill_registry, task_outputs, OBJECTIVE).result()
                except Exception as e:
                    print(f"Error executing task {task_id}: {e}")
                    continue

                task_outputs[task_id]["output"] = output
                task_outputs[task_id]["completed"] = True

                # Update the task in the TaskRegistry
                task_registry.update_tasks({"id": task_id, "status": "completed", "result": output})

                completed_task = task_registry.get_task(task_id)
                print(f"Task {task_id}: {completed_task['task']} [COMPLETED] [{completed_task['skill']}]")

                # Reflect on the output
                if output:
                    task_registry.reflect_on_output(output, skill_descriptions)

            if all(task["status"] == "completed" for task in task_registry.tasks):
                print("All tasks completed!")
                break

            # Short delay to prevent busy looping
            time.sleep(0.1)

        # Print session summary
        print("\n*****SAVING FILE...*****\n")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_name = f'output_{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.txt'
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, 'w') as file:
            file.write(session_summary)
        print(f"...file saved as {file_name}")
        print("END")


if __name__ == "__main__":
    session_summary = ""
    main()
