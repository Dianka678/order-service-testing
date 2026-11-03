"""ШАГ 2. Тесты OrderService с fake-репозиториями (app/service.py).

ЧТО НАПИСАТЬ (минимум):
  - успешный заказ: проверьте поля заказа (id, user_id, product_id, quantity, total)
    И ТО, ЧТО ЗАКАЗ ЛЕЖИТ В РЕПОЗИТОРИИ
  - товар не найден -> ProductNotFound, в репозитории пусто
  - запрошено больше, чем на складе -> OutOfStock, в репозитории пусто
  - заказ ровно на весь остаток склада — проходит
  - quantity = 0 и отрицательное -> InvalidQuantity (параметризация), в репозитории пусто
  - сумма со скидкой за объём: параметризованный тест (количество, ожидаемая сумма) —
    возьмите товар с ценой 0.99 и количества 1, 9, 10, 49, 50, 100
  - два заказа подряд получают id 1 и 2

Не забудьте пометить файл маркером:  pytestmark = pytest.mark.unit  (после импортов).
"""

from decimal import Decimal  # noqa: F401

import pytest

from app.errors import InvalidQuantity, OutOfStock, ProductNotFound  # noqa: F401


# Пример: фикстуры service / orders / phone приходят из conftest.py (после того как вы их допишете).
def test_successful_order_is_saved(service, orders, phone):
    order = service.place_order(user_id=1, product_id=phone.id, quantity=2)

    assert order.total == Decimal("200.00")
    # TODO: проверьте остальные поля и что orders.get(order.id) == order


# TODO: остальные тесты по списку выше
