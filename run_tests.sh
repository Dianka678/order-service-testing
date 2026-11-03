#!/usr/bin/env bash
# Тесты + покрытие + Allure одной командой (macOS/Linux). Запуск: ./run_tests.sh
set -e
rm -rf allure-results htmlcov .coverage
python -m pytest --cov=app --cov-branch --cov-report=term-missing --cov-report=html --alluredir=allure-results "$@"
echo "HTML-покрытие: htmlcov/index.html"
echo "Allure-отчёт:  allure serve allure-results   (Allure CLI ставится отдельно)"
