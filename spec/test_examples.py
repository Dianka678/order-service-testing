"""Публичные примеры из задания — «спецификация в виде тестов».

Запуск:  python -m pytest spec -q
Пока ваша реализация не готова, эти проверки красные; когда всё сделано — зелёные.
Это НЕ все проверки: проверяющие запускают более полный набор скрытых тестов.
"""

import sqlite3
from decimal import Decimal

from app.models import Order, Product
from app.pricing import calculate_total, volume_discount_percent
from app.service import OrderService
from app.sqlite_repo import SqliteOrderRepository, init_schema


class _Products:
    def __init__(self, *items):
        self._items = {p.id: p for p in items}

    def get(self, pid):
        return self._items.get(pid)


class _Orders:
    def __init__(self):
        self.saved = []

    def add(self, order):
        from dataclasses import replace

        saved = replace(order, id=len(self.saved) + 1)
        self.saved.append(saved)
        return saved


class _Spy:
    def __init__(self):
        self.messages = []

    def send(self, user_id, text):
        self.messages.append((user_id, text))


def test_volume_discount_examples():
    assert [volume_discount_percent(q) for q in (1, 10, 50)] == [0, 5, 10]


def test_total_example():
    assert calculate_total(Decimal("100.00"), 10) == Decimal("950.00")


def test_place_order_example():
    spy = _Spy()
    service = OrderService(_Products(Product(7, "Телефон", Decimal("100.00"), 5)), _Orders(), spy)
    order = service.place_order(user_id=1, product_id=7, quantity=2)
    assert order.total == Decimal("200.00")
    assert spy.messages and spy.messages[0][0] == 1


def test_sqlite_example():
    conn = sqlite3.connect(":memory:")
    init_schema(conn)
    repo = SqliteOrderRepository(conn)
    saved = repo.add(Order(None, 1, 7, 2, Decimal("9.41")))
    assert saved.id == 1 and repo.get(1) == saved
