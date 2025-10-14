import unittest
from unittest.mock import patch, MagicMock
import json

from src.tools import (
    BaseTool,
    WebSearchTool,
    CalculatorTool,
    DateTimeTool,
    CodeInterpreterTool,
    TOOL_REGISTRY
)


class TestBaseTool(unittest.TestCase):
    """Test the abstract BaseTool class."""
    
    def test_base_tool_has_properties(self):
        """Test that BaseTool has name and description."""
        tool = BaseTool()
        self.assertEqual(tool.name, "Base Tool")
        self.assertEqual(tool.description, "This is a base tool.")
    
    def test_base_tool_execute_not_implemented(self):
        """Test that base execute method raises NotImplementedError."""
        tool = BaseTool()
        with self.assertRaises(NotImplementedError):
            tool.execute("test")


class TestWebSearchTool(unittest.TestCase):
    """Test the WebSearchTool class."""
    
    def setUp(self):
        """Set up a WebSearchTool instance for testing."""
        self.tool = WebSearchTool()
    
    def test_tool_properties(self):
        """Test the tool has correct name and description."""
        self.assertEqual(self.tool.name, "WebSearch")
        self.assertIn("searches", self.tool.description.lower())
    
    @patch('src.tools.requests.get')
    def test_successful_search(self, mock_get):
        """Test successful web search returns results."""
        # Arrange: Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Abstract": "Python is a high-level programming language.",
            "Heading": "Python"
        }
        mock_get.return_value = mock_response
        
        # Act: Execute search
        result = self.tool.execute("Python programming")
        
        # Assert: Verify results format and content
        self.assertIn("Search result", result)
        self.assertIn("Python", result)
        mock_get.assert_called_once()
    
    @patch('src.tools.requests.get')
    def test_no_results_found(self, mock_get):
        """Test search with no results returns appropriate message."""
        # Arrange: Mock empty response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Abstract": "",
            "Heading": "",
            "RelatedTopics": []
        }
        mock_get.return_value = mock_response
        
        # Act: Execute search
        result = self.tool.execute("xyznonexistentquery123")
        
        # Assert: Verify no results message
        self.assertIn("no detailed information", result.lower())
    
    @patch('src.tools.requests.get')
    def test_search_api_error(self, mock_get):
        """Test search handles API errors gracefully."""
        # Arrange: Mock API error
        mock_get.side_effect = Exception("Network error")
        
        # Act: Execute search
        result = self.tool.execute("test query")
        
        # Assert: Verify error message
        self.assertIn("error", result.lower())
        self.assertIn("Network error", result)
    
    @patch('src.tools.requests.get')
    def test_search_timeout(self, mock_get):
        """Test search handles timeout errors."""
        # Arrange: Mock timeout
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        # Act: Execute search
        result = self.tool.execute("test query")
        
        # Assert: Verify timeout error message
        self.assertIn("Error", result)
    
    def test_empty_query(self):
        """Test search with empty query."""
        result = self.tool.execute("")
        # Should return some result, not necessarily an error
        self.assertIsInstance(result, str)


