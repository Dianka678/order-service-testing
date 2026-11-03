@echo off
rem Тесты + покрытие + Allure одной командой (Windows)
rmdir /s /q allure-results htmlcov 2>nul
python -m pytest --cov=app --cov-branch --cov-report=term-missing --cov-report=html --alluredir=allure-results %*
echo HTML-покрытие: htmlcov\index.html
echo Allure-отчёт:  allure serve allure-results
