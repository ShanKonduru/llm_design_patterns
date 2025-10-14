"""
A module to define a collection of tools that can be used by LLM agents.
"""
import math
import datetime
import requests
from typing import Optional

class BaseTool:
    """Base class for all tools."""
    name: str = "Base Tool"
    description: str = "This is a base tool."

    def execute(self, params: str) -> str:
        raise NotImplementedError("Each tool must implement the execute method.")

class WebSearchTool(BaseTool):
    """A tool to search the web using DuckDuckGo."""
    name: str = "WebSearch"
    description: str = (
        "Searches the web for information on a given topic. "
        "Input should be a search query string."
    )

    def execute(self, query: str) -> str:
        """Performs a web search using DuckDuckGo's instant answer API."""
        print(f"--- Executing WebSearchTool with query: '{query}' ---")
        
        try:
            # Use DuckDuckGo's Instant Answer API (free, no API key required)
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Try to extract useful information from the response
            abstract = data.get("Abstract", "")
            if abstract:
                return f"Search result: {abstract}"
            
            # If no abstract, try the heading + related topics
            heading = data.get("Heading", "")
            related_topics = data.get("RelatedTopics", [])
            
            if heading and related_topics:
                results = [heading]
                for topic in related_topics[:3]:  # Get first 3 related topics
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append(topic["Text"])
                return "Search results:\n" + "\n- ".join(results)
            
            # If still nothing, return a message
            return f"No detailed information found for '{query}'. You may want to try a different search term or visit a search engine directly."
            
        except requests.exceptions.RequestException as e:
            return f"Error performing web search: {e}. The search service may be unavailable."
        except Exception as e:
            return f"Unexpected error during web search: {e}"

class CodeInterpreterTool(BaseTool):
    """A tool to execute Python code snippets."""
    name: str = "CodeInterpreter"
    description: str = (
        "Executes a single line of Python code and returns the result. "
        "Only simple expressions are allowed (e.g., '1 + 1', 'math.sqrt(256)')."
        "You have access to the 'math' and 'datetime' libraries."
    )

    def execute(self, code: str) -> str:
        """
        Executes the given Python code in a safe environment and returns the result.
        WARNING: Executing arbitrary code is dangerous. This is a simplified and risky example.
        A real implementation should use a sandboxed environment.
        """
        print(f"--- Executing CodeInterpreterTool with code: '{code}' ---")
        try:
            # Define the environment in which the code will be executed.
            # We are only allowing access to 'math' and 'datetime' for safety.
            allowed_globals = {"math": math, "datetime": datetime}
            result = eval(code, {"__builtins__": {}}, allowed_globals)
            return f"Result: {result}"
        except Exception as e:
            return f"Error executing code: {e}"

class CalculatorTool(BaseTool):
    """A tool to perform mathematical calculations."""
    name: str = "Calculator"
    description: str = (
        "Performs mathematical calculations. "
        "Input should be a mathematical expression as a string (e.g., '25 * 48', '(100 + 50) / 2', 'sqrt(144)', 'sin(3.14/2)'). "
        "Supports basic arithmetic (+, -, *, /, **, %), square root (sqrt), and trigonometric functions (sin, cos, tan). "
        "Use this for any numerical computation or math problem."
    )

    def execute(self, expression: str) -> str:
        """Evaluates a mathematical expression safely."""
        print(f"--- Executing CalculatorTool with expression: '{expression}' ---")
        try:
            # Clean up the expression
            expression = expression.strip()
            
            # Replace common math function names
            expression = expression.replace('sqrt', 'math.sqrt')
            expression = expression.replace('sin', 'math.sin')
            expression = expression.replace('cos', 'math.cos')
            expression = expression.replace('tan', 'math.tan')
            expression = expression.replace('log', 'math.log')
            expression = expression.replace('pi', 'math.pi')
            expression = expression.replace('e', 'math.e')
            
            # Safe evaluation with math module
            allowed_globals = {"math": math, "__builtins__": {}}
            result = eval(expression, allowed_globals)
            
            # Format the result nicely
            if isinstance(result, float):
                # Round to reasonable precision
                if result == int(result):
                    return f"Result: {int(result)}"
                else:
                    return f"Result: {result:.6f}".rstrip('0').rstrip('.')
            else:
                return f"Result: {result}"
                
        except ZeroDivisionError:
            return "Error: Division by zero is not allowed."
        except Exception as e:
            return f"Error evaluating expression: {e}. Please check your mathematical expression."

