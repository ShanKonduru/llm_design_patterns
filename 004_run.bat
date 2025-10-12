@echo off
REM This script runs the main Python application with a specified metric.
REM It assumes that the virtual environment is already activated.

SET "METRIC=%1"

IF "%METRIC%"=="" (
    echo Usage: %0 [metric_name]
    echo.
    echo Available metrics are:
    echo.
    echo   RAGAS Metrics (LLM-as-a-judge):
    echo     - faithfulness:       Measures if the answer is factually consistent with the context.
    echo     - answer_relevancy:   Measures if the answer is relevant to the question.
    echo     - context_recall:     Measures if the retrieved context contains all necessary information.
    echo     - context_precision:  Measures if the retrieved context contains only relevant information.
    echo     - answer_correctness: Measures if the answer is factually correct compared to a ground truth.
    echo.
    echo   Classic Generation Metrics:
    echo     - rouge:              Measures n-gram overlap between answer and ground truth (recall-focused).
    echo     - bleu:               Measures n-gram overlap with a precision focus.
    echo     - bert_score:         Measures semantic similarity using BERT embeddings.
    echo.
    echo   Classic Retrieval Metrics:
    echo     - retrieval:          Calculates Precision@K, Recall@K, and MRR for retrieved documents.
    echo     - ndcg:               Measures the ranked order of retrieved documents based on relevance.
    echo.
    echo   Utility:
    echo     - all:                Runs all available metrics sequentially.
    goto :eof
)

echo Running the main application for metric: %METRIC%
python main.py --metric %METRIC%

echo.
echo Application run finished.


