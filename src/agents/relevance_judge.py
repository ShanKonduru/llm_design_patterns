from typing import Dict, Any, Optional
import json

from .base import BaseAgent, Verdict, ConfigLoader

class RelevanceJudgeAgent(BaseAgent):
    """
    The Judge Agent responsible for evaluating the relevance of the answer
    to the given question.
    """
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("RelevanceJudgeAgent", config_loader)

    def run(self, case_data: Dict[str, Any]) -> Optional[Verdict]:
        """
        Runs the relevance evaluation using the agent's LLM.
        """
        print(f"[{self.agent_name}] Evaluating case...")

        # Use the agent's LLM to reason about the relevance of the answer.
        reasoning_prompt = f"""
        {self.persona}

        Case Data:
        - Question: {case_data['question']}
        - Answer: {case_data['answer']}

        Based on the case data, provide your final written verdict on the relevance of the answer to the question. The answer should directly address the user's query without unnecessary information. Your verdict should explain your reasoning and give a final, single, overall score for relevance on a scale of 0.0 to 1.0.
        
        Return your response as a JSON object with two keys: "final_score" and "verdict_text".
        """
        
        try:
            response_str = self.llm.invoke(reasoning_prompt)
            
            # Robustly parse the JSON from the LLM's response string
            if "```json" in response_str:
                json_str = response_str.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_str

            verdict_data = json.loads(json_str)
            
            final_score = verdict_data.get("final_score", 0.0)
            verdict_text = verdict_data.get("verdict_text", "Could not generate a verdict.")

        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            print(f"[{self.agent_name}] Error parsing LLM response: {e}")
            print(f"Raw response was: {response_str}")
            final_score = 0.0
            verdict_text = "Failed to generate a valid verdict due to a response format error."

        return Verdict(
            judge_name=self.agent_name,
            score=float(final_score),
            verdict=verdict_text,
            metrics={}
        )
