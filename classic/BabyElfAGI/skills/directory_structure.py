from skills.skill import Skill
import os
from typing import Dict, Union, Any

class DirectoryStructure(Skill):
    """
    A tool that outputs the file and folder structure of its top parent folder.
    """
    name = 'directory_structure'
    description = "A tool that outputs the file and folder structure of its top parent folder."

    def __init__(self, api_keys: dict = None):
        super().__init__(api_keys)

    def execute(self, params: dict, dependent_task_outputs: dict, objective: dict) -> Dict[str, Union[Dict[str, Any], str]]:
        # Get the current script path
        current_script_path = os.path.realpath(__file__)

        # Get the top parent directory of current script
        top_parent_path = self.get_top_parent_path(current_script_path)

        # Get the directory structure from the top parent directory
        dir_structure = self.get_directory_structure(top_parent_path)

        return dir_structure

    def get_directory_structure(self, start_path: str, depth: int = 1) -> Dict[str, Union[Dict[str, Any], str]]:
        dir_structure = {}
        ignore_dirs = ['.', '__init__.py', '__pycache__', 'pydevd', 'poetry', 'venv']  # add any other directories to ignore here

        try:
            for root, dirs, files in os.walk(start_path):
                dirs[:] = [d for d in dirs if not any(d.startswith(i) for i in ignore_dirs)]  # exclude specified directories
                files = [f for f in files if not f[0] == '.']  # exclude hidden files

                current_dict = dir_structure
                path_parts = os.path.relpath(root, start_path).split(os.sep)

                for part in path_parts:
                    if part:  # skip empty parts
                        if part not in current_dict:
                            current_dict[part] = {}
                        current_dict = current_dict[part]

                for f in files:
                    current_dict[f] = None

                # Handle nested directories
                for d in dirs:
                    nested_dir_structure = self.get_directory_structure(os.path.join(root, d), depth=depth + 1)
                    for key, value in nested_dir_structure.items():
                        current_dict[key] = value

        except FileNotFoundError:
            print(f"Error: The starting path '{start_path}' does not exist.")
            return {}

        return dir_structure

    def get_top_parent_path(self, current_path: str) -> str:
        top_parent_path = os.path.abspath(os.path.join(current_path, os.pardir))

        if top_parent_path == os.path.abspath(top_parent_path + os.sep + os.pardir):
            return top_parent_path
        else:
            return self.get_top_parent_path(top_parent_path)
