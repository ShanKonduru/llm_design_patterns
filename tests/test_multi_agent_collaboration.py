"""
Tests for Multi-Agent Collaboration Pattern

Tests the collaboration orchestrator and specialized software engineering agents.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.collaboration_agent import (
    CollaborationAgent,
    CollaborationOrchestrator,
    CollaborationMode,
    AgentTask,
    AgentResult
)
from src.agents.software_team import (
    PlannerAgent,
    CoderAgent,
    TesterAgent,
    ReviewerAgent,
    CoordinatorAgent,
    create_software_team
)
from src.agents.config import ConfigLoader


class TestCollaborationAgent(unittest.TestCase):
    """Test the base CollaborationAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config_loader = Mock(spec=ConfigLoader)
        self.mock_config_loader.get_agent_config.return_value = {
            'model': 'llama3.1:latest',
            'persona_prompt': 'You are a test agent.'
        }
    
    @patch('src.agents.base.LLMFactory')
    def test_collaboration_agent_initialization(self, mock_llm_factory):
        """Test that CollaborationAgent initializes correctly."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = CollaborationAgent("TestAgent", "TestRole", self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "TestAgent")
        self.assertEqual(agent.role, "TestRole")
        self.assertEqual(len(agent.collaboration_history), 0)
    
    @patch('src.agents.base.LLMFactory')
    def test_execute_task_success(self, mock_llm_factory):
        """Test successful task execution."""
        mock_llm = Mock()
        mock_llm.llm.invoke.return_value = "Test response"
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = CollaborationAgent("TestAgent", "TestRole", self.mock_config_loader)
        
        task = AgentTask(
            agent_role="TestRole",
            description="Test task",
            input_data={"key": "value"},
            task_id="test_1"
        )
        
        result = agent.execute_task(task)
        
        self.assertTrue(result.success)
        self.assertEqual(result.agent_role, "TestRole")
        self.assertEqual(result.task_id, "test_1")
        self.assertIsNotNone(result.output)
        self.assertEqual(len(agent.collaboration_history), 1)
    
    @patch('src.agents.base.LLMFactory')
    def test_execute_task_failure(self, mock_llm_factory):
        """Test task execution with error."""
        # Set up the mock BEFORE creating the agent
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_inner.invoke.side_effect = Exception("Test error")
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Now create the agent - it will get the mocked LLM
        agent = CollaborationAgent("TestAgent", "TestRole", self.mock_config_loader)
        
        task = AgentTask(
            agent_role="TestRole",
            description="Test task",
            input_data={"key": "value"},
            task_id="test_1"
        )
        
        result = agent.execute_task(task)
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertIn("Test error", result.error)
        self.assertEqual(len(agent.collaboration_history), 1)


class TestCollaborationOrchestrator(unittest.TestCase):
    """Test the CollaborationOrchestrator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config_loader = Mock(spec=ConfigLoader)
        self.orchestrator = CollaborationOrchestrator(
            CollaborationMode.SEQUENTIAL,
            self.mock_config_loader
        )
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        self.assertEqual(self.orchestrator.mode, CollaborationMode.SEQUENTIAL)
        self.assertEqual(len(self.orchestrator.agents), 0)
        self.assertEqual(len(self.orchestrator.results), 0)
    
    @patch('src.agents.base.LLMFactory')
    def test_register_agent(self, mock_llm_factory):
        """Test agent registration."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        self.mock_config_loader.get_agent_config.return_value = {
            'model': 'llama3.1:latest',
            'persona_prompt': 'Test prompt'
        }
        
        agent = CollaborationAgent("TestAgent", "TestRole", self.mock_config_loader)
        self.orchestrator.register_agent(agent)
        
        self.assertEqual(len(self.orchestrator.agents), 1)
        self.assertIn("TestRole", self.orchestrator.agents)
    
    @patch('src.agents.base.LLMFactory')
    def test_sequential_collaboration(self, mock_llm_factory):
        """Test sequential collaboration mode."""
        mock_llm = Mock()
        mock_llm.llm.invoke.return_value = "Test output"
        mock_llm_factory.get_llm.return_value = mock_llm
        
        self.mock_config_loader.get_agent_config.return_value = {
            'model': 'llama3.1:latest',
            'persona_prompt': 'Test prompt'
        }
        
        # Create and register multiple agents
        agent1 = CollaborationAgent("Agent1", "Role1", self.mock_config_loader)
        agent2 = CollaborationAgent("Agent2", "Role2", self.mock_config_loader)
        
        self.orchestrator.register_agent(agent1)
        self.orchestrator.register_agent(agent2)
        
        task = {
            "description": "Test task",
            "requirements": "Test requirements"
        }
        
        result = self.orchestrator.collaborate(task)
        
        self.assertTrue(result["success"])
        self.assertIn("final_output", result)
        self.assertIn("all_results", result)
        self.assertEqual(len(result["all_results"]), 2)
    
    @patch('src.agents.base.LLMFactory')
    def test_parallel_collaboration(self, mock_llm_factory):
        """Test parallel collaboration mode."""
        mock_llm = Mock()
        mock_llm.llm.invoke.return_value = "Test output"
        mock_llm_factory.get_llm.return_value = mock_llm
        
        self.mock_config_loader.get_agent_config.return_value = {
            'model': 'llama3.1:latest',
            'persona_prompt': 'Test prompt'
        }
        
        orchestrator = CollaborationOrchestrator(
            CollaborationMode.PARALLEL,
            self.mock_config_loader
        )
        
        agent1 = CollaborationAgent("Agent1", "Role1", self.mock_config_loader)
        agent2 = CollaborationAgent("Agent2", "Role2", self.mock_config_loader)
        
        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2)
        
        task = {
            "description": "Test task",
            "requirements": "Test requirements"
        }
        
        result = orchestrator.collaborate(task)
        
        self.assertTrue(result["success"])
        self.assertIn("individual_results", result)
        self.assertIn("synthesis", result)
        self.assertEqual(len(result["individual_results"]), 2)
    
    def test_get_collaboration_summary(self):
        """Test collaboration summary generation."""
        summary = self.orchestrator.get_collaboration_summary()
        
        self.assertIn("mode", summary)
        self.assertIn("total_agents", summary)
        self.assertIn("total_tasks", summary)
        self.assertEqual(summary["mode"], "sequential")


class TestSoftwareTeamAgents(unittest.TestCase):
    """Test specialized software engineering agents."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config_loader = Mock(spec=ConfigLoader)
        self.mock_config_loader.get_agent_config.return_value = {
            'model': 'llama3.1:latest',
            'persona_prompt': 'Test persona'
        }
    
    @patch('src.agents.base.LLMFactory')
    def test_planner_agent_initialization(self, mock_llm_factory):
        """Test PlannerAgent initialization."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = PlannerAgent(self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "PlannerAgent")
        self.assertEqual(agent.role, "Planner")
    
    @patch('src.agents.base.LLMFactory')
    def test_coder_agent_initialization(self, mock_llm_factory):
        """Test CoderAgent initialization."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = CoderAgent(self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "CoderAgent")
        self.assertEqual(agent.role, "Coder")
    
    @patch('src.agents.base.LLMFactory')
    def test_tester_agent_initialization(self, mock_llm_factory):
        """Test TesterAgent initialization."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = TesterAgent(self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "TesterAgent")
        self.assertEqual(agent.role, "Tester")
    
    @patch('src.agents.base.LLMFactory')
    def test_reviewer_agent_initialization(self, mock_llm_factory):
        """Test ReviewerAgent initialization."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = ReviewerAgent(self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "ReviewerAgent")
        self.assertEqual(agent.role, "Reviewer")
    
    @patch('src.agents.base.LLMFactory')
    def test_coordinator_agent_initialization(self, mock_llm_factory):
        """Test CoordinatorAgent initialization."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = CoordinatorAgent(self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "CoordinatorAgent")
        self.assertEqual(agent.role, "Coordinator")
    
    @patch('src.agents.base.LLMFactory')
    def test_planner_task_execution(self, mock_llm_factory):
        """Test PlannerAgent task execution."""
        mock_llm = Mock()
        mock_llm.llm.invoke.return_value = """
