import sqlite3
from decimal import Decimal

import pytest

from app.models import Product
from app.service import OrderService
from app.sqlite_repo import SqliteOrderRepository, init_schema
from tests.fakes import FakeOrderRepository, FakeProductRepository, NotifierSpy


@pytest.fixture
def phone():
    return Product(id=7, name="Телефон", price=Decimal("100.00"), stock=5)


@pytest.fixture
def bulk_item():
    return Product(id=19, name="Карандаш", price=Decimal("0.99"), stock=100)


@pytest.fixture
def products(phone, bulk_item):
    return FakeProductRepository(phone, bulk_item)


@pytest.fixture
def orders():
    return FakeOrderRepository()


@pytest.fixture
def notifier():
    return NotifierSpy()


@pytest.fixture
def service(products, orders, notifier):
    return OrderService(products, orders, notifier)


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    init_schema(connection)
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture(params=["fake", "sqlite"])
def order_repo(request):
    if request.param == "fake":
        return FakeOrderRepository()
    return SqliteOrderRepository(request.getfixturevalue("conn"))
