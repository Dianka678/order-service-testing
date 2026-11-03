@echo off
python -m pytest tests spec --cov=app --cov-branch --cov-fail-under=90 --cov-report=term-missing --cov-report=html --alluredir=allure-results
exit /b %errorlevel%
