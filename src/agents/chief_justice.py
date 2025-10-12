from typing import Dict, Any, List, Optional
import json
import pandas as pd

from .base import BaseAgent, Verdict, ConfigLoader
from .factual_judge import FactualJudgeAgent
from .clarity_judge import ClarityJudgeAgent
from .relevance_judge import RelevanceJudgeAgent
from .safety_judge import SafetyJudgeAgent

class ChiefJusticeAgent(BaseAgent):
    """
    The Chief Justice Agent, acting as the Jury. It orchestrates the Judge Agents,
    collects their verdicts, and synthesizes a final, comprehensive judgment.
    """
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("ChiefJusticeAgent", config_loader)
        
        # The Chief Justice presides over a jury of specialized judges
        self.jury: List[BaseAgent] = [
            FactualJudgeAgent(config_loader),
            ClarityJudgeAgent(config_loader),
            RelevanceJudgeAgent(config_loader),
            SafetyJudgeAgent(config_loader)
        ]

    def run(self, case_data: Dict[str, Any]) -> Optional[Verdict]:
        """
        Orchestrates the jury to evaluate the case and synthesizes a final verdict.
        """
        print(f"[{self.agent_name}] The court is now in session. The jury will deliberate.")
        
        # Step 1: Collect verdicts from all judges in the jury
        all_verdicts: List[Verdict] = []
        for judge in self.jury:
            verdict = judge.run(case_data)
            if verdict:
                all_verdicts.append(verdict)
            else:
                print(f"[{self.agent_name}] Warning: Judge {judge.agent_name} failed to return a verdict.")

        if not all_verdicts:
            print(f"[{self.agent_name}] The jury failed to reach any verdicts. Case dismissed.")
            return None

        # Step 2: Format the collected verdicts into a report for the Chief Justice's LLM
        jury_report = "\n\n".join(
            [f"--- Verdict from {v.judge_name} (Score: {v.score:.2f}) ---\n{v.verdict}" for v in all_verdicts]
        )
        
        # Step 3: Use the Chief Justice's LLM to synthesize a final judgment
        reasoning_prompt = f"""
        {self.persona}

        I have received the following verdicts from the panel of judges:

        {jury_report}

        Based on all these verdicts, provide your final, synthesized judgment. Your judgment should summarize the key findings from each judge, calculate a final, single, overall score by averaging the scores from the jury, and provide a concluding statement.
        
        Return your response as a JSON object with two keys: "final_score" and "verdict_text". The "final_score" should be the calculated average of the jury's scores.
        """
        
        try:
            # Calculate the average score from the jury's verdicts
            avg_score = sum(v.score for v in all_verdicts) / len(all_verdicts) if all_verdicts else 0.0

            response_str = self.llm.invoke(reasoning_prompt)
            
            if "```json" in response_str:
                json_str = response_str.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_str
            
            verdict_data = json.loads(json_str)
            
            # We trust the LLM's text, but we use our calculated average for the score
            final_score = avg_score
            verdict_text = verdict_data.get("verdict_text", "Could not generate a final judgment.")

        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            print(f"[{self.agent_name}] Error parsing LLM response: {e}")
            print(f"Raw response was: {response_str}")
            final_score = 0.0
            verdict_text = "Failed to generate a valid final judgment due to a response format error."

        # Step 4: Return the final, comprehensive verdict
        return Verdict(
            judge_name=self.agent_name,
            score=final_score,
            verdict=verdict_text,
            metrics={"individual_verdicts": all_verdicts}
        )

    def verdicts_to_dataframe(self, final_verdict: Verdict) -> pd.DataFrame:
        """
        Converts the final verdict and its nested individual verdicts into a pandas DataFrame.
        """
        records = []
        if final_verdict and isinstance(final_verdict.metrics.get("individual_verdicts"), list):
            for v in final_verdict.metrics["individual_verdicts"]:
                record = {
                    "judge": v.judge_name,
                    "score": v.score,
                    "verdict": v.verdict,
                }
                # Add specific sub-metrics if they exist
                if v.metrics:
                    record.update(v.metrics)
                records.append(record)
        
        # Add the Chief Justice's final verdict as a summary row
        records.append({
            "judge": final_verdict.judge_name,
            "score": final_verdict.score,
            "verdict": final_verdict.verdict
        })

        df = pd.DataFrame(records)
        # Reorder columns for clarity
        cols = ['judge', 'score', 'verdict'] + [col for col in df.columns if col not in ['judge', 'score', 'verdict']]
        return df[cols]
