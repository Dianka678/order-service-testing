import sqlite3
from dataclasses import replace
from decimal import Decimal

from app.models import Order

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
    return Order(row[0], row[1], row[2], row[3], Decimal(row[4]))


class SqliteOrderRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, order: Order) -> Order:
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO orders (user_id, product_id, quantity, total) VALUES (?, ?, ?, ?)",
                (order.user_id, order.product_id, order.quantity, str(order.total)),
            )
        return replace(order, id=cursor.lastrowid)

    def get(self, order_id: int) -> Order | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        return None if row is None else _to_order(row)

    def list_for_user(self, user_id: int) -> list[Order]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM orders WHERE user_id = ? ORDER BY id", (user_id,)
        ).fetchall()
        return [_to_order(row) for row in rows]
