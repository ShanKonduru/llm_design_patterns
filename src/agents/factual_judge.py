from typing import Dict, Any, Optional

from .base import BaseAgent, Verdict, ConfigLoader
from src.llm_evaluation import RagasEvaluator

class FactualJudgeAgent(BaseAgent):
    """
    The Judge Agent responsible for evaluating factual consistency and accuracy.
    """
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("FactualJudgeAgent", config_loader)
        # This agent uses ragas, so it needs the RagasEvaluator tool.
        # The RagasEvaluator itself uses an LLM, which we pass from this agent.
        self.ragas_tool = RagasEvaluator(self.llm)

    def run(self, case_data: Dict[str, Any]) -> Optional[Verdict]:
        """
        Runs the factual evaluation using Ragas metrics and then synthesizes a verdict.
        """
        print(f"[{self.agent_name}] Evaluating case...")
        
        # Step 1: Use RagasEvaluator to get raw scores
        try:
            faithfulness_score = self.ragas_tool.evaluate_faithfulness(
                question=case_data['question'],
                answer=case_data['answer'],
                contexts=case_data['contexts']
            )
            correctness_score = self.ragas_tool.evaluate_answer_correctness(
                question=case_data['question'],
                answer=case_data['answer'],
                ground_truth=case_data['ground_truth']
            )
            
            faithfulness = faithfulness_score.get('faithfulness', 0.0)
            correctness = correctness_score.get('answer_correctness', 0.0)
            
        except Exception as e:
            print(f"[{self.agent_name}] Error during Ragas evaluation: {e}")
            return None

        # Step 2: Use the agent's LLM to reason over the scores and generate a verdict
        reasoning_prompt = f"""
        {self.persona}

        Case Data:
        - Question: {case_data['question']}
        - Answer: {case_data['answer']}
        - Ground Truth: {case_data['ground_truth']}

        I have conducted my analysis and collected the following metrics:
        - Faithfulness Score (consistency with context): {faithfulness:.2f}
        - Answer Correctness Score (accuracy against ground truth): {correctness:.2f}

        Based on these scores and the case data, provide your final written verdict. Your verdict should explain the reasoning behind the scores and give a final, single, overall score for factual integrity on a scale of 0.0 to 1.0.
        
        Return your response as a JSON object with two keys: "final_score" and "verdict_text".
        """
        
        try:
            response = self.llm.invoke(reasoning_prompt)
            # Assuming the response is a JSON string, we need to parse it.
            # This might need a more robust parsing mechanism in a real implementation.
            import json
            verdict_data = json.loads(response)
            
            final_score = verdict_data.get("final_score", 0.0)
            verdict_text = verdict_data.get("verdict_text", "Could not generate a verdict.")

        except (json.JSONDecodeError, AttributeError) as e:
            print(f"[{self.agent_name}] Error parsing LLM response: {e}")
            final_score = 0.0
            verdict_text = "Failed to generate a valid verdict due to a response format error."

        return Verdict(
            judge_name=self.agent_name,
            score=float(final_score),
            verdict=verdict_text,
            metrics={"faithfulness": faithfulness, "answer_correctness": correctness}
        )
