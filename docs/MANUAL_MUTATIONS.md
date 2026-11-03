# Ручная мутационная проверка

Дата: 3 ноября 2026 года.

Перед проверкой выполнен базовый прогон: 114 тестов прошли. Затем каждая поломка вносилась отдельной правкой в `app/`. После запуска тестов результат проверялся, а правка отменялась до следующей мутации. Скрипт автоматической мутационной проверки в этих запусках не использовался. Тесты не изменялись.

Команда для каждой внесённой поломки:

```bash
python -B -m pytest tests -q -o addopts= --tb=short
```

| № | Поломка | Упало | Прошло | Пример теста |
|---|---|---:|---:|---|
| 1 | Граница скидки 10 | 4 | 106 | [test_volume_discount_boundaries[10-5]](../tests/test_pricing.py) |
| 2 | Граница скидки 50 | 4 | 106 | [test_volume_discount_boundaries[50-10]](../tests/test_pricing.py) |
| 3 | Округление | 5 | 105 | [test_discount_rounds_half_up[9.90-5-9.41]](../tests/test_pricing.py) |
| 4 | Весь остаток склада | 2 | 108 | [test_order_can_use_entire_stock](../tests/test_order_service.py) |
| 5 | Сохранение заказа | 27 | 83 | [test_successful_order_is_saved](../tests/test_order_service.py) |
| 6 | Получатель уведомления | 6 | 104 | [test_notification_sent_once_after_success](../tests/test_notifications.py) |
| 7 | Двойное уведомление | 16 | 94 | [test_notification_sent_once_after_success](../tests/test_notifications.py) |
| 8 | Ошибка уведомителя | 6 | 104 | [test_failing_notifier_keeps_saved_order](../tests/test_notifications.py) |
| 9 | Фильтрация SQL | 1 | 109 | [test_list_filters_user_and_sorts_by_id[sqlite]](../tests/test_order_repository.py) |
| 10 | Порядок заказов | 1 | 109 | [test_list_filters_user_and_sorts_by_id[sqlite]](../tests/test_order_repository.py) |
| 11 | Ограничение SQLite | 2 | 108 | [test_sqlite_rejects_nonpositive_quantity[0]](../tests/test_order_repository.py) |

## Изменения и наблюдаемые ошибки

1. **Граница скидки 10.** `quantity >= 10` → `quantity > 10` Ожидалось 5%, получено 0%.

2. **Граница скидки 50.** `quantity >= 50` → `quantity > 50` Ожидалось 10%, получено 5%.

3. **Округление.** `ROUND_HALF_UP` → `ROUND_HALF_EVEN` Ожидалось 9.41, получено 9.40.

4. **Весь остаток склада.** `stock < quantity` → `stock <= quantity` Заказ 5 товаров при остатке 5 вызвал OutOfStock.

5. **Сохранение заказа.** Вызов `self._orders.add(...)` заменён созданием `Order(1, ...)` без сохранения. Поиск сохранённого заказа вернул None.

6. **Получатель уведомления.** `order.user_id` → `order.product_id` в вызове send. Ожидался получатель 42, получен 7.

7. **Двойное уведомление.** Добавлен второй вызов `self._notify(order, product)`. Ожидалось одно сообщение, получено два.

8. **Ошибка уведомителя.** Удалён блок try/except вокруг send. TimeoutError прервал оформление вместо возврата сохранённого заказа.

9. **Фильтрация SQL.** Удалены `WHERE user_id = ?` и соответствующий аргумент запроса. В списке пользователя 42 появился заказ пользователя 65.

10. **Порядок заказов.** `ORDER BY id` → `ORDER BY id DESC` Получены идентификаторы 3, 1 вместо 1, 3.

11. **Ограничение SQLite.** Удалено `CHECK (quantity > 0)`. Для 0 и -1 не возник ожидаемый IntegrityError.

## Восстановление

После каждой проверки правильный код возвращён. После последней правки содержимое `app/pricing.py`, `app/service.py` и `app/sqlite_repo.py` побайтово совпало с исходным состоянием перед проверкой.

Финальная команда:

```bash
python -B -m pytest tests spec -q -o addopts= --cov=app --cov-branch --cov-fail-under=90 --cov-report=term-missing
```

Результат: 114 тестов прошли, покрытие `app/` с учётом ветвлений 100%. Все 11 ручных мутаций обнаружены. Сломанные версии не включены в коммиты.
