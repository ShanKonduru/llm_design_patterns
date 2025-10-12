import argparse
import pandas as pd
from tqdm import tqdm
from src.agents import (
    ConfigLoader,
    FactualJudgeAgent,
    ClarityJudgeAgent,
    RelevanceJudgeAgent,
    SafetyJudgeAgent
)

# A mapping from judge names (as strings) to their corresponding classes
JUDGE_MAPPING = {
    "factual": FactualJudgeAgent,
    "clarity": ClarityJudgeAgent,
    "relevance": RelevanceJudgeAgent,
    "safety": SafetyJudgeAgent,
}

def main(input_file: str, output_file: str, judge_name: str):
    """
    Main function to run a single 'LLM as a Judge' evaluation.

    Args:
        input_file (str): Path to the input CSV/Excel file.
        output_file (str): Path to save the output CSV file.
        judge_name (str): The name of the judge to use for evaluation.
    """
    print(f"Initializing the 'LLM as a Judge' Evaluation Framework...")
    
    # Select the judge class from the mapping
    judge_class = JUDGE_MAPPING.get(judge_name.lower())
    if not judge_class:
        print(f"Error: Judge '{judge_name}' not found. Available judges are: {list(JUDGE_MAPPING.keys())}")
        return

    # Load the agent configurations
    config_loader = ConfigLoader("agents.json")
    
    # Initialize the selected judge
    judge = judge_class(config_loader)
    print(f"Using judge: {judge.agent_name}")
    
    # Load the dataset to be evaluated
    print(f"Loading dataset from {input_file}...")
    try:
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(input_file)
        else:
            raise ValueError("Unsupported input file format. Please use CSV or Excel.")
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return
    except Exception as e:
        print(f"Error loading input file: {e}")
        return

    all_verdicts = []

    print(f"Starting evaluation for {len(df)} cases...")
    # Use tqdm for a progress bar
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc=f"Judging with {judge.agent_name}"):
        case_data = row.to_dict()
        
        # Run the selected judge
        verdict = judge.run(case_data)
        
        if verdict:
            record = {
                "case_index": index,
                "judge": verdict.judge_name,
                "score": verdict.score,
                "verdict": verdict.verdict,
            }
            # Add specific sub-metrics if they exist
            if verdict.metrics:
                record.update(verdict.metrics)
            all_verdicts.append(record)

    if not all_verdicts:
        print("Evaluation completed, but no verdicts were generated.")
        return

    # Convert all verdicts into a single DataFrame
    final_df = pd.DataFrame(all_verdicts)
    
    # Save the results
    try:
        final_df.to_csv(output_file, index=False)
        print(f"\nEvaluation complete. Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a single 'LLM as a Judge' evaluation.")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input data file (CSV or Excel)."
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to save the output results (CSV)."
    )
    parser.add_argument(
        "--judge",
        type=str,
        required=True,
        choices=list(JUDGE_MAPPING.keys()),
        help="The name of the judge to use for the evaluation."
    )
    
    args = parser.parse_args()
    main(input_file=args.input, output_file=args.output, judge_name=args.judge)
