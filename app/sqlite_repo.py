"""Репозиторий заказов на SQLite. ШАГ 4 практики."""

from __future__ import annotations

import sqlite3
from decimal import Decimal  # noqa: F401

from app.models import Order  # noqa: F401

# Схема уже готова — менять не нужно. Сумма хранится ТЕКСТОМ, чтобы не потерять копейки.
SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    total      TEXT    NOT NULL
)
"""

_COLUMNS = "id, user_id, product_id, quantity, total"


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(SCHEMA)
    conn.commit()


def _to_order(row: tuple) -> Order:
    """Превратить строку (id, user_id, product_id, quantity, total) в Order.

    total в базе — текст: превратите его в Decimal.
    """
    # TODO (шаг 4)
    raise NotImplementedError


class SqliteOrderRepository:
    """Те же методы, что и у порта OrderRepository (см. app/ports.py)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, order: Order) -> Order:
        """INSERT без id; вернуть копию заказа с id = cursor.lastrowid.

        Подсказки: dataclasses.replace(order, id=...), str(order.total), conn.commit().
        Всегда используйте параметры `?`, а не f-строки в SQL.
        """
        # TODO (шаг 4)
        raise NotImplementedError

    def get(self, order_id: int) -> Order | None:
        """SELECT по id; None, если строки нет."""
        # TODO (шаг 4)
        raise NotImplementedError

    def list_for_user(self, user_id: int) -> list[Order]:
        """Заказы пользователя, отсортированные по id по возрастанию."""
        # TODO (шаг 4)
        raise NotImplementedError
