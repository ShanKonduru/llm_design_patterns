@echo off
REM This script runs the main Python application with a specified metric or mode.
REM It assumes that the virtual environment is already activated.

SET "COMMAND=%1"

IF "%COMMAND%"=="" (
    goto :show_help
)

REM The SHIFT command moves the argument list one position to the left.
REM This is so we can pass the rest of the arguments (%*) to the python scripts.
SHIFT

IF /I "%COMMAND%"=="judge" (
    echo Running 'LLM as a Judge' evaluation...
    python LLM_as_a_Judge.py %*
    goto :eof
)

IF /I "%COMMAND%"=="jury" (
    echo Running 'LLM as a Jury' evaluation...
    python LLM_as_a_Jury.py %*
    goto :eof
)

REM --- If the command is not judge or jury, it's treated as a classic metric ---

echo Running the classic metrics runner for metric: %COMMAND%
python individual_metrics_runner.py --metric %COMMAND%
goto :eof


:show_help
echo.
echo Usage: %0 [command] [options]
echo.
echo Available Commands:
echo.
echo   Classic Metrics Commands:
echo   (These run the individual_metrics_runner.py script)
echo   ----------------------------------------------------
echo     - faithfulness, answer_relevancy, context_recall, context_precision, answer_correctness
echo     - classic (for ROUGE, BLEU, etc.), retrieval (for Precision@K, etc.)
echo     - all (runs all classic and ragas metrics)
echo   Example: %0 faithfulness
echo.
echo.
echo   Agentic Commands:
echo   -----------------
echo   judge     - Runs an evaluation using a single specialized judge agent.
echo     Usage:   %0 judge --input [infile] --output [outfile] --judge [judge_name]
echo     Example: %0 judge --input data/eval_data.csv --output results/judge_clarity.csv --judge clarity
echo.
echo   jury      - Runs the full multi-agent jury for a comprehensive evaluation.
echo     Usage:   %0 jury --input [infile] --output [outfile]
echo     Example: %0 jury --input data/eval_data.csv --output results/jury_final.csv
echo.
goto :eof




