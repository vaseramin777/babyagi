import openai
import json
import threading
import os
import numpy as np

class TaskRegistry:
    def __init__(self):
        self.tasks = []
        self.lock = threading.Lock()
        self.objectives_folder_path = "tasks/example_objectives"
        self.example_loader = ExampleObjectivesLoader(self.objectives_folder_path)

    def load_example_objectives(self, user_objective):
        return self.example_loader.load_example_objectives(user_objective)

    def create_tasklist(self, objective, skill_descriptions):
        example_objective, example_tasklist = self.load_example_objectives(objective)

        prompt = (
            f"You are an expert task list creation AI tasked with creating a  list of tasks as a JSON array, considering the ultimate objective of your team: {objective}. "
            f"Create a very short task list based on the objective, the final output of the last task will be provided back to the user. Limit tasks types to those that can be completed with the available skills listed below. Task description should be detailed.###"
            f"AVAILABLE SKILLS: {skill_descriptions}.###"
            f"RULES:"
            f"Do not use skills that are not listed."
            f"Always include one skill."
            f"dependent_task_ids should always be an empty array, or an array of numbers representing the task ID it should pull results from."
            f"Make sure all task IDs are in chronological order.###\n"
            f"EXAMPLE OBJECTIVE={json.dumps(example_objective)}"
            f"TASK LIST={json.dumps(example_tasklist)}"
            f"OBJECTIVE={objective}"
            f"TASK LIST="
        )

        print("\033[90m\033[3m" + "\nInitializing...\n" + "\033[0m")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": "You are a task creation AI."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        result = response["choices"][0]["message"]["content"]
        try:
            self.tasks = json.loads(result)
        except Exception as error:
            print(error)

    def execute_task(self, i, task, skill_registry, task_outputs, objective):
        print(f"\033[92m\033[1m\n*****NEXT TASK ID:{task['id']}*****\n\033[0m\033[0m"
              f"Executing task {task['id']}: {task['task']} [{task['skill']}]\033[")
        skill = skill_registry.get_skill(task["skill"])
        dependent_task_outputs = {
            dep: task_outputs[dep]["output"] for dep in task.get("dependent_task_ids", [])}
        task_output = skill.execute(task["task"], dependent_task_outputs, objective)
        print("\033[93m\033[1m\nTask Output (ID:" + str(task['id']) + "):\033[0m\033[0m")
        print("TASK: " + str(task["task"]))
        print("OUTPUT: " + str(task_output))
        return i, task_output

    def reorder_tasks(self):
        self.tasks = sorted(self.tasks, key=lambda task: task["id"])

    def add_task(self, task, after_task_id):
        task_ids = [t["id"] for t in self.tasks]
        insert_index = task_ids.index(after_task_id) + 1 if after_task_id in task_ids else len(task_ids)
        self.tasks.insert(insert_index, task)
        self.reorder_tasks()

    def update_tasks(self, task_update):
        for task in self.tasks:
            if task["id"] == task_update["id"]:
                task.update(task_update)
                self.reorder_tasks()
                break

    def reflect_on_output(self, task_output, skill_descriptions):
        prompt = (
            f"You are an expert task manager, review the task output to decide at least one new task to add. "
            f"As you add a new task, see if there are any tasks that need to be updated (such as updating dependencies). "
            f"Use the current task list as reference. "
            f"Do not add duplicate tasks to those in the current task list. "
            f"Only provide JSON as your response without further comments. "
            f"Every new and updated task must include all variables, even they are empty array. "
            f"Dependent IDs must be smaller than the ID of the task. "
            f"New tasks IDs should be no larger than the last task ID. "
            f"Always select at least one skill. "
            f"Task IDs should be unique and in chronological order. "
            f"Do not change the status of complete tasks. "
            f"Only add skills from the AVAILABLE SKILLS, using the exact same spelling. "
            f"Provide your array as a JSON array with double quotes. The first object is new tasks to add as a JSON array, the second array lists the ID numbers where the new tasks should be added after (number of ID numbers matches array), and the third object provides the tasks that need to be updated. "
            f"Make sure to keep dependent_task_ids key, even if an empty array. "
            f"AVAILABLE SKILLS: {skill_descriptions}.###"
            f"\n###Here is the last task output: {task_
