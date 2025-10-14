"""
Tests for the ReflectionAgent class (Self-Correction Pattern).
"""
import unittest
from unittest.mock import MagicMock, patch
import json

from src.agents.reflection_agent import ReflectionAgent
from src.agents.base import ConfigLoader


class TestReflectionAgent(unittest.TestCase):
    """Test cases for ReflectionAgent"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_config_loader = MagicMock(spec=ConfigLoader)
        self.mock_config_loader.get_agent_config.return_value = {
            "persona_prompt": "You are a meticulous content creator.",
            "model": "llama3.1:latest"
        }

    @patch('src.agents.base.LLMFactory')
    def test_reflection_agent_initialization(self, mock_llm_factory):
        """Test that ReflectionAgent initializes correctly"""
        agent = ReflectionAgent(self.mock_config_loader)
        
        self.assertEqual(agent.agent_name, "ReflectionAgent")
        self.assertEqual(agent.max_iterations, 3)
        self.assertIsNotNone(agent.llm)

    @patch('src.agents.base.LLMFactory')
    def test_reflection_agent_custom_max_iterations(self, mock_llm_factory):
        """Test ReflectionAgent with custom max iterations"""
        agent = ReflectionAgent(self.mock_config_loader, max_iterations=5)
        
        self.assertEqual(agent.max_iterations, 5)

    @patch('src.agents.base.LLMFactory')
    def test_generate_initial_response(self, mock_llm_factory):
        """Test initial response generation"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        mock_llm_inner.invoke.return_value = "Initial response to the task"
        
        agent = ReflectionAgent(self.mock_config_loader)
        response = agent._generate_initial_response("Write a test", "Context info")
        
        self.assertEqual(response, "Initial response to the task")
        mock_llm_inner.invoke.assert_called_once()

    @patch('src.agents.base.LLMFactory')
    def test_critique_response_success(self, mock_llm_factory):
        """Test successful response critique"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        critique_json = {
            "quality_score": 0.7,
            "issues_found": ["Minor grammar error", "Could be more detailed"],
            "suggestions": ["Fix grammar", "Add more examples"],
            "is_acceptable": False
        }
        mock_llm_inner.invoke.return_value = json.dumps(critique_json)
        
        agent = ReflectionAgent(self.mock_config_loader)
        critique = agent._critique_response("Task", "Response")
        
        self.assertEqual(critique["quality_score"], 0.7)
        self.assertEqual(len(critique["issues_found"]), 2)
        self.assertFalse(critique["is_acceptable"])

    @patch('src.agents.base.LLMFactory')
    def test_critique_response_with_text_before_json(self, mock_llm_factory):
        """Test critique when LLM includes text before JSON"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        critique_json = {
            "quality_score": 0.9,
            "issues_found": [],
            "suggestions": ["Great work!"],
            "is_acceptable": True
        }
        mock_llm_inner.invoke.return_value = f"Here's my critique:\n{json.dumps(critique_json)}"
        
        agent = ReflectionAgent(self.mock_config_loader)
        critique = agent._critique_response("Task", "Response")
        
        self.assertEqual(critique["quality_score"], 0.9)
        self.assertTrue(critique["is_acceptable"])

    @patch('src.agents.base.LLMFactory')
    def test_critique_response_invalid_json(self, mock_llm_factory):
        """Test critique with invalid JSON returns default"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        mock_llm_inner.invoke.return_value = "This is not valid JSON"
        
        agent = ReflectionAgent(self.mock_config_loader)
        critique = agent._critique_response("Task", "Response")
        
        # Should return default critique
        self.assertEqual(critique["quality_score"], 0.5)
        self.assertFalse(critique["is_acceptable"])

    @patch('src.agents.base.LLMFactory')
    def test_critique_response_incomplete_structure(self, mock_llm_factory):
        """Test critique with incomplete JSON structure"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Missing required keys
        incomplete_json = {"quality_score": 0.8}
        mock_llm_inner.invoke.return_value = json.dumps(incomplete_json)
        
        agent = ReflectionAgent(self.mock_config_loader)
        critique = agent._critique_response("Task", "Response")
        
        # Should return default critique
        self.assertEqual(critique["quality_score"], 0.5)

    @patch('src.agents.base.LLMFactory')
    def test_refine_response(self, mock_llm_factory):
        """Test response refinement"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        mock_llm_inner.invoke.return_value = "Refined and improved response"
        
        agent = ReflectionAgent(self.mock_config_loader)
        critique = {
            "quality_score": 0.6,
            "issues_found": ["Issue 1"],
            "suggestions": ["Suggestion 1"],
            "is_acceptable": False
        }
        
        refined = agent._refine_response("Task", "Original", critique)
        
        self.assertEqual(refined, "Refined and improved response")
        mock_llm_inner.invoke.assert_called_once()

    @patch('src.agents.base.LLMFactory')
    def test_run_meets_threshold_immediately(self, mock_llm_factory):
        """Test run when quality threshold is met immediately"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # High quality response from the start
        critique_json = {
            "quality_score": 0.95,
            "issues_found": [],
            "suggestions": ["Excellent work"],
            "is_acceptable": True
        }
        
        mock_llm_inner.invoke.side_effect = [
            "Perfect initial response",  # Initial generation
            json.dumps(critique_json),    # First critique
            json.dumps(critique_json)     # Final critique
        ]
        
        agent = ReflectionAgent(self.mock_config_loader)
        result = agent.run("Write perfect code", quality_threshold=0.9)
        
        self.assertEqual(result["iterations"], 1)
        self.assertEqual(result["final_response"], "Perfect initial response")
        self.assertGreaterEqual(result["final_quality_score"], 0.9)

    @patch('src.agents.base.LLMFactory')
    def test_run_reaches_max_iterations(self, mock_llm_factory):
        """Test run when max iterations is reached"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        # Low quality that never improves enough
        low_critique = {
            "quality_score": 0.5,
            "issues_found": ["Many issues"],
            "suggestions": ["Fix everything"],
            "is_acceptable": False
        }
        
        mock_llm_inner.invoke.side_effect = [
            "Initial response",           # Initial generation
            json.dumps(low_critique),     # Critique 1
            "Refined response 1",         # Refinement 1
            json.dumps(low_critique),     # Critique 2
            "Refined response 2",         # Refinement 2
            json.dumps(low_critique),     # Critique 3
            json.dumps(low_critique)      # Final critique
        ]
        
        agent = ReflectionAgent(self.mock_config_loader, max_iterations=3)
        result = agent.run("Difficult task", quality_threshold=0.9)
        
        self.assertEqual(result["iterations"], 3)
        self.assertEqual(result["final_response"], "Refined response 2")

    @patch('src.agents.base.LLMFactory')
    def test_run_gradual_improvement(self, mock_llm_factory):
        """Test run with gradual quality improvement"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        critique1 = {
            "quality_score": 0.5,
            "issues_found": ["Multiple issues"],
            "suggestions": ["Improve X"],
            "is_acceptable": False
        }
        critique2 = {
            "quality_score": 0.75,
            "issues_found": ["Minor issue"],
            "suggestions": ["Polish Y"],
            "is_acceptable": False
        }
        critique3 = {
            "quality_score": 0.92,
            "issues_found": [],
            "suggestions": ["Excellent"],
            "is_acceptable": True
        }
        
        mock_llm_inner.invoke.side_effect = [
            "Initial response",           # Initial generation
            json.dumps(critique1),        # Critique 1
            "Improved response",          # Refinement 1
            json.dumps(critique2),        # Critique 2
            "Polished response",          # Refinement 2
            json.dumps(critique3),        # Critique 3
            json.dumps(critique3)         # Final critique
        ]
        
        agent = ReflectionAgent(self.mock_config_loader)
        result = agent.run("Complex task", quality_threshold=0.9)
        
        self.assertEqual(result["iterations"], 3)
        self.assertGreaterEqual(result["final_quality_score"], 0.9)
        self.assertGreater(result["improvement"], 0)  # Should show improvement

    @patch('src.agents.base.LLMFactory')
    def test_run_with_context(self, mock_llm_factory):
        """Test run with context parameter"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        good_critique = {
            "quality_score": 0.95,
            "issues_found": [],
            "suggestions": ["Great"],
            "is_acceptable": True
        }
        
        mock_llm_inner.invoke.side_effect = [
            "Response with context",
            json.dumps(good_critique),
            json.dumps(good_critique)
        ]
        
        agent = ReflectionAgent(self.mock_config_loader)
        result = agent.run("Task", context="Important requirements")
        
        # Verify context was passed (check invoke was called with context)
        call_args = mock_llm_inner.invoke.call_args_list[0][0][0]
        self.assertIn("Important requirements", call_args)

    @patch('src.agents.base.LLMFactory')
    def test_run_without_context(self, mock_llm_factory):
        """Test run without context parameter"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        good_critique = {
            "quality_score": 0.95,
            "issues_found": [],
            "suggestions": ["Great"],
            "is_acceptable": True
        }
        
        mock_llm_inner.invoke.side_effect = [
            "Response without context",
            json.dumps(good_critique),
            json.dumps(good_critique)
        ]
        
        agent = ReflectionAgent(self.mock_config_loader)
        result = agent.run("Task")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["final_response"], "Response without context")

    @patch('src.agents.base.LLMFactory')
    def test_default_critique_structure(self, mock_llm_factory):
        """Test default critique has correct structure"""
        agent = ReflectionAgent(self.mock_config_loader)
        default = agent._default_critique()
        
        self.assertIn("quality_score", default)
        self.assertIn("issues_found", default)
        self.assertIn("suggestions", default)
        self.assertIn("is_acceptable", default)
        self.assertIsInstance(default["issues_found"], list)
        self.assertIsInstance(default["suggestions"], list)

    @patch('src.agents.base.LLMFactory')
    def test_result_contains_all_fields(self, mock_llm_factory):
        """Test that run result contains all expected fields"""
        mock_llm_instance = MagicMock()
        mock_llm_inner = MagicMock()
        mock_llm_instance.llm = mock_llm_inner
        mock_llm_factory.get_llm.return_value = mock_llm_instance
        
        critique = {
            "quality_score": 0.95,
            "issues_found": [],
            "suggestions": [],
            "is_acceptable": True
        }
        
        mock_llm_inner.invoke.side_effect = [
            "Response",
            json.dumps(critique),
            json.dumps(critique)
        ]
        
        agent = ReflectionAgent(self.mock_config_loader)
        result = agent.run("Task")
        
        # Verify all expected fields
        self.assertIn("final_response", result)
        self.assertIn("iterations", result)
        self.assertIn("critiques", result)
        self.assertIn("final_critique", result)
        self.assertIn("final_quality_score", result)
        self.assertIn("improvement", result)


if __name__ == '__main__':
    unittest.main()
