"""
Tests for the ToolUsingAgent class.
"""
import unittest
from unittest.mock import MagicMock, patch
import json

from src.agents.tool_using_agent import ToolUsingAgent
from src.agents.base import ConfigLoader


class TestToolUsingAgent(unittest.TestCase):
    """Test cases for ToolUsingAgent"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_config_loader = MagicMock(spec=ConfigLoader)
        self.mock_config_loader.get_agent_config.return_value = {
            "persona_prompt": "You are a tool-using agent.",
            "model": "llama3.1:latest"
        }

    @patch('src.agents.base.LLMFactory')
    def test_tool_using_agent_initialization(self, mock_llm_factory):
        """Test that ToolUsingAgent initializes correctly"""
        agent = ToolUsingAgent(self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "ToolUsingAgent")
        self.assertIsNotNone(agent.tools)
        self.assertIn("WebSearch", agent.tools)
        self.assertIn("Calculator", agent.tools)

    @patch('src.agents.base.LLMFactory')
    def test_choose_tool_success(self, mock_llm_factory):
        """Test successful tool selection"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock LLM response with tool choice
        tool_choice = {
            "tool_name": "Calculator",
            "tool_params": "2 + 2"
        }
        mock_llm_inner.invoke.return_value = json.dumps(tool_choice)
        
        agent = ToolUsingAgent(self.mock_config_loader)
        result = agent._choose_tool("What is 2 + 2?")
        
        self.assertEqual(result["tool_name"], "Calculator")
        self.assertEqual(result["tool_params"], "2 + 2")

    @patch('src.agents.base.LLMFactory')
    def test_choose_tool_with_text_before_json(self, mock_llm_factory):
        """Test tool selection when LLM includes text before JSON"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock response with text before JSON
        tool_choice = {
            "tool_name": "WebSearch",
            "tool_params": "Python programming"
        }
        mock_llm_inner.invoke.return_value = f"I will use the search tool:\n{json.dumps(tool_choice)}"
        
        agent = ToolUsingAgent(self.mock_config_loader)
        result = agent._choose_tool("Tell me about Python")
        
        self.assertEqual(result["tool_name"], "WebSearch")

    @patch('src.agents.base.LLMFactory')
    def test_choose_tool_none_needed(self, mock_llm_factory):
        """Test when no tool is needed"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock response indicating no tool needed
        tool_choice = {
            "tool_name": "None",
            "tool_params": ""
        }
        mock_llm_inner.invoke.return_value = json.dumps(tool_choice)
        
        agent = ToolUsingAgent(self.mock_config_loader)
        result = agent._choose_tool("Hello!")
        
        self.assertEqual(result["tool_name"], "None")

    @patch('src.agents.base.LLMFactory')
    def test_choose_tool_invalid_json(self, mock_llm_factory):
        """Test tool selection with invalid JSON"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock invalid JSON response
        mock_llm_inner.invoke.return_value = "This is not valid JSON"
        
        agent = ToolUsingAgent(self.mock_config_loader)
        result = agent._choose_tool("Test prompt")
        
        self.assertEqual(result["tool_name"], "None")

    @patch('src.agents.base.LLMFactory')
    def test_choose_tool_no_json_object(self, mock_llm_factory):
        """Test tool selection when no JSON object found"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock response without JSON object
        mock_llm_inner.invoke.return_value = "I don't know which tool to use"
        
        agent = ToolUsingAgent(self.mock_config_loader)
        result = agent._choose_tool("Complex prompt")
        
        self.assertEqual(result["tool_name"], "None")

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_with_tool(self, mock_registry, mock_llm_factory):
        """Test run with tool execution"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock tool selection and synthesis
        tool_choice = {
            "tool_name": "Calculator",
            "tool_params": "2 + 2"
        }
        mock_llm_inner.invoke.side_effect = [
            json.dumps(tool_choice),  # First call for tool selection
            "The answer is 4"          # Second call for synthesis
        ]
        
        # Mock tool execution
        mock_tool = MagicMock()
        mock_tool.execute.return_value = "Result: 4"
        mock_registry.get.return_value = mock_tool
        
        agent = ToolUsingAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("What is 2 + 2?")
        
        self.assertEqual(result, "The answer is 4")
        mock_tool.execute.assert_called_once_with("2 + 2")

    @patch('src.agents.base.LLMFactory')
    def test_run_without_tool(self, mock_llm_factory):
        """Test run when no tool is needed"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock no tool needed
        tool_choice = {"tool_name": "None"}
        mock_llm_inner.invoke.side_effect = [
            json.dumps(tool_choice),
            "Hello! How can I help you?"
        ]
        
        agent = ToolUsingAgent(self.mock_config_loader)
        result = agent.run("Hello!")
        
        self.assertEqual(result, "Hello! How can I help you?")

    @patch('src.agents.base.LLMFactory')
    def test_run_tool_name_is_none_value(self, mock_llm_factory):
        """Test run when tool_name is explicitly None"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock tool_name as None
        tool_choice = {"tool_name": None}
        mock_llm_inner.invoke.side_effect = [
            json.dumps(tool_choice),
            "Direct response"
        ]
        
        agent = ToolUsingAgent(self.mock_config_loader)
        result = agent.run("Simple question")
        
        self.assertEqual(result, "Direct response")

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_tool_not_found(self, mock_registry, mock_llm_factory):
        """Test run when selected tool is not found"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock tool selection
        tool_choice = {
            "tool_name": "InvalidTool",
            "tool_params": "test"
        }
        mock_llm_inner.invoke.return_value = json.dumps(tool_choice)
        
        # Mock tool not found
        mock_registry.get.return_value = None
        
        agent = ToolUsingAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("Use invalid tool")
        
        self.assertIn("Error", result)
        self.assertIn("InvalidTool", result)

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_tool_execution_error(self, mock_registry, mock_llm_factory):
        """Test run when tool execution fails"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock tool selection
        tool_choice = {
            "tool_name": "Calculator",
            "tool_params": "1/0"
        }
        mock_llm_inner.invoke.return_value = json.dumps(tool_choice)
        
        # Mock tool that raises exception
        mock_tool = MagicMock()
        mock_tool.execute.side_effect = Exception("Division by zero")
        mock_registry.get.return_value = mock_tool
        
        agent = ToolUsingAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("Calculate 1/0")
        
        self.assertIn("Error", result)
        self.assertIn("Division by zero", result)

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_web_search_tool(self, mock_registry, mock_llm_factory):
        """Test run with web search tool"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock tool selection
        tool_choice = {
            "tool_name": "WebSearch",
            "tool_params": "Python programming language"
        }
        mock_llm_inner.invoke.side_effect = [
            json.dumps(tool_choice),
            "Python is a high-level programming language"
        ]
        
        # Mock web search tool
        mock_tool = MagicMock()
        mock_tool.execute.return_value = "Python is a popular programming language"
        mock_registry.get.return_value = mock_tool
        
        agent = ToolUsingAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("What is Python?")
        
        self.assertIn("Python", result)
        mock_tool.execute.assert_called_once_with("Python programming language")

    @patch('src.agents.base.LLMFactory')
    @patch('src.tools.TOOL_REGISTRY')
    def test_run_datetime_tool(self, mock_registry, mock_llm_factory):
        """Test run with datetime tool"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Mock tool selection
        tool_choice = {
            "tool_name": "DateTime",
            "tool_params": "what is today's date"
        }
        mock_llm_inner.invoke.side_effect = [
            json.dumps(tool_choice),
            "Today is October 13, 2025"
        ]
        
        # Mock datetime tool
        mock_tool = MagicMock()
        mock_tool.execute.return_value = "Today's date is Sunday, October 13, 2025"
        mock_registry.get.return_value = mock_tool
        
        agent = ToolUsingAgent(self.mock_config_loader)
        agent.tools = mock_registry
        
        result = agent.run("What is today's date?")
        
        self.assertIn("October", result)
        mock_tool.execute.assert_called_once()


if __name__ == '__main__':
    unittest.main()
