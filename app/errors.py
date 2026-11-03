"""Ошибки оформления заказа. Изменять не нужно."""

from __future__ import annotations


class OrderError(Exception):
    """Базовая ошибка прикладного уровня."""


class InvalidQuantity(OrderError):
    def __init__(self, quantity: int) -> None:
        super().__init__(f"Количество должно быть положительным, получено {quantity}")
        self.quantity = quantity


class ProductNotFound(OrderError):
    def __init__(self, product_id: int) -> None:
        super().__init__(f"Товар {product_id} не найден")
        self.product_id = product_id


class OutOfStock(OrderError):
    def __init__(self, product_id: int, requested: int, available: int) -> None:
        super().__init__(
            f"Товара {product_id} не хватает: запрошено {requested}, на складе {available}"
        )
        self.product_id = product_id
        self.requested = requested
        self.available = available
