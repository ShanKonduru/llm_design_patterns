@echo off
REM ============================================================================
REM LLM Design Patterns - Unified Execution Script
REM ============================================================================
REM This script runs various evaluation metrics and design patterns.
REM It assumes that the virtual environment is already activated.
REM
REM Usage: .\004_run.bat [command] [arguments]
REM ============================================================================

setlocal enabledelayedexpansion

SET "COMMAND=%~1"

REM If no command is provided, show help
IF "%COMMAND%"=="" (
    goto :show_help
)

REM ============================================================================
REM AGENTIC EVALUATION PATTERNS
REM ============================================================================

REM LLM as a Judge Pattern
if /i "%COMMAND%"=="judge" (
    echo.
    echo [Judge Pattern] Running single judge evaluation...
    echo.
    shift
    python LLM_as_a_Judge.py %*
    goto :end
)

REM LLM as a Jury Pattern
if /i "%COMMAND%"=="jury" (
    echo.
    echo [Jury Pattern] Running multi-agent jury evaluation...
    echo.
    shift
    python LLM_as_a_Jury.py %*
    goto :end
)

REM ============================================================================
REM EXECUTION PATTERNS
REM ============================================================================

REM Tool Use Pattern
if /i "%COMMAND%"=="tool-use" (
    echo.
    echo [Tool Use Pattern] Running tool-using agent...
    echo.
    shift
    python execution_patterns_runner.py tool-use %*
    goto :end
)

REM Plan-and-Execute Pattern
if /i "%COMMAND%"=="plan-and-execute" (
    echo.
    echo [Plan-and-Execute Pattern] Running planning agent...
    echo.
    shift
    python execution_patterns_runner.py plan-and-execute %*
    goto :end
)

REM Reflection Pattern
if /i "%COMMAND%"=="reflection" (
    echo.
    echo [Reflection Pattern] Running reflection agent...
    echo.
    shift
    python demo_reflection_pattern.py %*
    goto :end
)

REM ============================================================================
REM RAGAS METRICS (LLM-as-a-Judge)
REM ============================================================================

if /i "%COMMAND%"=="faithfulness" (
    echo.
    echo [RAGAS Metric] Measuring faithfulness...
    echo.
    python individual_metrics_runner.py --metric faithfulness
    goto :end
)

if /i "%COMMAND%"=="answer_relevancy" (
    echo.
    echo [RAGAS Metric] Measuring answer relevancy...
    echo.
    python individual_metrics_runner.py --metric answer_relevancy
    goto :end
)

if /i "%COMMAND%"=="context_recall" (
    echo.
    echo [RAGAS Metric] Measuring context recall...
    echo.
    python individual_metrics_runner.py --metric context_recall
    goto :end
)

if /i "%COMMAND%"=="context_precision" (
    echo.
    echo [RAGAS Metric] Measuring context precision...
    echo.
    python individual_metrics_runner.py --metric context_precision
    goto :end
)

if /i "%COMMAND%"=="answer_correctness" (
    echo.
    echo [RAGAS Metric] Measuring answer correctness...
    echo.
    python individual_metrics_runner.py --metric answer_correctness
    goto :end
)

REM ============================================================================
REM CLASSIC GENERATION METRICS
REM ============================================================================

if /i "%COMMAND%"=="rouge" (
    echo.
    echo [Classic Metric] Measuring ROUGE scores...
    echo.
    python individual_metrics_runner.py --metric rouge
    goto :end
)

if /i "%COMMAND%"=="bleu" (
    echo.
    echo [Classic Metric] Measuring BLEU scores...
    echo.
    python individual_metrics_runner.py --metric bleu
    goto :end
)

if /i "%COMMAND%"=="bert_score" (
    echo.
    echo [Classic Metric] Measuring BERT scores...
    echo.
    python individual_metrics_runner.py --metric bert_score
    goto :end
)

REM ============================================================================
REM CLASSIC RETRIEVAL METRICS
REM ============================================================================

if /i "%COMMAND%"=="retrieval" (
    echo.
    echo [Classic Metric] Calculating retrieval metrics...
    echo.
    python individual_metrics_runner.py --metric retrieval
    goto :end
)

if /i "%COMMAND%"=="ndcg" (
    echo.
    echo [Classic Metric] Measuring nDCG...
    echo.
    python individual_metrics_runner.py --metric ndcg
    goto :end
)

REM ============================================================================
REM UTILITY COMMANDS
REM ============================================================================

if /i "%COMMAND%"=="all" (
    echo.
    echo [Utility] Running all available metrics sequentially...
    echo.
    python individual_metrics_runner.py --metric all
    goto :end
)

