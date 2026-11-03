import sqlite3
from decimal import Decimal

import pytest

from app.models import Order
from app.service import OrderService
from app.sqlite_repo import SqliteOrderRepository, init_schema

pytestmark = pytest.mark.integration


def make_order(user_id=42, product_id=7, quantity=2, total="200.00"):
    return Order(None, user_id, product_id, quantity, Decimal(total))


def test_add_assigns_sequential_ids(order_repo):
    original = make_order()
    saved = [order_repo.add(original) for _ in range(3)]
    assert [order.id for order in saved] == [1, 2, 3]
    assert original.id is None
    assert all(order is not original for order in saved)


@pytest.mark.parametrize("total", ["46.08", "0.01", "0.00", "12345678901234567890.12"])
def test_get_preserves_every_field_and_decimal(order_repo, total):
    original = make_order(user_id=42, product_id=19, quantity=49, total=total)
    saved = order_repo.add(original)
    loaded = order_repo.get(saved.id)
    assert saved == Order(1, 42, 19, 49, Decimal(total))
    assert loaded == saved
    assert isinstance(loaded.total, Decimal)


def test_get_distinguishes_existing_ids(order_repo):
    first = order_repo.add(make_order(user_id=42, total="46.08"))
    second = order_repo.add(make_order(user_id=65, product_id=19, quantity=1, total="0.99"))
    assert order_repo.get(first.id) == first
    assert order_repo.get(second.id) == second


@pytest.mark.parametrize("order_id", [0, -1, 999])
def test_unknown_id_returns_none(order_repo, order_id):
    order_repo.add(make_order())
    assert order_repo.get(order_id) is None


def test_list_filters_user_and_sorts_by_id(order_repo):
    first = order_repo.add(make_order(user_id=42))
    other = order_repo.add(make_order(user_id=65))
    third = order_repo.add(make_order(user_id=42, product_id=19, quantity=49, total="46.08"))
    assert order_repo.list_for_user(42) == [first, third]
    assert order_repo.list_for_user(65) == [other]
    assert order_repo.list_for_user(999) == []


def test_empty_repository(order_repo):
    assert order_repo.get(1) is None
    assert order_repo.list_for_user(42) == []


@pytest.mark.parametrize("quantity", [0, -1])
def test_sqlite_rejects_nonpositive_quantity(conn, quantity):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total) VALUES (?, ?, ?, ?)",
            (42, 7, quantity, "0.00"),
        )


def test_sqlite_stores_total_as_text(conn):
    repo = SqliteOrderRepository(conn)
    saved = repo.add(make_order(total="12345678901234567890.12"))
    assert conn.execute("SELECT total, typeof(total) FROM orders WHERE id = ?", (saved.id,)).fetchone() == (
        "12345678901234567890.12", "text"
    )


def test_sqlite_add_is_committed(tmp_path):
    path = tmp_path / "orders.db"
    with sqlite3.connect(path) as writer:
        init_schema(writer)
        saved = SqliteOrderRepository(writer).add(make_order())
        with sqlite3.connect(path) as reader:
            assert SqliteOrderRepository(reader).get(saved.id) == saved


def test_schema_initialization_is_repeatable(conn):
    repo = SqliteOrderRepository(conn)
    saved = repo.add(make_order())
    init_schema(conn)
    assert repo.get(saved.id) == saved


def test_service_works_with_sqlite(conn, products, notifier, bulk_item):
    repo = SqliteOrderRepository(conn)
    service = OrderService(products, repo, notifier)
    order = service.place_order(user_id=42, product_id=bulk_item.id, quantity=49)
    assert order.total == Decimal("46.08")
    assert repo.get(order.id) == order
    assert repo.list_for_user(42) == [order]
    assert len(notifier.messages) == 1
    assert notifier.messages[0][0] == 42
