"""ШАГ 4. Контрактные тесты репозитория заказов: fake И настоящая SQLite.

Тесты принимают фикстуру order_repo (см. conftest.py) и поэтому выполняются дважды —
для FakeOrderRepository и для SqliteOrderRepository. Если оба варианта зелёные,
fake ведёт себя как настоящее хранилище. Но SQL-ограничения fake не воспроизводит —
их проверяет отдельный тест на conn.

ЧТО НАПИСАТЬ (минимум):
  - add присваивает id 1, 2, 3
  - get возвращает то, что сохранили (равенство заказов); сумма сохраняется точно (Decimal("46.08"))
  - get для несуществующего id -> None
  - list_for_user: заказы только своего пользователя, по порядку id (создайте заказы ДВУХ пользователей,
    минимум два у одного)
  - список для неизвестного пользователя пуст
  - только SQLite: вставка строки с quantity = 0 напрямую через conn.execute(...) -> sqlite3.IntegrityError

Не забудьте пометить файл маркером:  pytestmark = pytest.mark.integration  (после импортов).
"""

import sqlite3  # noqa: F401
from decimal import Decimal

import pytest

from app.models import Order


def make_order(user_id=1, product_id=7, quantity=2, total="200.00"):
    return Order(None, user_id, product_id, quantity, Decimal(total))


def test_add_assigns_sequential_ids(order_repo):
    first = order_repo.add(make_order())
    second = order_repo.add(make_order())

    assert (first.id, second.id) == (1, 2)


# TODO: остальные тесты по списку выше
