@echo off
REM This script runs the main Python application with a specified metric or mode.
REM It assumes that the virtual environment is already activated.

setlocal enabledelayedexpansion

set "command=%~1"
shift
set "args="
:build_args
if "%~1"=="" goto :done_args
if defined args (
    set "args=!args! %~1"
) else (
    set "args=%~1"
)
shift
goto :build_args
:done_args

if /i "%command%"=="tool-use" (
    echo Running the Tool-Use pattern...
    python execution_patterns_runner.py tool-use !args!
    goto :eof
)
if /i "%command%"=="plan-and-execute" (
    echo Running the Plan-and-Execute pattern...
    python execution_patterns_runner.py plan-and-execute !args!
    goto :eof
)

REM Check for agentic commands (judge, jury)
if /i "%command%"=="judge" (
    echo Running the LLM as a Judge evaluation...
    python LLM_as_a_Judge.py %command% %all_args%
    goto :eof
)

if /i "%command%"=="jury" (
    echo Running the LLM as a Jury evaluation...
    python LLM_as_a_Jury.py %command% %all_args%
    goto :eof
)

REM If no agentic command is found, assume it's a classic metric
echo Running the classic metrics runner for metric: %command%
python individual_metrics_runner.py %command% %all_args%

:eof




