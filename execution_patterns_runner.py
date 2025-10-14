import argparse
from src.agents import ConfigLoader, ToolUsingAgent, PlanningAgent

def run_tool_using_agent(prompt: str):
    """Initializes and runs the ToolUsingAgent."""
    print("--- Running Tool-Using Agent ---")
    config_loader = ConfigLoader("agents.json")
    agent = ToolUsingAgent(config_loader)
    result = agent.run(prompt)
    print("\n--- Final Answer ---")
    print(result)

def run_planning_agent(goal: str):
    """Initializes and runs the PlanningAgent."""
    print("--- Running Planning Agent ---")
    config_loader = ConfigLoader("agents.json")
    agent = PlanningAgent(config_loader)
    result = agent.run(goal)
    print("\n--- Final Answer ---")
    print(result)

def main():
    parser = argparse.ArgumentParser(description="Run Execution and Capability Pattern Agents.")
    subparsers = parser.add_subparsers(dest="pattern", required=True)

    # Sub-parser for the Tool Use pattern
    parser_tool = subparsers.add_parser("tool-use", help="Run the Tool-Using Agent.")
    parser_tool.add_argument(
        "prompt", type=str, nargs="+", help="The prompt for the agent to process."
    )

    # Sub-parser for the Planning pattern
    parser_plan = subparsers.add_parser("plan-and-execute", help="Run the Planning Agent.")
    parser_plan.add_argument(
        "goal", type=str, nargs="+", help="The goal for the agent to achieve."
    )

    args = parser.parse_args()

    if args.pattern == "tool-use":
        prompt = " ".join(args.prompt)
        run_tool_using_agent(prompt)
    elif args.pattern == "plan-and-execute":
        goal = " ".join(args.goal)
        run_planning_agent(goal)

if __name__ == "__main__":
    main()