if /i "%COMMAND%"=="classic" (
    echo.
    echo [Utility] Running all classic metrics...
    echo.
    python individual_metrics_runner.py --metric classic
    goto :end
)

REM ============================================================================
REM ERROR HANDLING
REM ============================================================================

echo.
echo [ERROR] Unknown command: %COMMAND%
echo.
echo Type '.\004_run.bat' without arguments to see available commands.
echo.
goto :end

REM ============================================================================
REM HELP DOCUMENTATION
REM ============================================================================

:show_help
echo.
echo ============================================================================
echo  LLM Design Patterns - Unified Execution Script
echo ============================================================================
echo.
echo Usage: .\004_run.bat [command] [arguments]
echo.
echo ============================================================================
echo  AGENTIC EVALUATION PATTERNS
echo ============================================================================
echo.
echo   judge                Run LLM as a Judge evaluation
echo                        Options: --input FILE --output FILE --judge TYPE
echo                        Judge types: factual, clarity, relevance, safety
echo                        Example: .\004_run.bat judge --input data.csv --output results.csv --judge factual
echo.
echo   jury                 Run LLM as a Jury evaluation (multi-agent)
echo                        Options: --input FILE --output FILE
echo                        Example: .\004_run.bat jury --input data.csv --output verdict.csv
echo.
echo ============================================================================
echo  EXECUTION PATTERNS (Agentic Behaviors)
echo ============================================================================
echo.
echo   tool-use             Run Tool Use pattern with prompt
echo                        Example: .\004_run.bat tool-use "what is 156 times 89?"
echo                        Example: .\004_run.bat tool-use "what day is Christmas 2025?"
echo.
echo   plan-and-execute     Run Plan-and-Execute pattern with goal
echo                        Example: .\004_run.bat plan-and-execute "calculate 50*3 and find day of Christmas 2025"
echo.
echo   reflection           Run Reflection/Self-Correction pattern
echo                        Options: --max-iterations N --quality-threshold X
echo                        Example: .\004_run.bat reflection "Write a factorial function"
echo.
echo ============================================================================
echo  RAGAS METRICS (LLM-as-a-Judge Evaluation)
echo ============================================================================
echo.
echo   faithfulness         Measures if the answer is factually consistent with context
echo   answer_relevancy     Measures if the answer is relevant to the question
echo   context_recall       Measures if retrieved context contains all necessary info
echo   context_precision    Measures if retrieved context contains only relevant info
echo   answer_correctness   Measures if the answer is factually correct vs ground truth
echo.
echo ============================================================================
echo  CLASSIC GENERATION METRICS
echo ============================================================================
echo.
echo   rouge                Measures n-gram overlap (recall-focused)
echo   bleu                 Measures n-gram overlap (precision-focused)
echo   bert_score           Measures semantic similarity using BERT embeddings
echo.
echo ============================================================================
echo  CLASSIC RETRIEVAL METRICS
echo ============================================================================
echo.
echo   retrieval            Calculates Precision@K, Recall@K, and MRR
echo   ndcg                 Measures ranked order of retrieved documents
echo.
echo ============================================================================
echo  UTILITY COMMANDS
echo ============================================================================
echo.
echo   all                  Runs all available metrics sequentially
echo   classic              Runs all classic metrics (ROUGE, BLEU, BERT, etc.)
echo.
echo ============================================================================
echo  EXAMPLES
echo ============================================================================
echo.
echo   REM Run a single RAGAS metric
echo   .\004_run.bat faithfulness
echo.
echo   REM Run Tool Use pattern with a math question
echo   .\004_run.bat tool-use "what is the square root of 256?"
echo.
echo   REM Run Planning pattern with multi-step goal
echo   .\004_run.bat plan-and-execute "Calculate 50*3 and tell me what day is Dec 25, 2025"
echo.
echo   REM Run Judge evaluation with specific judge
echo   .\004_run.bat judge --input evaluation_data.csv --output results.csv --judge clarity
echo.
echo   REM Run Jury evaluation for comprehensive assessment
echo   .\004_run.bat jury --input evaluation_data.csv --output final_verdict.csv
echo.
echo   REM Run Reflection pattern for high-quality code generation
echo   .\004_run.bat reflection "Write a Python function to calculate factorial"
echo.
echo   REM Run all classic metrics
echo   .\004_run.bat classic
echo.
echo ============================================================================
echo.
goto :eof

:end
echo.
echo ============================================================================
echo Execution completed.
echo ============================================================================
echo.

:eof
endlocal





