"""
Multi-Agent Collaboration Pattern Implementation

This module implements a sophisticated multi-agent collaboration system where
specialized agents work together to solve complex problems. Agents can collaborate
in three modes:
1. Sequential: Agents work one after another in a pipeline
2. Parallel: Agents work simultaneously on different aspects
3. Hierarchical: A coordinator agent manages and delegates to specialist agents
"""

from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field
from enum import Enum
import json

from .base import BaseAgent, ConfigLoader, Verdict
from src.llm_evaluation import LLMFactory
from src.tools import TOOL_REGISTRY


class CollaborationMode(Enum):
    """Defines how agents collaborate in the system."""
    SEQUENTIAL = "sequential"  # Agents work in order, each using previous output
    PARALLEL = "parallel"      # Agents work simultaneously on the same input
    HIERARCHICAL = "hierarchical"  # Coordinator delegates to specialists


@dataclass
class AgentTask:
    """Represents a task assigned to an agent."""
    agent_role: str
    description: str
    input_data: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    task_id: str = ""


@dataclass
class AgentResult:
    """Result from an agent's work."""
    agent_role: str
    task_id: str
    success: bool
    output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class CollaborationAgent(BaseAgent):
    """
    Base class for agents participating in multi-agent collaboration.
    Each agent has a specialized role and can contribute to a larger goal.
    """
    
    def __init__(self, agent_name: str, role: str, config_loader: ConfigLoader):
        super().__init__(agent_name, config_loader)
        self.role = role
        self.collaboration_history: List[AgentResult] = []
    
    def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Execute a specific task assigned to this agent.
        
        Args:
            task: The task to execute
            
        Returns:
            AgentResult containing the outcome
        """
        try:
            print(f"[{self.agent_name}] Executing task: {task.description}")
            
            # Prepare the prompt for the LLM
            prompt = self._prepare_task_prompt(task)
            
            # Execute using the LLM
            response = self.llm.llm.invoke(prompt)
            
            # Parse and validate the response
            output = self._parse_response(response, task)
            
            result = AgentResult(
                agent_role=self.role,
                task_id=task.task_id,
                success=True,
                output=output,
                metadata={
                    "agent_name": self.agent_name,
                    "response_length": len(str(response))
                }
            )
            
            self.collaboration_history.append(result)
            return result
            
        except Exception as e:
            error_result = AgentResult(
                agent_role=self.role,
                task_id=task.task_id,
                success=False,
                output=None,
                error=str(e)
            )
            self.collaboration_history.append(error_result)
            return error_result
    
    def _prepare_task_prompt(self, task: AgentTask) -> str:
        """Prepare the prompt for the LLM based on the task."""
        return f"""{self.persona}

Task: {task.description}

Input Data:
{json.dumps(task.input_data, indent=2)}

