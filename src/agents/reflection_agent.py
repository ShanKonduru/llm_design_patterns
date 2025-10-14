"""
Reflection Agent - Implements the Self-Correction Pattern

This agent evaluates its own output and iteratively improves it through
self-critique and refinement.
"""
from typing import Dict, Any, List, Optional
import json

from .base import BaseAgent, ConfigLoader


class ReflectionAgent(BaseAgent):
    """
    An agent that implements the Reflection/Self-Correction pattern.
    
    It generates an initial response, critically evaluates it, identifies
    areas for improvement, and iteratively refines the output until it
    meets quality standards or reaches the maximum iteration limit.
    
    Use Cases:
    - High-quality content generation (legal contracts, technical docs)
    - Code generation with automated debugging
    - Essay writing with self-editing
    - Complex problem-solving with verification
    """
    
    def __init__(self, config_loader: ConfigLoader, max_iterations: int = 3):
        """
        Initialize the Reflection Agent.
        
        Args:
            config_loader: Configuration loader for agent settings
            max_iterations: Maximum number of refinement iterations (default: 3)
        """
        super().__init__("ReflectionAgent", config_loader)
        self.max_iterations = max_iterations
    
    def _generate_initial_response(self, task: str, context: Optional[str] = None) -> str:
        """
        Generate the initial response to the task.
        
        Args:
            task: The task or prompt to respond to
            context: Optional context or requirements
            
        Returns:
            Initial generated response
        """
        prompt = f"""{self.persona}

Task: {task}
{f"Context/Requirements: {context}" if context else ""}

Generate your initial response to this task. Be thorough and detailed.
"""
        
        print(f"[{self.agent_name}] Generating initial response...")
        response = self.llm.llm.invoke(prompt)
        return response
    
    def _critique_response(self, task: str, response: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Critically evaluate the current response.
        
        Args:
            task: The original task
            response: The current response to critique
            context: Optional context or requirements
            
        Returns:
            Dictionary containing critique score, issues found, and suggestions
        """
        critique_prompt = f"""You are a critical reviewer. Your job is to identify errors, weaknesses, 
and areas for improvement in the following response.

Original Task: {task}
{f"Requirements: {context}" if context else ""}

Current Response:
---
{response}
---

Evaluate this response critically and return a JSON object with:
1. "quality_score": A score from 0.0 to 1.0 (1.0 being perfect)
2. "issues_found": A list of specific problems or errors
3. "suggestions": Concrete suggestions for improvement
4. "is_acceptable": Boolean indicating if the response meets minimum quality standards

Be thorough and constructive. Return ONLY valid JSON.
"""
        
        print(f"[{self.agent_name}] Critiquing current response...")
        critique_response = self.llm.llm.invoke(critique_prompt)
        
        try:
            # Extract JSON from response
            json_start = critique_response.find('{')
            json_end = critique_response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = critique_response[json_start:json_end]
                critique = json.loads(json_str)
                
                # Validate structure
                required_keys = ["quality_score", "issues_found", "suggestions", "is_acceptable"]
                if all(key in critique for key in required_keys):
                    return critique
                else:
                    print(f"[{self.agent_name}] Warning: Incomplete critique structure")
                    return self._default_critique()
            else:
                print(f"[{self.agent_name}] Warning: No JSON found in critique")
                return self._default_critique()
                
        except json.JSONDecodeError as e:
            print(f"[{self.agent_name}] Error parsing critique JSON: {e}")
            return self._default_critique()
    
    def _default_critique(self) -> Dict[str, Any]:
        """Return a default critique when parsing fails."""
        return {
            "quality_score": 0.5,
            "issues_found": ["Unable to parse critique"],
            "suggestions": ["Try again with clearer output"],
            "is_acceptable": False
        }
    
    def _refine_response(
        self, 
        task: str, 
        current_response: str, 
        critique: Dict[str, Any],
        context: Optional[str] = None
    ) -> str:
        """
        Refine the response based on the critique.
        
        Args:
            task: The original task
            current_response: The current response to improve
            critique: The critique containing issues and suggestions
            context: Optional context or requirements
            
        Returns:
            Refined response
        """
        refinement_prompt = f"""You are refining a previous response based on critical feedback.

Original Task: {task}
{f"Requirements: {context}" if context else ""}

Previous Response:
---
{current_response}
---

Critique Feedback:
- Quality Score: {critique['quality_score']:.2f}
- Issues Found: {json.dumps(critique['issues_found'], indent=2)}
- Suggestions: {json.dumps(critique['suggestions'], indent=2)}

Based on this critique, generate an improved version that addresses all identified issues
and implements the suggestions. Maintain what was good while fixing the problems.
"""
        
        print(f"[{self.agent_name}] Refining response based on critique...")
        refined_response = self.llm.llm.invoke(refinement_prompt)
        return refined_response
    
    def run(
        self, 
        task: str, 
        context: Optional[str] = None,
        quality_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Execute the reflection/self-correction pattern.
        
        Args:
            task: The task or prompt to complete
            context: Optional context or requirements
            quality_threshold: Minimum quality score to accept (0.0-1.0)
            
        Returns:
            Dictionary containing:
            - final_response: The best response after refinement
            - iterations: Number of refinement iterations performed
            - critiques: List of all critiques from each iteration
            - final_quality_score: Quality score of the final response
        """
        print(f"\n[{self.agent_name}] Starting reflection process...")
        print(f"[{self.agent_name}] Task: {task}")
        print(f"[{self.agent_name}] Quality threshold: {quality_threshold}")
        print(f"[{self.agent_name}] Max iterations: {self.max_iterations}\n")
        
        # Generate initial response
        current_response = self._generate_initial_response(task, context)
        
        critiques: List[Dict[str, Any]] = []
        iteration = 0
        
        # Iterative refinement loop
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration}/{self.max_iterations} ---")
            
            # Critique current response
            critique = self._critique_response(task, current_response, context)
            critiques.append(critique)
            
            quality_score = critique.get("quality_score", 0.0)
            is_acceptable = critique.get("is_acceptable", False)
            
            print(f"[{self.agent_name}] Quality Score: {quality_score:.2f}")
            print(f"[{self.agent_name}] Issues Found: {len(critique.get('issues_found', []))}")
            
            # Check if quality threshold is met
            if quality_score >= quality_threshold and is_acceptable:
                print(f"\n[{self.agent_name}] ✅ Quality threshold met! Stopping refinement.")
                break
            
            # Check if this is the last iteration
            if iteration >= self.max_iterations:
                print(f"\n[{self.agent_name}] ⚠️ Max iterations reached.")
                break
            
            # Refine the response
            current_response = self._refine_response(task, current_response, critique, context)
        
        # Final critique
        final_critique = self._critique_response(task, current_response, context)
        
        result = {
            "final_response": current_response,
            "iterations": iteration,
            "critiques": critiques,
            "final_critique": final_critique,
            "final_quality_score": final_critique.get("quality_score", 0.0),
            "improvement": (
                final_critique.get("quality_score", 0.0) - critiques[0].get("quality_score", 0.0)
                if critiques else 0.0
            )
        }
        
        print(f"\n[{self.agent_name}] === Reflection Complete ===")
        print(f"[{self.agent_name}] Total Iterations: {iteration}")
        print(f"[{self.agent_name}] Final Quality Score: {result['final_quality_score']:.2f}")
        print(f"[{self.agent_name}] Improvement: {result['improvement']:+.2f}")
        
        return result