class DateTimeTool(BaseTool):
    """A tool to handle date and time queries."""
    name: str = "DateTime"
    description: str = (
        "Answers questions about dates and times. "
        "Can provide: current date/time, day of the week for a specific date, "
        "date arithmetic (days between dates, adding/subtracting days), "
        "timezone information. "
        "Input should be a clear question like 'what is today's date?', "
        "'what day of the week is Christmas 2025?', or 'how many days until New Year 2026?'"
    )

    def execute(self, query: str) -> str:
        """Processes date/time queries."""
        print(f"--- Executing DateTimeTool with query: '{query}' ---")
        try:
            query_lower = query.lower().strip()
            
            # Get current date and time
            now = datetime.datetime.now()
            today = datetime.date.today()
            
            # Handle various types of queries
            if any(keyword in query_lower for keyword in ["today", "current date", "what is the date", "today's date"]):
                return f"Today's date is {today.strftime('%A, %B %d, %Y')}"
            
            elif any(keyword in query_lower for keyword in ["current time", "what time", "time now"]):
                return f"The current time is {now.strftime('%I:%M:%S %p')}"
            
            elif any(keyword in query_lower for keyword in ["day of week", "what day", "which day"]):
                # Try to extract a date from the query
                # Look for patterns like "December 25, 2025" or "2025-12-25"
                import re
                
                # Try to find year
                year_match = re.search(r'\b(20\d{2})\b', query)
                if year_match:
                    year = int(year_match.group(1))
                    
                    # Try to find month
                    months = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4,
                        'may': 5, 'june': 6, 'july': 7, 'august': 8,
                        'september': 9, 'october': 10, 'november': 11, 'december': 12,
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    
                    month = None
                    for month_name, month_num in months.items():
                        if month_name in query_lower:
                            month = month_num
                            break
                    
                    # Try to find day
                    day_match = re.search(r'\b(\d{1,2})\b', query)
                    day = int(day_match.group(1)) if day_match else 1
                    
                    if month:
                        target_date = datetime.date(year, month, day)
                        day_name = target_date.strftime('%A')
                        return f"{target_date.strftime('%B %d, %Y')} is a {day_name}"
                
                return "Please specify a date in the format like 'December 25, 2025' or provide month and year."
            
            elif any(keyword in query_lower for keyword in ["how many days", "days until", "days between"]):
                # Try to extract a future date
                import re
                year_match = re.search(r'\b(20\d{2})\b', query)
                
                if year_match:
                    year = int(year_match.group(1))
                    
                    months = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4,
                        'may': 5, 'june': 6, 'july': 7, 'august': 8,
                        'september': 9, 'october': 10, 'november': 11, 'december': 12,
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    
                    month = None
                    for month_name, month_num in months.items():
                        if month_name in query_lower:
                            month = month_num
                            break
                    
                    day_match = re.search(r'\b(\d{1,2})\b', query)
                    day = int(day_match.group(1)) if day_match else 1
                    
                    if month:
                        target_date = datetime.date(year, month, day)
                        delta = target_date - today
                        
                        if delta.days > 0:
                            return f"There are {delta.days} days until {target_date.strftime('%B %d, %Y')}"
                        elif delta.days < 0:
                            return f"That date was {abs(delta.days)} days ago"
                        else:
                            return "That date is today!"
                
                return "Please specify a target date with month and year (e.g., 'New Year 2026' or 'December 31, 2025')"
            
            else:
                # Default: return current date and time
                return f"Current date and time: {now.strftime('%A, %B %d, %Y at %I:%M:%S %p')}"
                
        except Exception as e:
            return f"Error processing date/time query: {e}. Please try rephrasing your question."

# A dictionary to easily access tools by name
TOOL_REGISTRY = {
    "WebSearch": WebSearchTool(),
    "CodeInterpreter": CodeInterpreterTool(),
    "Calculator": CalculatorTool(),
    "DateTime": DateTimeTool(),
}
