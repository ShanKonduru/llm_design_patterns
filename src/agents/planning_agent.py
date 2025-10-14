from typing import Dict, Any, List
import json

from .base import BaseAgent, ConfigLoader
from src.tools import TOOL_REGISTRY

class PlanningAgent(BaseAgent):
    """
    An agent that creates a plan and executes it to accomplish a goal.
    This is a simplified implementation of the "Plan-and-Execute" pattern.
    """
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("PlanningAgent", config_loader)
        self.tools = TOOL_REGISTRY

    def _create_plan(self, goal: str) -> List[Dict[str, str]]:
        """
        Uses the LLM to decompose a goal into a sequence of tool-using steps.
        """
        tool_descriptions = "\n".join(
            [f"- {name}: {tool.description}" for name, tool in self.tools.items()]
        )

        system_prompt = f"""You are a planning assistant. Your job is to create a step-by-step plan to achieve a user's goal.
Each step in the plan must involve a single call to one of the available tools.

Available Tools:
{tool_descriptions}

CRITICAL: You must respond with ONLY a valid JSON array. Do not include any explanation before or after the JSON.

Decompose the user's goal into a sequence of steps.
Return ONLY a JSON array of objects. Each object must have exactly three keys:
- "step": A short description of what this step does
- "tool_name": The exact name of the tool to use (must be one of: WebSearch, Calculator, DateTime, CodeInterpreter)
- "tool_params": The input parameter string for the tool

Example Goal: "Find when Python was created and calculate 2024 minus that year"
Example Response (respond with ONLY this format):
[
    {{"step": "Search for when Python was created", "tool_name": "WebSearch", "tool_params": "when was python programming language created"}},
    {{"step": "Calculate 2024 minus the year Python was created", "tool_name": "Calculator", "tool_params": "2024 - 1991"}}
]

User Goal: {goal}

Respond with ONLY the JSON array, no other text:"""
        
        print(f"[{self.agent_name}] Creating a plan for goal: '{goal}'")
        response_text = self.llm.llm.invoke(system_prompt)
        
        print(f"[{self.agent_name}] Raw LLM Response:\n---\n{response_text}\n---")

        try:
            # Try to find JSON array in the response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                plan = json.loads(json_str)
                
                # Validate the plan structure
                if isinstance(plan, list) and len(plan) > 0:
                    for step in plan:
                        if not all(key in step for key in ["step", "tool_name", "tool_params"]):
                            print(f"[{self.agent_name}] Warning: Invalid step structure in plan")
                            return []
                    return plan
                else:
                    print(f"[{self.agent_name}] Warning: Plan is not a valid list or is empty")
                    return []
            else:
                print(f"[{self.agent_name}] Warning: No JSON array found in response")
                return []
        except json.JSONDecodeError as e:
            print(f"[{self.agent_name}] Warning: Could not decode plan from LLM response. Error: {e}")
            return []
        except Exception as e:
            print(f"[{self.agent_name}] Unexpected error parsing plan: {e}")
            return []
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return []
        except json.JSONDecodeError:
            print(f"[{self.agent_name}] Warning: Could not decode plan from LLM response.")
            return []

    def run(self, goal: str) -> str:
        """
        The main execution loop for the Planning Agent.
        """
        print(f"[{self.agent_name}] Received goal: '{goal}'")

        # Step 1: Create a plan
        plan = self._create_plan(goal)
        if not plan:
            return "I could not create a plan to achieve that goal."

        print(f"[{self.agent_name}] Plan created with {len(plan)} steps.")
        
        # Step 2: Execute the plan
        step_results = []
        for i, step in enumerate(plan):
            print(f"\n--- Executing Step {i+1}/{len(plan)}: {step['step']} ---")
            tool_name = step.get("tool_name")
            tool = self.tools.get(tool_name)

            if not tool:
                step_results.append(f"Step {i+1} failed: Tool '{tool_name}' not found.")
                continue

            tool_params = step.get("tool_params", "")
            try:
                result = tool.execute(tool_params)
                step_results.append(result)
            except Exception as e:
                step_results.append(f"Step {i+1} failed: Error executing tool '{tool_name}': {e}")
        
        # Step 3: Synthesize the final answer from the results of all steps
        synthesis_prompt = f"""
        You are a helpful assistant.
        A user gave you the following goal: "{goal}"

        To achieve this, I executed a plan with {len(plan)} steps.
        Here are the results from each step:
        ---
        {step_results}
        ---

        Based on the results of the plan, provide a final, comprehensive answer to the user's original goal.
        """
        
        print(f"\n[{self.agent_name}] Synthesizing final answer from all step results...")
        final_answer = self.llm.llm.invoke(synthesis_prompt)
        
        return final_answer