Please complete this task according to your role and expertise.
"""
    
    def _parse_response(self, response: str, task: AgentTask) -> Any:
        """Parse the LLM response into structured output."""
        # Default implementation - subclasses can override
        return response
    
    def run(self, case_data: Dict[str, Any]) -> Optional[Verdict]:
        """
        Standard BaseAgent interface - wraps execute_task for compatibility.
        """
        task = AgentTask(
            agent_role=self.role,
            description=f"Process case data for {self.role}",
            input_data=case_data,
            task_id=f"{self.role}_task"
        )
        result = self.execute_task(task)
        
        if result.success:
            return Verdict(
                judge_name=self.agent_name,
                score=1.0,
                verdict=str(result.output)
            )
        else:
            return Verdict(
                judge_name=self.agent_name,
                score=0.0,
                verdict=f"Error: {result.error}"
            )


class CollaborationOrchestrator:
    """
    Orchestrates collaboration between multiple specialized agents.
    Supports sequential, parallel, and hierarchical collaboration modes.
    """
    
    def __init__(self, mode: CollaborationMode, config_loader: ConfigLoader):
        self.mode = mode
        self.config_loader = config_loader
        self.agents: Dict[str, CollaborationAgent] = {}
        self.results: List[AgentResult] = []
    
    def register_agent(self, agent: CollaborationAgent):
        """Register an agent to participate in collaboration."""
        self.agents[agent.role] = agent
        print(f"[Orchestrator] Registered agent: {agent.agent_name} (role: {agent.role})")
    
    def collaborate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the collaboration based on the configured mode.
        
        Args:
            task: The overall task/problem to solve
            
        Returns:
            Final result after all agents have collaborated
        """
        print(f"\n{'='*70}")
        print(f"[Orchestrator] Starting {self.mode.value} collaboration")
        print(f"[Orchestrator] Task: {task.get('description', 'No description')}")
        print(f"{'='*70}\n")
        
        if self.mode == CollaborationMode.SEQUENTIAL:
            return self._sequential_collaboration(task)
        elif self.mode == CollaborationMode.PARALLEL:
            return self._parallel_collaboration(task)
        elif self.mode == CollaborationMode.HIERARCHICAL:
            return self._hierarchical_collaboration(task)
        else:
            raise ValueError(f"Unsupported collaboration mode: {self.mode}")
    
    def _sequential_collaboration(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sequential collaboration: Each agent builds on the previous agent's output.
        """
        print("[Orchestrator] Executing SEQUENTIAL collaboration...")
        
        current_data = task
        agent_order = list(self.agents.keys())
        
        for i, role in enumerate(agent_order):
            agent = self.agents[role]
            
            agent_task = AgentTask(
                agent_role=role,
                description=f"Step {i+1}: {role} processing",
                input_data=current_data,
                task_id=f"seq_task_{i+1}_{role}"
            )
            
            result = agent.execute_task(agent_task)
            self.results.append(result)
            
            if not result.success:
                print(f"[Orchestrator] Agent {role} failed. Stopping collaboration.")
                return {
                    "success": False,
                    "error": result.error,
                    "completed_steps": i,
                    "results": self.results
                }
            
            # Next agent receives previous agent's output
            current_data = {
                "previous_output": result.output,
                "original_task": task,
                "step": i + 1
            }
        
        print("[Orchestrator] Sequential collaboration completed successfully!\n")
        return {
            "success": True,
            "final_output": current_data["previous_output"],
            "all_results": self.results
        }
    
    def _parallel_collaboration(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parallel collaboration: All agents work on the same input simultaneously.
        """
        print("[Orchestrator] Executing PARALLEL collaboration...")
        
        parallel_results = []
        
        for role, agent in self.agents.items():
            agent_task = AgentTask(
                agent_role=role,
                description=f"{role} analysis",
                input_data=task,
                task_id=f"parallel_task_{role}"
            )
            
            result = agent.execute_task(agent_task)
            parallel_results.append(result)
            self.results.append(result)
        
        # Synthesize all parallel results
        synthesis = self._synthesize_parallel_results(parallel_results)
        
        print("[Orchestrator] Parallel collaboration completed successfully!\n")
        return {
            "success": True,
            "individual_results": parallel_results,
            "synthesis": synthesis,
            "all_results": self.results
        }
    
    def _hierarchical_collaboration(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hierarchical collaboration: A coordinator agent manages specialist agents.
        """
        print("[Orchestrator] Executing HIERARCHICAL collaboration...")
        
        # Find the coordinator agent (usually the first one registered)
        coordinator_role = list(self.agents.keys())[0]
        coordinator = self.agents[coordinator_role]
        specialist_roles = list(self.agents.keys())[1:]
        
        print(f"[Orchestrator] Coordinator: {coordinator.agent_name}")
        print(f"[Orchestrator] Specialists: {[self.agents[r].agent_name for r in specialist_roles]}")
        
        # Coordinator creates a plan
        coordinator_task = AgentTask(
            agent_role=coordinator_role,
            description="Create coordination plan for specialists",
            input_data=task,
            task_id="coordinator_planning"
        )
        
        coord_result = coordinator.execute_task(coordinator_task)
        self.results.append(coord_result)
        
        if not coord_result.success:
            return {
                "success": False,
                "error": "Coordinator failed to create plan",
                "results": self.results
            }
        
        # Specialists execute their parts
        specialist_results = []
        for role in specialist_roles:
            agent = self.agents[role]
            
            specialist_task = AgentTask(
                agent_role=role,
                description=f"{role} executing coordinator's plan",
                input_data={
                    "coordinator_plan": coord_result.output,
                    "original_task": task
                },
                task_id=f"specialist_task_{role}"
            )
            
            result = agent.execute_task(specialist_task)
            specialist_results.append(result)
            self.results.append(result)
        
        # Coordinator synthesizes specialist results
        synthesis_task = AgentTask(
            agent_role=coordinator_role,
            description="Synthesize specialist results",
            input_data={
                "specialist_results": [r.output for r in specialist_results],
                "original_task": task
            },
            task_id="coordinator_synthesis"
        )
        
        final_result = coordinator.execute_task(synthesis_task)
        self.results.append(final_result)
        
        print("[Orchestrator] Hierarchical collaboration completed successfully!\n")
        return {
            "success": True,
            "coordinator_plan": coord_result.output,
            "specialist_outputs": specialist_results,
            "final_synthesis": final_result.output,
            "all_results": self.results
        }
    
    def _synthesize_parallel_results(self, results: List[AgentResult]) -> str:
        """Synthesize multiple parallel results into a coherent summary."""
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return "All parallel tasks failed."
        
        synthesis = "Synthesis of Parallel Agent Results:\n\n"
        for result in successful_results:
            synthesis += f"- {result.agent_role}: {result.output}\n"
        
        return synthesis
    
    def get_collaboration_summary(self) -> Dict[str, Any]:
        """Get a summary of the collaboration session."""
        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        
        return {
            "mode": self.mode.value,
            "total_agents": len(self.agents),
            "total_tasks": len(self.results),
            "successful_tasks": successful,
            "failed_tasks": failed,
            "agents": list(self.agents.keys())
        }
