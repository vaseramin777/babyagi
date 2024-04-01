import openai
import os
import requests
from urllib.parse import quote  # Python built-in URL encoding function
from skills.skill import Skill

class AirtableSearch(Skill):
    name = 'airtable_search'
    description = "A skill that retrieves data from our Airtable notes using a search. Useful for remembering who we talked to about a certain topic."
    api_keys_required = ['code_reader', 'skill_saver', 'documentation_search', 'text_completion', 'airtable']

    def __init__(self, api_keys, main_loop_function):
        super().__init__(api_keys, main_loop_function)
        self.airtable_api_key = self.api_keys['airtable']
        self.base_id = '<base_id>'
        self.table_name = '<table_name>'
        self.filter_field = '<filter_field>'

    def execute(self, params, dependent_task_outputs, objective):
        if not self.valid:
            return

        tried_queries = []
        dependent_task = f"Use the dependent task output below as reference to help craft the correct search query for the provided task above. Dependent task output: {dependent_task_outputs}." if dependent_task_outputs else "."

        output = ''
        while not output:
            tried_queries_prompt = f" Do not include search queries we have tried, and instead try synonyms or misspellings. Search queries we have tried: {', '.join(tried_queries)}." if tried_queries else ""
            query = self.text_completion_tool(f"You are an AI assistant tasked with generating a one word search query based on the following task: {params}. Provide only the search query as a response. {tried_queries_prompt} Take into account output from the previous task:{dependent_task}.\nExample Task: Retrieve data from Airtable notes using the skill 'airtable_search' to find people we have talked to about TED AI.\nExample Query:TED AI\nExample Task:Conduct a search in our Airtable notes to identify investors who have expressed interest in climate.\nExample Query:climate\nTask:{params}\nQuery:")

            if not query or len(query.strip()) == 0:
                continue

            if query in tried_queries:
                continue

            tried_queries.append(query)
            print(f"\033[90m\033[3mSearch query: {query}\033[0m")

            headers = {
                "Authorization": f"Bearer {self.airtable_api_key}",
                "Content-Type": "application/json"
            }

            filter_value = query
            if ' ' in filter_value:
                filter_value = f'"{filter_value}"'

            encoded_filter_field = quote(self.filter_field)
            formula_field = f'{{{self.filter_field}}}' if ' ' in self.filter_field else f'{self.filter_field}'
            formula = f"{filter_value},{formula_field}"
            encoded_formula = quote(formula)

            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}?fields%5B%5D={encoded_filter_field}&filterByFormula=FIND({encoded_formula})"
            print(f"\033[90m\033[3mURL: {url}\033[0m")

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve data from Airtable. Error: {e}")
                return None

            data = response.json()
            if 'records' not in data or len(data['records']) == 0:
                print("No records found.")
                continue

            output = self._process_record(data['records'][0], params, objective)

        output = f"Tried Queries: {str(tried_queries)}###Result:{output}"
        return output

    def _process_record(self, record, params, objective):
        input_str = f"Your objective:{objective}\nYour task:{params}\nThe Airtable record:{record['fields']}"
        instructions = f"Update the existing summary by adding information from this new record. ###Current summary:{output}." if output else ""
        response = self.text_completion_tool(f"You are an AI assistant that will review content from an Airtable record provided by the user, and extract only relevant information to the task at hand with context on why that information is relevant, taking into account the objective. If there is no relevant info, simply respond with '###'. Note that the Airtable note may use shorthand, and do your best to understand it first.{instructions} #####AIRTABLE DATA: {input_str}.")
        return response

    def text_completion_tool(self, prompt: str):
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=0.2,
            max_tokens=350,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message['content'].strip()
