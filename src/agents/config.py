import json
from typing import Dict, Any

class ConfigLoader:
    """A utility class to load agent configurations from a JSON file."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # Don't pass any arguments to the object's __new__ method
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path="agents.json"):
        if not hasattr(self, 'config'):
            with open(config_path, 'r') as f:
                self.config = json.load(f)

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Retrieves the configuration for a specific agent."""
        if agent_name not in self.config['agents']:
            raise ValueError(f"Agent '{agent_name}' not found in configuration.")
        return self.config['agents'][agent_name]

    def get_embedding_model_config(self, model_key: str) -> str:
        """Retrieves the configuration for an embedding model."""
        if model_key not in self.config['embedding_models']:
            raise ValueError(f"Embedding model key '{model_key}' not found in configuration.")
        return self.config['embedding_models'][model_key]
