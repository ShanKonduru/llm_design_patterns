from typing import Dict, Any, Optional, List
import json

from .base import BaseAgent, ConfigLoader
from src.tools import TOOL_REGISTRY, BaseTool

class ToolUsingAgent(BaseAgent):
    """
    An agent that can use a predefined set of tools to answer questions.
    """
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("ToolUsingAgent", config_loader)
        self.tools = TOOL_REGISTRY

    def _choose_tool(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Uses the LLM to decide which tool to use based on the user's prompt.
        """
        # Create a formatted list of available tools for the prompt
        tool_descriptions = "\n".join(
            [f"- {name}: {tool.description}" for name, tool in self.tools.items()]
        )

        # The system prompt guides the LLM to act as a tool-choosing router
        system_prompt = f"""
        You are a helpful assistant that decides which tool to use to answer a user's question.
        You have access to the following tools:
        {tool_descriptions}

        Based on the user's prompt, decide which tool is the most appropriate.
        If no tool is suitable, respond with "None".

        Return your response as a JSON object with two keys:
        - "tool_name": The name of the selected tool (e.g., "WebSearch").
        - "tool_params": The input parameter for the tool (e.g., "what is ragas").
        
        If no tool is needed, the value for "tool_name" should be "None".
        """

        # Combine the system prompt with the user's actual prompt
        full_prompt = f"{system_prompt}\n\nUser Prompt: {prompt}"
        
        print(f"[{self.agent_name}] Deciding which tool to use...")
        response_text = self.llm.llm.invoke(full_prompt)
        
        try:
            # Extract the JSON part of the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"tool_name": "None"}
        except json.JSONDecodeError:
            print(f"[{self.agent_name}] Warning: Could not decode JSON from LLM response.")
            return {"tool_name": "None"}

    def run(self, prompt: str) -> str:
        """
        The main execution loop for the Tool-Using Agent.
        """
        print(f"[{self.agent_name}] Received prompt: '{prompt}'")

        # Step 1: Decide which tool to use
        tool_choice = self._choose_tool(prompt)
        tool_name = tool_choice.get("tool_name")

        if not tool_name or tool_name == "None":
            print(f"[{self.agent_name}] Decided that no tool is needed.")
            # If no tool is chosen, just use the LLM to generate a direct response
            return self.llm.llm.invoke(prompt)

        # Step 2: Execute the chosen tool
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found."

        tool_params = tool_choice.get("tool_params", "")
        try:
            tool_result = tool.execute(tool_params)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"

        # Step 3: Synthesize the final answer using the tool's result
        synthesis_prompt = f"""
        You are a helpful assistant.
        A user asked the following question: "{prompt}"
        
        To answer this, I used the '{tool_name}' tool with the parameter '{tool_params}'.
        The result from the tool was:
        ---
        {tool_result}
        ---

        Based on the tool's result, provide a clear and concise final answer to the user's original question.
        """
        
        print(f"[{self.agent_name}] Synthesizing final answer...")
        final_answer = self.llm.llm.invoke(synthesis_prompt)
        
        return final_answer
