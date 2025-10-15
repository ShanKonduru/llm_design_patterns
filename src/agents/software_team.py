"""
Software Engineering Multi-Agent Team

This module implements specialized agents that collaborate to build software:
- PlannerAgent: Analyzes requirements and creates development plans
- CoderAgent: Writes code based on plans
- TesterAgent: Tests code and identifies issues
- ReviewerAgent: Reviews code quality and suggests improvements

Demonstrates the Multi-Agent Collaboration Pattern applied to software engineering.
"""

from typing import Dict, Any
import json
import re

from .collaboration_agent import CollaborationAgent, AgentTask, AgentResult
from .config import ConfigLoader
from src.llm_evaluation import LLMFactory


class PlannerAgent(CollaborationAgent):
    """
    Planner Agent: Analyzes requirements and creates development plans.
    This agent breaks down software requirements into actionable tasks.
    """
    
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("PlannerAgent", "Planner", config_loader)
    
    def _prepare_task_prompt(self, task: AgentTask) -> str:
        requirements = task.input_data.get("requirements", "")
        
        return f"""{self.persona}

ROLE: Software Development Planner

Your task is to analyze software requirements and create a detailed development plan.

Requirements:
{requirements}

Create a structured development plan with:
1. High-level architecture decisions
2. Key components/modules to implement
3. Implementation steps in logical order
4. Potential challenges and considerations

Format your response as:
ARCHITECTURE:
[Your architecture decisions]

COMPONENTS:
[List of components]

STEPS:
1. [First step]
2. [Second step]
...

CONSIDERATIONS:
[Key considerations]
"""
    
    def _parse_response(self, response: str, task: AgentTask) -> Any:
        """Parse the planner's response into structured plan."""
        return {
            "plan": response,
            "requirements": task.input_data.get("requirements", ""),
            "role": "Planner"
        }


class CoderAgent(CollaborationAgent):
    """
    Coder Agent: Writes code based on plans or requirements.
    This agent generates actual code implementations.
    """
    
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("CoderAgent", "Coder", config_loader)
    
    def _prepare_task_prompt(self, task: AgentTask) -> str:
        input_data = task.input_data
        
        if "previous_output" in input_data:
            # Sequential mode: received plan from Planner
            plan_info = input_data["previous_output"]
            context = f"Development Plan:\n{plan_info.get('plan', '')}"
        else:
            # Parallel or direct mode
            context = f"Requirements:\n{input_data.get('requirements', '')}"
        
        return f"""{self.persona}

ROLE: Software Developer

Your task is to write clean, well-documented code.

Context:
{context}

Write production-quality code that:
1. Follows best practices and coding standards
2. Includes proper error handling
3. Has clear comments and docstrings
4. Is modular and maintainable

Provide your code with explanations.
"""
    
    def _parse_response(self, response: str, task: AgentTask) -> Any:
        """Parse the coder's response and extract code."""
        # Extract code blocks if present
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', response, re.DOTALL)
        
        return {
            "code": response,
            "code_blocks": code_blocks,
            "role": "Coder"
        }


class TesterAgent(CollaborationAgent):
    """
    Tester Agent: Tests code and identifies issues.
    This agent creates test cases and validates implementations.
    """
    
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("TesterAgent", "Tester", config_loader)
    
    def _prepare_task_prompt(self, task: AgentTask) -> str:
        input_data = task.input_data
        
        if "previous_output" in input_data:
            # Sequential mode: received code from Coder
            code_info = input_data["previous_output"]
            code = code_info.get('code', '')
        else:
            # Parallel mode
            code = input_data.get('code', '')
        
        return f"""{self.persona}

ROLE: Software Tester / Quality Assurance

Your task is to test the following code and identify any issues.

Code to Test:
{code}

Provide:
1. Test cases (unit tests)
2. Edge cases to consider
3. Potential bugs or issues found
4. Security considerations
5. Performance concerns

Format your response with clear sections for each aspect.
"""
    
    def _parse_response(self, response: str, task: AgentTask) -> Any:
        """Parse the tester's response and extract findings."""
        return {
            "test_report": response,
            "role": "Tester"
        }


