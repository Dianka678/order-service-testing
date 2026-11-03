# Order service testing

Практика по тестированию Python: расчёт скидок, оформление заказа, уведомления, SQLite и идемпотентность по `request_id`.

Реализованный код и тесты не содержат комментариев. Исходные контракты, модели, ошибки, публичная спецификация и проверяющие инструменты преподавателя сохранены.

## Запуск

Нужен Python 3.10+.

```bash
python -m venv .venv
```

Активация на macOS/Linux:

```bash
source .venv/bin/activate
```

Активация в Windows cmd:

```bat
.venv\Scripts\activate
```

```bash
python -m pip install -r requirements.txt
python -m pytest tests spec --cov=app --cov-branch --cov-fail-under=90 --cov-report=term-missing --cov-report=html
python tools/self_check.py
python tools/check_mutations.py
```

110 тестовых случаев в `tests/`, 4 публичных примера в `spec/`. На Python 3.12 локально проходят все 114, покрытие `app/` с учётом ветвлений — 100%. Мутационная проверка обнаруживает все 11 поломок. Это результаты локальной проверки, не оценка скрытой системы преподавателя.

## Отчёты

- Покрытие: `htmlcov/index.html`, скриншот `docs/coverage.png`.
- Allure: результаты `allure-results/`, скриншот `docs/allure.png`.
- Мутации: `docs/MUTATIONS.md` и `docs/mutations.json`.
- `REPORT.md` — черновик ответов. Перед сдачей заполнить ФИО и группу и переписать текст своими словами.

Allure CLI устанавливается отдельно. После прогона тестов:

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

Для отдельного запуска:

```bash
python -m pytest -m unit
python -m pytest -m integration
python -m pytest spec
```

## CI

GitHub Actions проверяет Python 3.10, 3.12 и 3.13, запускает тесты и самопроверку, требует покрытие от 90% и сохраняет `htmlcov`, `coverage.xml` и `allure-results` даже при падении тестов.

## Ограничения

Кэш `request_id` работает в пределах одного экземпляра сервиса и не является распределённой защитой от повторов. Уменьшение складского остатка не предусмотрено исходным заданием. Настоящая отправка уведомлений не требуется: зависимость передаётся через контракт `Notifier`.

## Перед сдачей

1. Переписать ответы в `REPORT.md`, заполнить ФИО и группу.
2. Вручную воспроизвести мутации из `GUIDE.md`, если требуется именно ручная проверка; каждый раз возвращать исходный код.
3. Убедиться, что CI зелёный и отчёты сохранены.
4. Получить ревью Pull Request от однокурсника и после ревью перенести работу в `main`.

Исходное условие: [TASK.md](TASK.md). Подробное руководство: [GUIDE.md](GUIDE.md).
