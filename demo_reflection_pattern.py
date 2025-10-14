"""
Demo: Reflection/Self-Correction Pattern

This demo shows how the ReflectionAgent iteratively improves its output
through self-critique and refinement.

Use Cases Demonstrated:
1. Code Generation with Self-Debugging
2. High-Quality Content Generation
3. Technical Documentation Writing
"""

from src.agents import ReflectionAgent, ConfigLoader
import json


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_critique(critique: dict, iteration: int):
    """Print formatted critique information"""
    print(f"\n--- Critique {iteration} ---")
    print(f"Quality Score: {critique['quality_score']:.2f}")
    print(f"Is Acceptable: {critique['is_acceptable']}")
    print(f"\nIssues Found ({len(critique['issues_found'])}):")
    for issue in critique['issues_found']:
        print(f"  • {issue}")
    print(f"\nSuggestions ({len(critique['suggestions'])}):")
    for suggestion in critique['suggestions']:
        print(f"  • {suggestion}")


def demo_code_generation():
    """Demonstrate self-correcting code generation"""
    print_section("Demo 1: Code Generation with Self-Debugging")
    
    config_loader = ConfigLoader("agents.json")
    agent = ReflectionAgent(config_loader, max_iterations=3)
    
    task = """
    Write a Python function that calculates the factorial of a number.
    The function should:
    - Handle edge cases (0, 1, negative numbers)
    - Include error handling
    - Have proper docstring
    - Be efficient
    """
    
    context = """
    Requirements:
    - Use recursion or iteration (your choice)
    - Raise ValueError for negative numbers
    - Return 1 for 0! and 1!
    - Include type hints
    - Follow PEP 8 style guidelines
    """
    
    result = agent.run(task, context, quality_threshold=0.85)
    
    # Print results
    print("\n" + "-" * 80)
    print("FINAL RESULT")
    print("-" * 80)
    print(f"\nTotal Iterations: {result['iterations']}")
    print(f"Final Quality Score: {result['final_quality_score']:.2f}")
    print(f"Improvement: {result['improvement']:+.2f}")
    
    print("\n" + "-" * 80)
    print("FINAL CODE:")
    print("-" * 80)
    print(result['final_response'])
    
    # Print all critiques
    print("\n" + "-" * 80)
    print("CRITIQUE HISTORY:")
    print("-" * 80)
    for i, critique in enumerate(result['critiques'], 1):
        print_critique(critique, i)


def demo_technical_documentation():
    """Demonstrate high-quality technical documentation generation"""
    print_section("Demo 2: Technical Documentation Writing")
    
    config_loader = ConfigLoader("agents.json")
    agent = ReflectionAgent(config_loader, max_iterations=3)
    
    task = """
    Write technical documentation explaining the Reflection/Self-Correction pattern
    in software design.
    """
    
    context = """
    Requirements:
    - Clear and concise explanation
    - Include a practical example
    - Mention benefits and trade-offs
    - Target audience: intermediate developers
    - Length: 2-3 paragraphs
    """
    
    result = agent.run(task, context, quality_threshold=0.88)
    
    # Print results
    print("\n" + "-" * 80)
    print("FINAL RESULT")
    print("-" * 80)
    print(f"\nTotal Iterations: {result['iterations']}")
    print(f"Final Quality Score: {result['final_quality_score']:.2f}")
    print(f"Improvement: {result['improvement']:+.2f}")
    
    print("\n" + "-" * 80)
    print("FINAL DOCUMENTATION:")
    print("-" * 80)
    print(result['final_response'])


def demo_legal_contract():
    """Demonstrate iterative refinement for legal content"""
    print_section("Demo 3: Legal Contract Generation")
    
    config_loader = ConfigLoader("agents.json")
    agent = ReflectionAgent(config_loader, max_iterations=4)
    
    task = """
    Draft a simple Non-Disclosure Agreement (NDA) clause for protecting
    confidential information.
    """
    
    context = """
    Requirements:
    - Clear definition of confidential information
    - Obligations of the receiving party
    - Exclusions from confidential information
    - Duration of the agreement
    - Professional and legally sound language
    - No longer than 1 paragraph
    """
    
    result = agent.run(task, context, quality_threshold=0.90)
    
    # Print results
    print("\n" + "-" * 80)
    print("FINAL RESULT")
    print("-" * 80)
    print(f"\nTotal Iterations: {result['iterations']}")
    print(f"Final Quality Score: {result['final_quality_score']:.2f}")
    print(f"Improvement: {result['improvement']:+.2f}")
    
    print("\n" + "-" * 80)
    print("FINAL CONTRACT CLAUSE:")
    print("-" * 80)
    print(result['final_response'])
    
    print("\n" + "-" * 80)
    print("FINAL CRITIQUE:")
    print("-" * 80)
    final_critique = result['final_critique']
    print(f"Quality Score: {final_critique['quality_score']:.2f}")
    print(f"Is Acceptable: {final_critique['is_acceptable']}")
    print(f"\nFinal Assessment:")
    for suggestion in final_critique['suggestions']:
        print(f"  • {suggestion}")


def demo_comparison():
    """Demonstrate quality improvement over iterations"""
    print_section("Demo 4: Quality Improvement Tracking")
    
    config_loader = ConfigLoader("agents.json")
    agent = ReflectionAgent(config_loader, max_iterations=3)
    
    task = "Explain quantum entanglement to a 10-year-old"
    context = "Use simple analogies, avoid jargon, be engaging and accurate"
    
    result = agent.run(task, context, quality_threshold=0.85)
    
    print("\n" + "-" * 80)
    print("QUALITY PROGRESSION:")
    print("-" * 80)
    
    scores = [c['quality_score'] for c in result['critiques']]
    scores.append(result['final_quality_score'])
    
    print("\nQuality Score Over Iterations:")
    for i, score in enumerate(scores):
        bar = "█" * int(score * 50)
        print(f"Iteration {i}: {score:.2f} {bar}")
    
    print(f"\nTotal Improvement: {result['improvement']:+.2f}")
    print(f"Percentage Improvement: {(result['improvement'] / scores[0] * 100):+.1f}%")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    REFLECTION/SELF-CORRECTION PATTERN DEMO                   ║
║                                                                              ║
║  This demo showcases how an LLM agent can iteratively improve its output    ║
║  through self-critique and refinement, achieving higher quality results.    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run individual demos
    # Uncomment the demos you want to run:
    
    print("\n[INFO] Starting demonstrations...")
    print("[INFO] Each demo shows the agent improving its output through reflection")
    
    # Demo 1: Code Generation
    demo_code_generation()
    
    # Demo 2: Technical Documentation
    # demo_technical_documentation()
    
    # Demo 3: Legal Contract
    # demo_legal_contract()
    
    # Demo 4: Quality Tracking
    # demo_comparison()
    
    print("\n" + "=" * 80)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\n[INFO] The Reflection pattern successfully demonstrated iterative improvement!")
    print("[INFO] Try uncommenting other demos to see different use cases.\n")
