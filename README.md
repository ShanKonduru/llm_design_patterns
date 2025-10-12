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

The main application (`main.py`) allows you to run evaluations for different Ragas metrics. You can run all evaluations at once or specify a single metric.

### Running All Evaluations

To run all available evaluation metrics sequentially, execute the `004_run.bat` script or run `main.py` without any arguments.

```bash
.\004_run.bat
```

or

```bash
python main.py
```

### Running a Specific Metric

You can evaluate a single metric by using the `--metric` command-line argument. This is useful for focused testing and debugging.

```bash
python main.py --metric <metric_name>
```

Replace `<metric_name>` with one of the following:

- `faithfulness`
- `answer_relevancy`
- `context_recall`
- `context_precision`
- `answer_correctness`

**Example:** To run only the `faithfulness` evaluation:

```bash
python main.py --metric faithfulness
```

## Evaluation Metrics

This framework uses the following `ragas` metrics to evaluate the RAG pipeline:

- **Faithfulness:** Measures whether the answer is factually consistent with the provided context. A high score means the answer is well-supported by the context.
- **Answer Relevancy:** Assesses how relevant the answer is to the given question.
- **Context Precision:** Measures the signal-to-noise ratio in the retrieved contexts. It checks if the contexts are relevant and to the point.
- **Context Recall:** Evaluates whether the retrieved contexts contain all the necessary information from the ground truth to answer the question.
- **Answer Correctness:** Assesses the factual accuracy of the answer when compared to the ground truth.

## Project Structure

```text
.
├── src/
│   ├── __init__.py
│   └── llm_evaluation.py   # Contains the RagasEvaluator class and LLM factory.
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
