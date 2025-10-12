@echo off
REM This script runs the main Python application with a specified metric.
REM It assumes that the virtual environment is already activated.
REM
REM Usage:
REM   .\004_run.bat [metric_name]
REM
REM   metric_name (optional): The name of the metric to evaluate.
REM     Choices: faithfulness, answer_relevancy, context_recall,
REM              context_precision, answer_correctness, rouge, bleu,
REM              bert_score, retrieval, ndcg, all.
REM     Defaults to 'all' if not provided.

SET "METRIC=%1"

IF "%METRIC%"=="" (
    SET "METRIC=all"
)

echo Running the main application for metric: %METRIC%
python main.py --metric %METRIC%

echo.
echo Application run finished.


