import argparse
import pandas as pd
from tqdm import tqdm
from src.agents import ConfigLoader, ChiefJusticeAgent


def main(input_file: str, output_file: str):
    """
    Main function to run the 'LLM as a Jury' agentic evaluation system.

    Args:
        input_file (str): Path to the input CSV/Excel file.
        output_file (str): Path to save the output CSV file.
    """
    print("Initializing the 'LLM as a Jury' Evaluation Framework...")

    # Load the agent configurations
    config_loader = ConfigLoader("agents.json")

    # Initialize the head of the jury
    chief_justice = ChiefJusticeAgent(config_loader)

    # Load the dataset to be evaluated
    print(f"Loading dataset from {input_file}...")
    try:
        if input_file.endswith(".csv"):
            df = pd.read_csv(input_file)
        elif input_file.endswith((".xls", ".xlsx")):
            df = pd.read_excel(input_file)
        else:
            raise ValueError("Unsupported input file format. Please use CSV or Excel.")
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return
    except Exception as e:
        print(f"Error loading input file: {e}")
        return

    all_results = []

    print(f"Starting evaluation for {len(df)} cases...")
    # Use tqdm for a progress bar
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Evaluating Cases"):
        case_data = row.to_dict()

        # The Chief Justice runs the entire jury deliberation
        final_verdict = chief_justice.run(case_data)

        if final_verdict:
            # Use the helper to get a detailed DataFrame for this single case
            case_results_df = chief_justice.verdicts_to_dataframe(final_verdict)

            # Add a column to identify the case, using the index from the input file
            case_results_df["case_index"] = index

            all_results.append(case_results_df)

    if not all_results:
        print("Evaluation completed, but no results were generated.")
        return

    # Concatenate all individual case DataFrames into a single master DataFrame
    final_df = pd.concat(all_results, ignore_index=True)

    # Reorder columns to have the case_index first
    cols = ["case_index"] + [col for col in final_df.columns if col != "case_index"]
    final_df = final_df[cols]

    # Save the comprehensive results
    try:
        final_df.to_csv(output_file, index=False)
        print(f"\nEvaluation complete. Detailed results saved to {output_file}")
    except Exception as e:
        print(f"Error saving output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the 'LLM as a Jury' Agentic RAG Evaluation Framework."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input data file (CSV or Excel).",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to save the detailed output results (CSV).",
    )

    args = parser.parse_args()
    main(input_file=args.input, output_file=args.output)
