from abc import ABC, abstractmethod

class Skill(ABC):
    """
    Base class for all skills.
    """
    name: str
    description: str
    api_keys_required: list[str | list[str]]

    def __init__(self, api_keys: dict[str, str], main_loop_function):
        """
        Initialize the skill.

        :param api_keys: A dictionary of API keys required for the skill.
        :param main_loop_function: The main loop function for the skill.
        """
        self.name = 'base skill'
        self.description = 'This is the base skill.'
        self.api_keys_required = []

        print(f"Initializing {self.name}")
        self.api_keys = api_keys
        self.main_loop_function = main_loop_function
        missing_keys = self.check_required_keys(api_keys)
        if missing_keys:
            print(f"Missing API keys for {self.name}: {missing_keys}")
            self.valid = False
        else:
            self.valid = True
        for key in self.api_keys_required:
            if isinstance(key, list):
                for subkey in key:
                    if subkey in api_keys:
                        setattr(self, f"{subkey}_api_key", api_keys.get(subkey))
            elif key in api_keys:
                setattr(self, f"{key}_api_key", api_keys.get(key))
        print(f"{self.name} initialized successfully")

    def check_required_keys(self, api_keys: dict[str, str]) -> list[str]:
        """
        Check if all required API keys are present.

        :param api_keys: A dictionary of API keys.
        :return: A list of missing API keys.
        """
        missing_keys = []
        for key in self.api_keys_required:
            if isinstance(key, list):  # If the key is actually a list of alternatives
                if not any(k in api_keys for k in key):  # If none of the alternatives are present
                    missing_keys.append(key)  # Add the list of alternatives to the missing keys
            elif key not in api_keys:  # If the key
