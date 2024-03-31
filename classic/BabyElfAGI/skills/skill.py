class Skill:
    """
    A base class for skills that require API keys to execute.
    """

    def __init__(self, api_keys: dict):
        """
        Initialize the skill with the given API keys.

        :param api_keys: A dictionary mapping API key names to their values.
        """
        self.api_keys = api_keys
        missing_keys = self.check_required_keys(api_keys)
        if missing_keys:
            print(f"Missing API keys for {self.name}: {missing_keys}")
            self.valid = False
        else:
            self.valid = True
            self.setup(api_keys)

    def check_required_keys(self, api_keys: dict) -> set:
        """
        Check if all required API keys are present in the given dictionary.

        :param api_keys: A dictionary mapping API key names to their values.
        :return: A set of missing API key names.
        """
        missing_keys = set(self.api_keys_required) - set(api_keys.keys())
        return missing_keys

    def setup(self, api_keys: dict):
        """
        Set up the skill using the given API keys.

        This method is called only if all required API keys are present.

        :param api_keys: A dictionary mapping API key names to their values.
        """
        for key in self.api_keys_required:
            if isinstance(key, list):
                for subkey in key:
                    if subkey in api_keys:
                        setattr(self, f"{subkey}_api_key", api_keys.get(subkey))
            elif key in api_keys:
                setattr(self, f"{key}_api_key", api_keys.get(key))

    def execute(self, params, dependent_
