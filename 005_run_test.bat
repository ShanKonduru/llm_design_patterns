@echo off
pytest --cov=src --cov-report=term-missing --cov-report=html  --html=test_reports\report.html --self-contained-html tests\