class ReviewerAgent(CollaborationAgent):
    """
    Reviewer Agent: Reviews code quality and suggests improvements.
    This agent performs code review and provides feedback.
    """
    
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("ReviewerAgent", "Reviewer", config_loader)
    
    def _prepare_task_prompt(self, task: AgentTask) -> str:
        input_data = task.input_data
        
        if "previous_output" in input_data:
            # Sequential mode: received test report
            test_info = input_data["previous_output"]
            context = f"Test Report:\n{test_info.get('test_report', '')}"
        else:
            # Parallel mode or hierarchical
            code = input_data.get('code', '')
            test_report = input_data.get('test_report', '')
            context = f"Code:\n{code}\n\nTest Report:\n{test_report}"
        
        return f"""{self.persona}

ROLE: Senior Code Reviewer

Your task is to review the code and test results, providing constructive feedback.

Context:
{context}

Provide a comprehensive code review covering:
1. Code Quality: Readability, maintainability, structure
2. Best Practices: Adherence to language conventions
3. Testing: Adequacy of test coverage
4. Improvements: Specific suggestions for enhancement
5. Approval: Final verdict (APPROVED, NEEDS_CHANGES, REJECTED)

Format your response with clear sections and actionable feedback.
"""
    
    def _parse_response(self, response: str, task: AgentTask) -> Any:
        """Parse the reviewer's response and extract verdict."""
        # Try to determine approval status
        approval_status = "UNKNOWN"
        if "APPROVED" in response.upper() and "NEEDS_CHANGES" not in response.upper():
            approval_status = "APPROVED"
        elif "NEEDS_CHANGES" in response.upper() or "NEEDS CHANGES" in response.upper():
            approval_status = "NEEDS_CHANGES"
        elif "REJECTED" in response.upper():
            approval_status = "REJECTED"
        
        return {
            "review": response,
            "approval_status": approval_status,
            "role": "Reviewer"
        }


class CoordinatorAgent(CollaborationAgent):
    """
    Coordinator Agent: Manages the software engineering team.
    This agent delegates tasks and synthesizes results in hierarchical mode.
    """
    
    def __init__(self, config_loader: ConfigLoader):
        super().__init__("CoordinatorAgent", "Coordinator", config_loader)
    
    def _prepare_task_prompt(self, task: AgentTask) -> str:
        input_data = task.input_data
        
        if "specialist_results" in input_data:
            # Synthesis phase
            results = input_data["specialist_results"]
            results_text = "\n\n".join([f"Agent Result {i+1}:\n{r}" for i, r in enumerate(results)])
            
            return f"""{self.persona}

ROLE: Engineering Team Coordinator

You have received results from your team of specialists.

Team Results:
{results_text}

Your task is to:
1. Synthesize all the inputs from your team
2. Identify any conflicts or issues
3. Create a final, coherent deliverable
4. Provide recommendations for next steps

Provide a comprehensive synthesis and final recommendation.
"""
        else:
            # Planning phase
            requirements = input_data.get("requirements", "")
            
            return f"""{self.persona}

ROLE: Engineering Team Coordinator

You are managing a software engineering team with specialists:
- Planner: Creates development plans
- Coder: Writes implementations
- Tester: Creates and runs tests

Requirements:
{requirements}

Create a coordination plan that:
1. Defines what each specialist should focus on
2. Sets clear objectives for each team member
3. Establishes success criteria
4. Identifies dependencies between specialists

Provide a clear coordination plan.
"""
    
    def _parse_response(self, response: str, task: AgentTask) -> Any:
        """Parse coordinator's response."""
        return {
            "coordination": response,
            "role": "Coordinator"
        }


# Factory function to create a software engineering team
def create_software_team(
    mode: str,
    config_loader: ConfigLoader
) -> tuple:
    """
    Factory function to create a complete software engineering team.
    
    Args:
        mode: Collaboration mode ('sequential', 'parallel', 'hierarchical')
        config_loader: Configuration loader instance
    
    Returns:
        Tuple of (orchestrator, list of agents)
    """
    from .collaboration_agent import CollaborationOrchestrator, CollaborationMode
    
    # Map string to enum
    mode_map = {
        'sequential': CollaborationMode.SEQUENTIAL,
        'parallel': CollaborationMode.PARALLEL,
        'hierarchical': CollaborationMode.HIERARCHICAL
    }
    
    orchestrator = CollaborationOrchestrator(
        mode=mode_map[mode.lower()],
        config_loader=config_loader
    )
    
    # Create agents based on collaboration mode
    if mode.lower() == 'hierarchical':
        # Hierarchical: Coordinator + Specialists
        agents = [
            CoordinatorAgent(config_loader),
            PlannerAgent(config_loader),
            CoderAgent(config_loader),
            TesterAgent(config_loader)
        ]
    elif mode.lower() == 'sequential':
        # Sequential: Planner -> Coder -> Tester -> Reviewer
        agents = [
            PlannerAgent(config_loader),
            CoderAgent(config_loader),
            TesterAgent(config_loader),
            ReviewerAgent(config_loader)
        ]
    else:  # parallel
        # Parallel: All specialists work simultaneously
        agents = [
            PlannerAgent(config_loader),
            CoderAgent(config_loader),
            TesterAgent(config_loader),
            ReviewerAgent(config_loader)
        ]
    
    # Register all agents
    for agent in agents:
        orchestrator.register_agent(agent)
    
    return orchestrator, agents
