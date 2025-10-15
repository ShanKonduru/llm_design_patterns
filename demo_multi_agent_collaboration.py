"""
Demo: Multi-Agent Collaboration Pattern

This script demonstrates the Multi-Agent Collaboration Pattern where specialized
agents work together to solve complex software engineering tasks.

Showcases three collaboration modes:
1. Sequential: Planner -> Coder -> Tester -> Reviewer (pipeline)
2. Parallel: All agents analyze the same requirements simultaneously
3. Hierarchical: Coordinator manages and synthesizes specialist work

Usage:
    python demo_multi_agent_collaboration.py [mode]
    
    mode: sequential, parallel, or hierarchical (default: sequential)
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.config import ConfigLoader
from src.agents.software_team import create_software_team


def print_separator(title: str = ""):
    """Print a nice separator for output formatting."""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    else:
        print(f"{'='*70}\n")


def demo_sequential_collaboration():
    """
    Demonstrate Sequential Collaboration.
    Each agent builds on the previous agent's output.
    """
    print_separator("SEQUENTIAL COLLABORATION DEMO")
    print("Pipeline: Planner → Coder → Tester → Reviewer")
    print("Each agent processes the output from the previous agent.\n")
    
    config_loader = ConfigLoader("agents.json")
    orchestrator, agents = create_software_team("sequential", config_loader)
    
    task = {
        "description": "Create a Python function to calculate Fibonacci numbers",
        "requirements": """
Create a Python function that:
1. Calculates the nth Fibonacci number
2. Handles edge cases (n=0, n=1, negative numbers)
3. Is efficient (avoid exponential recursion)
4. Includes proper docstring documentation
5. Has type hints
"""
    }
    
    result = orchestrator.collaborate(task)
    
    if result["success"]:
        print_separator("FINAL RESULT")
        print(f"✓ Sequential collaboration completed successfully!")
        print(f"\nFinal Output:")
        print(f"{result['final_output']}")
    else:
        print(f"✗ Collaboration failed: {result.get('error')}")
    
    # Print summary
    summary = orchestrator.get_collaboration_summary()
    print_separator("COLLABORATION SUMMARY")
    print(f"Mode: {summary['mode']}")
    print(f"Total Agents: {summary['total_agents']}")
    print(f"Tasks Executed: {summary['total_tasks']}")
    print(f"Successful: {summary['successful_tasks']}")
    print(f"Failed: {summary['failed_tasks']}")
    print(f"Agents: {', '.join(summary['agents'])}")


def demo_parallel_collaboration():
    """
    Demonstrate Parallel Collaboration.
    All agents analyze the same input simultaneously.
    """
    print_separator("PARALLEL COLLABORATION DEMO")
    print("All agents work simultaneously on the same requirements.")
    print("Results are synthesized at the end.\n")
    
    config_loader = ConfigLoader("agents.json")
    orchestrator, agents = create_software_team("parallel", config_loader)
    
    task = {
        "description": "Analyze requirements for a task management system",
        "requirements": """
Build a simple task management CLI application that:
1. Allows users to add, list, complete, and delete tasks
2. Persists tasks to a file (JSON format)
3. Supports task priorities (high, medium, low)
4. Shows task statistics (total, completed, pending)
5. Has a clean, user-friendly command-line interface
"""
    }
    
    result = orchestrator.collaborate(task)
    
    if result["success"]:
        print_separator("INDIVIDUAL AGENT RESULTS")
        for agent_result in result["individual_results"]:
            print(f"\n[{agent_result.agent_role}]")
            print(f"Status: {'✓ Success' if agent_result.success else '✗ Failed'}")
            if agent_result.success:
                output = agent_result.output
                # Truncate long outputs for readability
                output_str = str(output)
                if len(output_str) > 500:
                    output_str = output_str[:500] + "... (truncated)"
                print(f"{output_str}\n")
        
        print_separator("SYNTHESIS")
        print(result["synthesis"])
    else:
        print(f"✗ Collaboration failed: {result.get('error')}")
    
    # Print summary
    summary = orchestrator.get_collaboration_summary()
    print_separator("COLLABORATION SUMMARY")
    print(f"Mode: {summary['mode']}")
    print(f"Total Agents: {summary['total_agents']}")
    print(f"Tasks Executed: {summary['total_tasks']}")
    print(f"Successful: {summary['successful_tasks']}")
    print(f"Failed: {summary['failed_tasks']}")


def demo_hierarchical_collaboration():
    """
    Demonstrate Hierarchical Collaboration.
    A coordinator agent manages specialist agents.
    """
    print_separator("HIERARCHICAL COLLABORATION DEMO")
    print("Coordinator agent manages and synthesizes specialist work.")
    print("Structure: Coordinator → [Planner, Coder, Tester] → Coordinator\n")
    
    config_loader = ConfigLoader("agents.json")
    orchestrator, agents = create_software_team("hierarchical", config_loader)
    
    task = {
        "description": "Design and implement a simple calculator",
        "requirements": """
Create a Python calculator module that:
1. Supports basic operations: add, subtract, multiply, divide
2. Handles division by zero gracefully
3. Supports floating-point numbers
4. Has a clean API design
5. Includes comprehensive error handling
"""
    }
    
    result = orchestrator.collaborate(task)
    
    if result["success"]:
        print_separator("COORDINATION PLAN")
        print(result["coordinator_plan"])
        
        print_separator("SPECIALIST OUTPUTS")
        for i, specialist_result in enumerate(result["specialist_outputs"], 1):
            print(f"\n{i}. [{specialist_result.agent_role}]")
            print(f"   Status: {'✓ Success' if specialist_result.success else '✗ Failed'}")
            if specialist_result.success:
                output_str = str(specialist_result.output)
                if len(output_str) > 400:
                    output_str = output_str[:400] + "... (truncated)"
                print(f"   {output_str}\n")
        
        print_separator("FINAL SYNTHESIS")
        print(result["final_synthesis"])
    else:
        print(f"✗ Collaboration failed: {result.get('error')}")
    
    # Print summary
    summary = orchestrator.get_collaboration_summary()
    print_separator("COLLABORATION SUMMARY")
    print(f"Mode: {summary['mode']}")
    print(f"Total Agents: {summary['total_agents']}")
    print(f"Tasks Executed: {summary['total_tasks']}")
    print(f"Successful: {summary['successful_tasks']}")
    print(f"Failed: {summary['failed_tasks']}")


def main():
    """Main entry point for the demo."""
    print("\n" + "="*70)
    print("  MULTI-AGENT COLLABORATION PATTERN DEMO")
    print("  Software Engineering Team Collaboration")
    print("="*70 + "\n")
    
    # Determine which mode to run
    mode = "sequential"  # default
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode not in ['sequential', 'parallel', 'hierarchical']:
            print(f"Invalid mode: {mode}")
            print("Valid modes: sequential, parallel, hierarchical")
            sys.exit(1)
    
    print(f"Running in {mode.upper()} mode\n")
    print("This demo showcases how specialized AI agents collaborate")
    print("to solve complex software engineering tasks.\n")
    
    if mode == "sequential":
        demo_sequential_collaboration()
    elif mode == "parallel":
        demo_parallel_collaboration()
    elif mode == "hierarchical":
        demo_hierarchical_collaboration()
    
    print_separator()
    print("Demo completed!")
    print("\nTo try other modes, run:")
    print("  python demo_multi_agent_collaboration.py sequential")
    print("  python demo_multi_agent_collaboration.py parallel")
    print("  python demo_multi_agent_collaboration.py hierarchical")
    print()


if __name__ == "__main__":
    main()
