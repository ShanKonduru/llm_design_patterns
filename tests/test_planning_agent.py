"""
Tests for the PlanningAgent class.
"""
import unittest
from unittest.mock import MagicMock, patch, call
import json

from src.agents.planning_agent import PlanningAgent
from src.agents.base import ConfigLoader


class TestPlanningAgent(unittest.TestCase):
    """Test cases for PlanningAgent"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_config_loader = MagicMock(spec=ConfigLoader)
        self.mock_config_loader.get_agent_config.return_value = {
            "persona_prompt": "You are a planning agent.",
            "model": "llama3.1:latest"
        }

    @patch('src.agents.base.LLMFactory')
    def test_planning_agent_initialization(self, mock_llm_factory):
        """Test that PlanningAgent initializes correctly"""
        agent = PlanningAgent(self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "PlanningAgent")
        self.assertIsNotNone(agent.tools)
        self.assertIn("WebSearch", agent.tools)
        self.assertIn("Calculator", agent.tools)

    @patch('src.agents.base.LLMFactory')
    def test_create_plan_success(self, mock_llm_factory):
        """Test successful plan creation"""
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock LLM response with valid JSON array
        plan_json = [
            {"step": "Search for Python", "tool_name": "WebSearch", "tool_params": "Python programming"},
            {"step": "Calculate result", "tool_name": "Calculator", "tool_params": "2024 - 1991"}
        ]
        mock_llm_inner.invoke.return_value = json.dumps(plan_json)
        
        agent = PlanningAgent(self.mock_config_loader)
        plan = agent._create_plan("When was Python created?")
        
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0]["tool_name"], "WebSearch")
        self.assertEqual(plan[1]["tool_name"], "Calculator")

    @patch('src.agents.base.LLMFactory')
    def test_create_plan_with_text_before_json(self, mock_llm_factory):
        """Test plan creation when LLM includes text before JSON"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock LLM response with text before JSON
        plan_json = [
            {"step": "Search", "tool_name": "WebSearch", "tool_params": "test"}
        ]
        mock_llm_inner.invoke.return_value = f"Here's the plan:\n{json.dumps(plan_json)}"
        
        agent = PlanningAgent(self.mock_config_loader)
        plan = agent._create_plan("Test goal")
        
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["tool_name"], "WebSearch")

    @patch('src.agents.base.LLMFactory')
    def test_create_plan_invalid_json(self, mock_llm_factory):
        """Test plan creation with invalid JSON response"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock invalid JSON response
        mock_llm_inner.invoke.return_value = "This is not valid JSON"
        
        agent = PlanningAgent(self.mock_config_loader)
        plan = agent._create_plan("Test goal")
        
        self.assertEqual(plan, [])

    @patch('src.agents.base.LLMFactory')
    def test_create_plan_no_json_array(self, mock_llm_factory):
        """Test plan creation when no JSON array found"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock response without JSON array
        mock_llm_inner.invoke.return_value = "I cannot create a plan for that"
        
        agent = PlanningAgent(self.mock_config_loader)
        plan = agent._create_plan("Impossible goal")
        
        self.assertEqual(plan, [])

    @patch('src.agents.base.LLMFactory')
    def test_create_plan_invalid_step_structure(self, mock_llm_factory):
        """Test plan creation with invalid step structure"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock response with invalid step structure (missing required keys)
        invalid_plan = [
            {"step": "Search", "tool_name": "WebSearch"}  # Missing tool_params
        ]
        mock_llm_inner.invoke.return_value = json.dumps(invalid_plan)
        
        agent = PlanningAgent(self.mock_config_loader)
        plan = agent._create_plan("Test goal")
        
        self.assertEqual(plan, [])

    @patch('src.agents.base.LLMFactory')
    def test_create_plan_empty_list(self, mock_llm_factory):
        """Test plan creation when LLM returns empty list"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock response with empty list
        mock_llm_inner.invoke.return_value = "[]"
        
        agent = PlanningAgent(self.mock_config_loader)
        plan = agent._create_plan("Test goal")
        
        self.assertEqual(plan, [])

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_success(self, mock_registry, mock_llm_factory):
        """Test successful run with plan execution"""
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock plan creation
        plan_json = [
            {"step": "Calculate", "tool_name": "Calculator", "tool_params": "2 + 2"}
        ]
        mock_llm_inner.invoke.side_effect = [
            json.dumps(plan_json),  # First call for plan creation
            "The answer is 4"        # Second call for synthesis
        ]
        
        # Mock tool execution
        mock_tool = MagicMock()
        mock_tool.execute.return_value = "Result: 4"
        mock_registry.get.return_value = mock_tool
        
        agent = PlanningAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("What is 2 + 2?")
        
        self.assertEqual(result, "The answer is 4")
        mock_tool.execute.assert_called_once_with("2 + 2")

    @patch('src.agents.base.LLMFactory')
    def test_run_no_plan(self, mock_llm_factory):
        """Test run when no plan can be created"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock invalid plan
        mock_llm_inner.invoke.return_value = "Cannot create plan"
        
        agent = PlanningAgent(self.mock_config_loader)
        result = agent.run("Impossible goal")
        
        self.assertEqual(result, "I could not create a plan to achieve that goal.")

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_tool_not_found(self, mock_registry, mock_llm_factory):
        """Test run when tool is not found"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock plan with non-existent tool
        plan_json = [
            {"step": "Use invalid tool", "tool_name": "InvalidTool", "tool_params": "test"}
        ]
        mock_llm_inner.invoke.side_effect = [
            json.dumps(plan_json),
            "Could not complete task"
        ]
        
        mock_registry.get.return_value = None
        
        agent = PlanningAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("Test goal")
        
        self.assertEqual(result, "Could not complete task")

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_tool_execution_error(self, mock_registry, mock_llm_factory):
        """Test run when tool execution fails"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        plan_json = [
            {"step": "Calculate", "tool_name": "Calculator", "tool_params": "1/0"}
        ]
        mock_llm_inner.invoke.side_effect = [
            json.dumps(plan_json),
            "Error occurred"
        ]
        
        # Mock tool that raises exception
        mock_tool = MagicMock()
        mock_tool.execute.side_effect = Exception("Division by zero")
        mock_registry.get.return_value = mock_tool
        
        agent = PlanningAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("Calculate 1/0")
        
        self.assertEqual(result, "Error occurred")

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_multi_step_plan(self, mock_registry, mock_llm_factory):
        """Test run with multi-step plan"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Multi-step plan
        plan_json = [
            {"step": "Search", "tool_name": "WebSearch", "tool_params": "Python"},
            {"step": "Calculate", "tool_name": "Calculator", "tool_params": "2024 - 1991"}
        ]
        mock_llm_inner.invoke.side_effect = [
            json.dumps(plan_json),
            "Python was created in 1991, 33 years ago"
        ]
        
        # Mock tools
        mock_search_tool = MagicMock()
        mock_search_tool.execute.return_value = "Python was created in 1991"
        
        mock_calc_tool = MagicMock()
        mock_calc_tool.execute.return_value = "Result: 33"
        
        def get_tool(name):
            if name == "WebSearch":
                return mock_search_tool
            elif name == "Calculator":
                return mock_calc_tool
            return None
        
        mock_registry.get.side_effect = get_tool
        
        agent = PlanningAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("When was Python created and how old is it?")
        
        self.assertIn("33", result)
        mock_search_tool.execute.assert_called_once()
        mock_calc_tool.execute.assert_called_once()


if __name__ == '__main__':
    unittest.main()
