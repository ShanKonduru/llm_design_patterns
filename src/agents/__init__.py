"""
The agents package for the LLM as a Judge/Jury evaluation system.
"""
from .base import BaseAgent, Verdict
from .config import ConfigLoader
from .factual_judge import FactualJudgeAgent
# Import other agents here as they are created
from .clarity_judge import ClarityJudgeAgent
from .relevance_judge import RelevanceJudgeAgent
from .safety_judge import SafetyJudgeAgent
from .chief_justice import ChiefJusticeAgent

__all__ = [
    "BaseAgent",
    "Verdict",
    "ConfigLoader",
    "FactualJudgeAgent",
    "ClarityJudgeAgent",
    "RelevanceJudgeAgent",
    "SafetyJudgeAgent",
    "ChiefJusticeAgent",
]
