# Мутационная проверка

Изолированные копии проекта, по одной поломке за запуск. Исходный код проекта не меняется.

| Мутация | Результат | Пример упавшего теста |
|---|---|---|
| `discount_boundary_10` | Обнаружена | `tests.test_order_service::test_order_total_includes_volume_discount[10-9.41]` |
| `discount_boundary_50` | Обнаружена | `tests.test_order_service::test_order_total_includes_volume_discount[50-44.55]` |
| `rounding_half_even` | Обнаружена | `tests.test_order_service::test_order_total_includes_volume_discount[10-9.41]` |
| `full_stock_rejected` | Обнаружена | `tests.test_order_service::test_order_can_use_entire_stock` |
| `order_not_saved` | Обнаружена | `tests.test_idempotency::test_same_request_returns_original_order_and_notifies_once[request-1]` |
| `wrong_notification_recipient` | Обнаружена | `tests.test_notifications::test_notification_sent_once_after_success` |
| `duplicate_notification` | Обнаружена | `tests.test_idempotency::test_same_request_returns_original_order_and_notifies_once[request-1]` |
| `notification_error_escapes` | Обнаружена | `tests.test_idempotency::test_notification_failure_does_not_create_duplicate` |
| `missing_user_filter` | Обнаружена | `tests.test_order_repository::test_list_filters_user_and_sorts_by_id[sqlite]` |
| `reversed_order` | Обнаружена | `tests.test_order_repository::test_list_filters_user_and_sorts_by_id[sqlite]` |
| `missing_quantity_constraint` | Обнаружена | `tests.test_order_repository::test_sqlite_rejects_nonpositive_quantity[0]` |