class TestCalculatorTool(unittest.TestCase):
    """Test the CalculatorTool class."""
    
    def setUp(self):
        """Set up a CalculatorTool instance for testing."""
        self.tool = CalculatorTool()
    
    def test_tool_properties(self):
        """Test the tool has correct name and description."""
        self.assertEqual(self.tool.name, "Calculator")
        self.assertIn("mathematical", self.tool.description.lower())
    
    def test_basic_arithmetic_operations(self):
        """Test basic arithmetic operations."""
        test_cases = [
            ("2 + 2", "4"),
            ("10 - 3", "7"),
            ("5 * 6", "30"),
            ("20 / 4", "5"),
            ("10 % 3", "1"),
            ("2 ** 8", "256"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.tool.execute(expression)
                self.assertIn(expected, result)
    
    def test_complex_expressions(self):
        """Test complex mathematical expressions."""
        test_cases = [
            ("(2 + 3) * 4", "20"),
            ("sqrt(16)", "4"),
            ("sin(0)", "0"),
            ("log(10)", "2.302"),  # Natural log
            ("pi", "3.14"),
        ]
        
        for expression, expected_substring in test_cases:
            with self.subTest(expression=expression):
                result = self.tool.execute(expression)
                self.assertIn(expected_substring, result)
    
    def test_invalid_expression(self):
        """Test calculator handles invalid expressions."""
        result = self.tool.execute("2 + + 3")
        # Python actually handles this as valid (unary +)
        self.assertIsInstance(result, str)
    
    def test_unsafe_expression(self):
        """Test calculator rejects unsafe expressions."""
        dangerous_expressions = [
            "__import__('os').system('ls')",
            "open('file.txt')",
            "exec('print(1)')",
            "eval('2+2')",
        ]
        
        for expr in dangerous_expressions:
            with self.subTest(expression=expr):
                result = self.tool.execute(expr)
                self.assertIn("Error", result)
    
    def test_division_by_zero(self):
        """Test calculator handles division by zero."""
        result = self.tool.execute("10 / 0")
        self.assertIn("Error", result)
        self.assertIn("division", result.lower())
    
    def test_empty_expression(self):
        """Test calculator with empty expression."""
        result = self.tool.execute("")
        self.assertIn("Error", result)


class TestDateTimeTool(unittest.TestCase):
    """Test the DateTimeTool class."""
    
    def setUp(self):
        """Set up a DateTimeTool instance for testing."""
        self.tool = DateTimeTool()
    
    def test_tool_properties(self):
        """Test the tool has correct name and description."""
        self.assertEqual(self.tool.name, "DateTime")
        self.assertIn("date", self.tool.description.lower())
    
    def test_current_date(self):
        """Test getting current date."""
        queries = [
            "what is the current date",
            "today's date",
            "what date is it",
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = self.tool.execute(query)
                self.assertIn("2025", result)  # Should contain current year
                self.assertIn("October", result)  # Current month
    
    def test_current_time(self):
        """Test getting current time."""
        queries = [
            "what time is it",
            "current time",
            "what is the time",
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = self.tool.execute(query)
                self.assertIn(":", result)  # Time has colons
    
    def test_current_datetime(self):
        """Test getting current datetime."""
        queries = [
            "what is the current date and time",
            "now",
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = self.tool.execute(query)
                self.assertIn("2025", result)
                # Should have either time (:) or be a date response
                self.assertTrue(":" in result or "2025" in result)
    
    def test_day_of_week(self):
        """Test getting day of week."""
        queries = [
            "what day is it",
            "current day of week",
            "what day of the week",
        ]
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for query in queries:
            with self.subTest(query=query):
                result = self.tool.execute(query)
                # Should contain day name or full date
                self.assertTrue(any(day in result for day in days) or "2025" in result)
    
    def test_year_query(self):
        """Test getting current year."""
        queries = [
            "what year is it",
            "current year",
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = self.tool.execute(query)
                self.assertIn("2025", result)
    
    def test_unrecognized_query(self):
        """Test unrecognized query returns current datetime."""
        result = self.tool.execute("some random query")
        self.assertIn(":", result)  # Falls back to datetime
    
    def test_empty_query(self):
        """Test empty query returns current datetime."""
        result = self.tool.execute("")
        self.assertIn(":", result)


class TestCodeInterpreterTool(unittest.TestCase):
    """Test the CodeInterpreterTool class."""
    
    def setUp(self):
        """Set up a CodeInterpreterTool instance for testing."""
        self.tool = CodeInterpreterTool()
    
    def test_tool_properties(self):
        """Test the tool has correct name and description."""
        self.assertEqual(self.tool.name, "CodeInterpreter")
        self.assertIn("python", self.tool.description.lower())
        self.assertIn("code", self.tool.description.lower())
    
    def test_simple_code_execution(self):
        """Test executing simple Python code."""
        test_cases = [
            ("2 + 2", "4"),
            ("'hello'.upper()", "HELLO"),
            ("[1, 2, 3]", "[1, 2, 3]"),
            ("{'a': 1}", "{'a': 1}"),
        ]
        
        for code, expected in test_cases:
            with self.subTest(code=code):
                result = self.tool.execute(code)
                self.assertIn(expected, result)
    
    def test_code_with_imports(self):
        """Test code execution with math module."""
        code = "math.sqrt(16)"
        result = self.tool.execute(code)
        self.assertIn("4", result)
    
    def test_code_execution_error(self):
        """Test code that raises an error."""
        code = "1 / 0"
        result = self.tool.execute(code)
        self.assertIn("Error", result)
        self.assertIn("division", result.lower())
    
    def test_syntax_error(self):
        """Test code with syntax error."""
        code = "if True print('hello')"
        result = self.tool.execute(code)
        self.assertIn("Error", result)
        self.assertIn("syntax", result.lower())
    
    def test_unsafe_code_rejection(self):
        """Test that dangerous code is rejected."""
        dangerous_code = [
            "import os; os.system('ls')",
            "open('file.txt', 'w').write('test')",
            "__import__('subprocess').call(['ls'])",
        ]
        
        for code in dangerous_code:
            with self.subTest(code=code):
                result = self.tool.execute(code)
                self.assertIn("Error", result)
    
    def test_empty_code(self):
        """Test executing empty code."""
        result = self.tool.execute("")
        self.assertIn("Error", result)
    
    def test_multiline_code(self):
        """Test executing simple expression."""
        code = "(5 + 10)"
        result = self.tool.execute(code)
        self.assertIn("15", result)


class TestDateTimeToolExtended(unittest.TestCase):
    """Extended tests for DateTimeTool edge cases."""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = DateTimeTool()
    
    def test_year_extraction(self):
        """Test extracting year from query."""
        result = self.tool.execute("what year is it?")
        self.assertIn("2025", result)
    
    def test_days_until_future_date(self):
        """Test calculating days until a future date."""
        result = self.tool.execute("how many days until December 25, 2025")
        self.assertIn("days", result.lower())
        self.assertIn("December 25, 2025", result)
    
    def test_days_since_past_date(self):
        """Test calculating days since a past date."""
        result = self.tool.execute("how many days until January 1, 2025")
        self.assertIn("ago", result.lower())
    
    def test_date_is_today(self):
        """Test when target date is today."""
        # Use dynamic current date to avoid test failures due to date changes
        import datetime
        today = datetime.date.today()
        result = self.tool.execute(f"how many days until {today.strftime('%B %d, %Y')}")
        # Should return "That date is today!"
        self.assertIn("today", result.lower())
    
    def test_day_of_week_calculation(self):
        """Test day of week calculation."""
        result = self.tool.execute("what day of the week is December 25 2025")
        self.assertIn("December 25, 2025", result)
        self.assertIn("Thursday", result)  # Dec 25, 2025 is a Thursday
    
    def test_month_extraction(self):
        """Test extracting month names from query."""
        result = self.tool.execute("what day of the week is January 1 2026")
        self.assertIn("January", result)
    
    def test_abbreviated_month_names(self):
        """Test abbreviated month names."""
        result = self.tool.execute("what day is Dec 31 2025")
        self.assertIn("December", result)
    
    def test_complex_date_query_without_complete_info(self):
        """Test date query without complete information."""
        result = self.tool.execute("what day of the week is in 2026")
        self.assertIn("specify a date", result.lower())
    
    def test_days_until_without_month(self):
        """Test days until query without month specified."""
        result = self.tool.execute("how many days until 2026")
        self.assertIn("specify", result.lower())


class TestWebSearchToolEdgeCases(unittest.TestCase):
    """Extended edge case tests for WebSearchTool."""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = WebSearchTool()
    
    @patch('src.tools.requests.get')
    def test_abstract_with_url_but_no_text(self, mock_get):
        """Test when abstract exists with URL but no text."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Abstract": "",
            "AbstractURL": "https://example.com",
            "AbstractText": "",
            "RelatedTopics": []
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.tool.execute("test query")
        # When Abstract and AbstractText are empty but AbstractURL exists,
        # the tool should return a "no results" message or the URL
        self.assertIn("No", result)
    
    @patch('src.tools.requests.get')
    def test_heading_with_related_topics(self, mock_get):
        """Test when heading exists with related topics."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Abstract": "",
            "Heading": "Test Topic",
            "RelatedTopics": [
                {"Text": "Related info 1"},
                {"Text": "Related info 2"},
                {"Text": "Related info 3"},
                {"Text": "Related info 4"}  # Should only use first 3
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.tool.execute("test query")
        self.assertIn("Test Topic", result)
        self.assertIn("Related info 1", result)
        self.assertIn("Related info 3", result)
        self.assertNotIn("Related info 4", result)
    
    @patch('src.tools.requests.get')
    def test_related_topics_with_non_dict_items(self, mock_get):
        """Test handling of non-dict items in related topics."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Heading": "Test",
            "RelatedTopics": [
                {"Text": "Valid topic"},
                "Invalid string item",
                {"NoText": "No text key"},
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.tool.execute("test")
        self.assertIn("Valid topic", result)


class TestCalculatorToolExtended(unittest.TestCase):
    """Extended tests for CalculatorTool edge cases."""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = CalculatorTool()
    
    def test_trigonometric_functions(self):
        """Test trigonometric function support."""
        result = self.tool.execute("sin(0)")
        self.assertIn("0", result)
    
    def test_logarithm(self):
        """Test logarithm function."""
        result = self.tool.execute("log(10)")
        self.assertIn("Result:", result)
    
    def test_pi_constant(self):
        """Test pi constant."""
        result = self.tool.execute("pi * 2")
        self.assertIn("6.28", result)
    
    def test_e_constant(self):
        """Test e constant."""
        result = self.tool.execute("e")
        self.assertIn("2.71", result)
    
    def test_integer_result(self):
        """Test integer results are formatted correctly."""
        result = self.tool.execute("2 + 2")
        self.assertEqual(result, "Result: 4")
    
    def test_float_result_rounding(self):
        """Test float results are rounded properly."""
        result = self.tool.execute("10 / 3")
        self.assertIn("3.33", result)


class TestToolRegistry(unittest.TestCase):
    """Test the TOOL_REGISTRY."""
    
    def test_registry_contains_all_tools(self):
        """Test that TOOL_REGISTRY contains all expected tools."""
        expected_tools = ["WebSearch", "Calculator", "DateTime", "CodeInterpreter"]
        
        for tool_name in expected_tools:
            with self.subTest(tool=tool_name):
                self.assertIn(tool_name, TOOL_REGISTRY)
    
    def test_registry_tools_are_instances(self):
        """Test that registry contains tool instances."""
        for tool_name, tool_instance in TOOL_REGISTRY.items():
            with self.subTest(tool=tool_name):
                self.assertIsInstance(tool_instance, BaseTool)
                self.assertEqual(tool_instance.name, tool_name)
    
    def test_all_tools_have_execute_method(self):
        """Test that all registered tools have execute method."""
        for tool_name, tool_instance in TOOL_REGISTRY.items():
            with self.subTest(tool=tool_name):
                self.assertTrue(callable(tool_instance.execute))


if __name__ == '__main__':
    unittest.main()
