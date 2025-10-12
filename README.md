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

The main application (`main.py`) and the accompanying batch script (`004_run.bat`) allow you to run evaluations for different metrics.

### Running Evaluations with the Batch Script

The `004_run.bat` script provides a convenient way to run evaluations and view available options.

1.  **Display Usage and Metrics:**
    Run the script without any arguments to see a detailed list of all available metrics and their descriptions.

    ```bash
    .\004_run.bat
    ```

2.  **Run a Specific Metric:**
    Pass the name of a metric as an argument to the script.

    ```bash
    .\004_run.bat <metric_name>
    ```

    **Example:** To run only the `rouge` evaluation:

    ```bash
    .\004_run.bat rouge
    ```

3.  **Run All Metrics:**
    To execute all available metrics sequentially, use the `all` argument.

    ```bash
    .\004_run.bat all
    ```

## Evaluation Metrics

This framework uses a combination of modern LLM-judged metrics from `ragas` and classic NLP/retrieval metrics.

### Ragas Metrics (LLM-as-a-judge)

- **Faithfulness:** Measures whether the answer is factually consistent with the provided context.
- **Answer Relevancy:** Assesses how relevant the answer is to the given question.
- **Context Precision:** Measures the signal-to-noise ratio in the retrieved contexts (are they relevant and to the point?).
- **Context Recall:** Evaluates whether the retrieved contexts contain all the necessary information from the ground truth.
- **Answer Correctness:** Assesses the factual accuracy of the answer when compared to the ground truth.

### Classic NLP & Retrieval Metrics

- **ROUGE:** (Recall-Oriented Understudy for Gisting Evaluation) Measures n-gram overlap between the generated answer and a ground truth, focusing on recall.
- **BLEU:** (Bilingual Evaluation Understudy) Measures n-gram overlap with a focus on precision.
- **BERTScore:** Measures the semantic similarity between the answer and a ground truth using contextual embeddings from BERT.
- **Retrieval Metrics:** A composite group that calculates:
    - **Precision@K:** The proportion of retrieved documents that are relevant.
    - **Recall@K:** The proportion of all relevant documents that were successfully retrieved.
    - **Mean Reciprocal Rank (MRR):** The rank of the first relevant retrieved document.
- **nDCG:** (Normalized Discounted Cumulative Gain) Evaluates the quality of the ranking of retrieved documents based on their relevance.

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
