# RAG Evaluation Framework using Ragas

## Description

This project provides a robust framework for evaluating the performance of Retrieval-Augmented Generation (RAG) pipelines. It utilizes the `ragas` library to assess various aspects of a RAG system's output, such as faithfulness, answer relevancy, context precision, and recall.

The framework is designed to be easily extensible and allows for testing different evaluation metrics against predefined positive and negative scenarios. This helps in systematically analyzing the strengths and weaknesses of your RAG implementation.

## Installation

Follow these steps to set up the project environment on Windows.

1. **Initialize Git:**
   Run the `000_init.bat` script to initialize the Git repository and configure user settings.

   ```bash
   .\000_init.bat
   ```

2. **Create Virtual Environment:**
   Run `001_env.bat` to create a Python virtual environment named `.venv`.

   ```bash
   .\001_env.bat
   ```

3. **Activate Virtual Environment:**
   Activate the environment by running `002_activate.bat`.

   ```bash
   .\002_activate.bat
   ```

4. **Install Dependencies:**
   Run `003_setup.bat` to install all the required packages from `requirements.txt`.

   ```bash
   .\003_setup.bat
   ```

## Usage

The `004_run.bat` script is the unified entry point for all evaluation tasks. It accepts a command as its first argument to determine which evaluation to run.

### Running Evaluations

1.  **Display Help:**
    Run the script without any arguments to see a detailed list of all available commands and their specific options.

    ```bash
    .\004_run.bat
    ```

2.  **Classic Metric Commands**
    These commands run the original evaluation script (`individual_metrics_runner.py`) for classic NLP and Ragas metrics.

    *   **Usage:** `.\004_run.bat <metric_name>`
    *   **Example:** To run the `faithfulness` metric:
        ```bash
        .\004_run.bat faithfulness
        ```
    *   **Available Commands:** `faithfulness`, `answer_relevancy`, `context_recall`, `context_precision`, `answer_correctness`, `classic`, `retrieval`, `all`.

3.  **Agentic Command: `judge`**
    This command runs an evaluation on a dataset using a single, specialized judge agent.

    *   **Usage:** `.\004_run.bat judge --input <infile> --output <outfile> --judge <judge_name>`
    *   **Example:** To evaluate a dataset for clarity:
        ```bash
        .\004_run.bat judge --input data/eval_data.csv --output results/judge_clarity_results.csv --judge clarity
        ```
    *   **Available Judges:** `factual`, `clarity`, `relevance`, `safety`.

4.  **Agentic Command: `jury`**
    This command runs the full, multi-agent system for a comprehensive evaluation.

    *   **Usage:** `.\004_run.bat jury --input <infile> --output <outfile>`
    *   **Example:**
        ```bash
        .\004_run.bat jury --input data/eval_data.csv --output results/jury_final_verdict.csv
        ```

## Evaluation Metrics & Design Patterns

This framework has evolved to incorporate sophisticated, agent-based evaluation patterns.

### LLM as a Judge
This design pattern uses a single LLM agent with a specific persona and task to evaluate a single quality dimension of a RAG system's output. For example, a `ClarityJudgeAgent` is prompted to focus solely on how clear and concise an answer is. This provides a targeted, qualitative score for a specific aspect.

### LLM as a Jury
This is a more advanced pattern where multiple, specialized "Judge" agents are orchestrated by a "Chief Justice" agent.
1.  **The Jury:** A panel of agents (`FactualJudgeAgent`, `ClarityJudgeAgent`, `RelevanceJudgeAgent`, `SafetyJudgeAgent`) each evaluate the same RAG output from their unique perspective.
2.  **The Chief Justice:** This agent collects the verdicts from all judges and synthesizes them into a single, comprehensive final judgment, including an overall score.

This pattern provides a holistic and multi-faceted evaluation, mimicking a real-world panel of experts.

### Classic NLP & Retrieval Metrics

The classic commands still support the original set of metrics:
- **ROUGE, BLEU, BERTScore:** For generation quality.
- **Precision@K, Recall@K, MRR, nDCG:** For retrieval quality.

## Project Structure



```text
.
├── src/
│   ├── __init__.py
│   ├── llm_evaluation.py   # Contains the RagasEvaluator class and LLM factory.
│   └── classic_metrics.py  # Contains the ClassicMetricEvaluator for ROUGE, BLEU, etc.
├── tests/
│   ├── __init__.py
│   ├── test_llm_evaluation.py # Unit tests for the evaluation logic.
│   └── test_main.py        # Unit tests for the main application script.
├── .env                    # Environment variables (e.g., API keys).
├── main.py                 # Main script to run evaluations.
├── requirements.txt        # Project dependencies.
├── pytest.ini              # Pytest configuration.
├── README.md               # This file.
└── *.bat                   # Batch scripts for Windows automation.
```

## Batch Scripts (Windows)

This project includes the following batch files to simplify common tasks on Windows:

- `000_init.bat`: Initializes the Git repository and sets up local user config.
- `001_env.bat`: Creates a Python virtual environment named `.venv`.
- `002_activate.bat`: Activates the `.venv` virtual environment.
- `003_setup.bat`: Installs Python packages from `requirements.txt`.
- `004_run.bat`: Executes the main script (`main.py`) to run all evaluations.
- `005_run_test.bat`: Runs unit tests using `pytest`.
- `005_run_code_cov.bat`: Runs unit tests with code coverage reporting.
- `008_deactivate.bat`: Deactivates the virtual environment.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss potential changes.

## License

This project is licensed under the MIT License.

This project is licensed under the MIT License.
