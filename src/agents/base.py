from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from src.llm_evaluation import LLMFactory
from .config import ConfigLoader

@dataclass
class Verdict:
    """A structured output for any Judge Agent's evaluation."""
    judge_name: str
    score: float
    verdict: str
    metrics: Dict[str, float] = field(default_factory=dict)

class BaseAgent(ABC):
    """
    An abstract base class for all agents in the evaluation system.
    It ensures that every agent has a consistent interface.
    """
    def __init__(self, agent_name: str, config_loader: ConfigLoader):
        self.agent_name = agent_name
        self.config = config_loader.get_agent_config(agent_name)
        self.persona = self.config['persona_prompt']
        self.llm = LLMFactory.get_llm(model_name=self.config['model'])

    @abstractmethod
    def run(self, case_data: Dict[str, Any]) -> Optional[Verdict]:
        """
        The main execution method for the agent.
        Subclasses must implement this to perform their specific evaluation.
        
        Args:
            case_data: A dictionary containing the data to be evaluated,
                       e.g., {'question': ..., 'answer': ..., 'contexts': ...}.
                       
        Returns:
            A Verdict object or None if the evaluation cannot be completed.
        """
        pass
