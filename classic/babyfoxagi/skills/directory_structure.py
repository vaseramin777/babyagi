from skills.skill import Skill
import os
import typing

class DirectoryStructure(Skill):
    """
    A tool that outputs the file and folder structure of its top parent folder.
    """
    name = 'directory_structure'
    description = "A tool that outputs the file and folder structure of its top parent folder."
    ignore_dirs = ['.','__init__.py', '__pycache__', 'pydevd', 'poetry','venv']

    def __init__(self, api_keys: dict, main_loop_function: typing.Callable):
        super().__init__(api_keys, main_loop_function)

    def execute(self, params: dict, dependent_task_outputs: dict, objective: dict) -> dict:
        # Get the current script path
        current_script_path = os.path.realpath(__file__)

        # Get the top parent directory of current script
        top_parent_path = self.get_top_parent_path(current_script_path)

        # Get the directory structure from the top parent directory
        dir_structure = self.get_directory_structure(top_parent_path)

        return dir_structure

    def get_directory_structure(self, start_path: str) -> dict:
        dir_structure = {}

        for root, dirs, files in os.walk(start_path):
            dirs[:] = [d for d in dirs if not any(d.startswith(i) for i in self.ignore_dirs)]  # exclude specified directories
            files = [f for f in files if not f[0] == '.' and f.endswith('.py')]  # exclude hidden files and non-Python files

            current_dict = dir_structure
            path_parts = os.path.relpath(root, start_path).split(os.sep)
            for part in path_parts:
                if part:  # skip empty parts
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]
            for f in files:
                current_dict[f] = None

        return dir_structure

    def get_top_parent_path(self, current_path: str) -> str:
        if not os.path.isdir(current_path):
            raise ValueError(f"{current_path} is not a valid directory")

        parent_path = os.path.abspath(current_path)
        while True:
            parent_path = os.path.abspath(os.path.join(parent_path, ".."))
            if parent_path == os.path.abspath("/").lower():
                return parent_path