ARCHITECTURE:
Modular design with separate components

COMPONENTS:
1. Main module
2. Helper functions

STEPS:
1. Define requirements
2. Implement core logic
3. Add error handling

CONSIDERATIONS:
- Performance
- Maintainability
"""
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = PlannerAgent(self.mock_config_loader)
        
        task = AgentTask(
            agent_role="Planner",
            description="Create plan",
            input_data={"requirements": "Build a calculator"},
            task_id="plan_1"
        )
        
        result = agent.execute_task(task)
        
        self.assertTrue(result.success)
        self.assertIn("plan", result.output)
        self.assertIn("requirements", result.output)
    
    @patch('src.agents.base.LLMFactory')
    def test_coder_parse_response_with_code_blocks(self, mock_llm_factory):
        """Test CoderAgent parsing code blocks."""
        mock_llm = Mock()
        response_with_code = """Here's the implementation:

```python
def add(a, b):
    return a + b
```

This function adds two numbers."""
        mock_llm.llm.invoke.return_value = response_with_code
        mock_llm_factory.get_llm.return_value = mock_llm
        
        agent = CoderAgent(self.mock_config_loader)
        
        task = AgentTask(
            agent_role="Coder",
            description="Write code",
            input_data={"requirements": "Add function"},
            task_id="code_1"
        )
        
        result = agent.execute_task(task)
        
        self.assertTrue(result.success)
        self.assertIn("code", result.output)
        self.assertIn("code_blocks", result.output)
        # Verify we extracted the code block correctly
        self.assertGreaterEqual(len(result.output["code_blocks"]), 1)
        if len(result.output["code_blocks"]) > 0:
            self.assertIn("def add", result.output["code_blocks"][0])
    
    @patch('src.agents.base.LLMFactory')
    def test_reviewer_approval_status_detection(self, mock_llm_factory):
        """Test ReviewerAgent detecting approval status."""
        # Setup mock structure properly
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Test APPROVED status (create new agent each time to avoid state issues)
        mock_llm_inner.invoke.return_value = "The code is excellent. I hereby grant my APPROVED status."
        agent = ReviewerAgent(self.mock_config_loader)
        task = AgentTask(
            agent_role="Reviewer",
            description="Review code",
            input_data={"code": "test code"},
            task_id="review_1"
        )
        result = agent.execute_task(task)
        self.assertEqual(result.output["approval_status"], "APPROVED")
        
        # Test NEEDS_CHANGES status (new agent)
        mock_llm_inner.invoke.return_value = "The code NEEDS_CHANGES for improvement."
        agent2 = ReviewerAgent(self.mock_config_loader)
        task2 = AgentTask(
            agent_role="Reviewer",
            description="Review code",
            input_data={"code": "test code"},
            task_id="review_2"
        )
        result2 = agent2.execute_task(task2)
        self.assertEqual(result2.output["approval_status"], "NEEDS_CHANGES")
        
        # Test REJECTED status (new agent)
        mock_llm_inner.invoke.return_value = "The code is poor quality. REJECTED."
        agent3 = ReviewerAgent(self.mock_config_loader)
        task3 = AgentTask(
            agent_role="Reviewer",
            description="Review code",
            input_data={"code": "test code"},
            task_id="review_3"
        )
        result3 = agent3.execute_task(task3)
        self.assertEqual(result3.output["approval_status"], "REJECTED")


class TestSoftwareTeamFactory(unittest.TestCase):
    """Test the software team factory function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config_loader = Mock(spec=ConfigLoader)
        self.mock_config_loader.get_agent_config.return_value = {
            'model': 'llama3.1:latest',
            'persona_prompt': 'Test persona'
        }
    
    @patch('src.agents.base.LLMFactory')
    def test_create_sequential_team(self, mock_llm_factory):
        """Test creating a sequential software team."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        orchestrator, agents = create_software_team('sequential', self.mock_config_loader)
        
        self.assertEqual(orchestrator.mode, CollaborationMode.SEQUENTIAL)
        self.assertEqual(len(agents), 4)
        self.assertEqual(len(orchestrator.agents), 4)
        
        # Verify agent types in sequential order
        self.assertIsInstance(agents[0], PlannerAgent)
        self.assertIsInstance(agents[1], CoderAgent)
        self.assertIsInstance(agents[2], TesterAgent)
        self.assertIsInstance(agents[3], ReviewerAgent)
    
    @patch('src.agents.base.LLMFactory')
    def test_create_parallel_team(self, mock_llm_factory):
        """Test creating a parallel software team."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        orchestrator, agents = create_software_team('parallel', self.mock_config_loader)
        
        self.assertEqual(orchestrator.mode, CollaborationMode.PARALLEL)
        self.assertEqual(len(agents), 4)
        self.assertEqual(len(orchestrator.agents), 4)
    
    @patch('src.agents.base.LLMFactory')
    def test_create_hierarchical_team(self, mock_llm_factory):
        """Test creating a hierarchical software team."""
        mock_llm = Mock()
        mock_llm_factory.get_llm.return_value = mock_llm
        
        orchestrator, agents = create_software_team('hierarchical', self.mock_config_loader)
        
        self.assertEqual(orchestrator.mode, CollaborationMode.HIERARCHICAL)
        self.assertEqual(len(agents), 4)
        self.assertEqual(len(orchestrator.agents), 4)
        
        # Verify coordinator is first in hierarchical mode
        self.assertIsInstance(agents[0], CoordinatorAgent)


class TestAgentTaskAndResult(unittest.TestCase):
    """Test AgentTask and AgentResult dataclasses."""
    
    def test_agent_task_creation(self):
        """Test AgentTask creation."""
        task = AgentTask(
            agent_role="TestRole",
            description="Test description",
            input_data={"key": "value"},
            dependencies=["task1", "task2"],
            task_id="test_id"
        )
        
        self.assertEqual(task.agent_role, "TestRole")
        self.assertEqual(task.description, "Test description")
        self.assertEqual(task.input_data, {"key": "value"})
        self.assertEqual(task.dependencies, ["task1", "task2"])
        self.assertEqual(task.task_id, "test_id")
    
    def test_agent_result_creation(self):
        """Test AgentResult creation."""
        result = AgentResult(
            agent_role="TestRole",
            task_id="test_id",
            success=True,
            output="Test output",
            metadata={"key": "value"},
            error=None
        )
        
        self.assertEqual(result.agent_role, "TestRole")
        self.assertEqual(result.task_id, "test_id")
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Test output")
        self.assertEqual(result.metadata, {"key": "value"})
        self.assertIsNone(result.error)


if __name__ == '__main__':
    unittest.main()
