"""Общие фикстуры (ШАГИ 2-4). pytest находит их по имени аргумента теста.

Нужно не менее 3 фикстур. Рекомендуемый набор — ниже; одна уже написана.
"""

from __future__ import annotations

import sqlite3  # noqa: F401
from decimal import Decimal

import pytest

from app.models import Product
from app.service import OrderService  # noqa: F401
from app.sqlite_repo import SqliteOrderRepository, init_schema  # noqa: F401
from tests.fakes import FakeOrderRepository, FakeProductRepository, NotifierSpy  # noqa: F401


@pytest.fixture
def phone() -> Product:
    """Готовый пример: товар с известными данными. Берите значения из него в тестах."""
    return Product(id=7, name="Телефон", price=Decimal("100.00"), stock=5)


# TODO (шаг 2): ещё один товар с большим запасом и «неудобной» ценой (например, 0.99) — для скидок за объём
# @pytest.fixture
# def bulk_item() -> Product: ...

# TODO (шаг 2): products -> FakeProductRepository(phone, bulk_item)
# TODO (шаг 2): orders   -> FakeOrderRepository()
# TODO (шаг 3): notifier -> NotifierSpy()
# TODO (шаг 2): service  -> OrderService(products, orders, notifier)   # фикстуры могут зависеть друг от друга

# TODO (шаг 4): conn — соединение SQLite в памяти с подготовкой и очисткой:
#
# @pytest.fixture
# def conn():
#     connection = sqlite3.connect(":memory:")
#     init_schema(connection)
#     yield connection          # до yield — подготовка, после — очистка
#     connection.close()

# TODO (шаг 4): order_repo — ОДНА фикстура с params=["fake", "sqlite"]:
# возвращает FakeOrderRepository() или SqliteOrderRepository(conn) в зависимости от request.param.
# Тогда любой тест с аргументом order_repo выполнится дважды — для fake и для SQLite.
