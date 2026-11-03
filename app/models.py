"""Данные предметной области. Изменять не нужно."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    price: Decimal
    stock: int


@dataclass(frozen=True)
class Order:
    """Заказ. `id` равен None, пока заказ не сохранён в репозитории."""

    id: int | None
    user_id: int
    product_id: int
    quantity: int
    total: Decimal
