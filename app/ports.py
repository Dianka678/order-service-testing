"""Контракты зависимостей сервиса (порты). Изменять не нужно.

Сервису важно, ЧТО умеют зависимости, а не КАК они устроены:
в приложении сюда подставляются настоящие реализации, в тестах — fake/spy/mock.
"""

from __future__ import annotations

from typing import Protocol

from app.models import Order, Product


class ProductRepository(Protocol):
    def get(self, product_id: int) -> Product | None:
        """Вернуть товар или None, если такого нет."""


class OrderRepository(Protocol):
    def add(self, order: Order) -> Order:
        """Сохранить заказ и вернуть его копию с присвоенным id (1, 2, 3, ...)."""

    def get(self, order_id: int) -> Order | None:
        """Вернуть заказ по id или None."""

    def list_for_user(self, user_id: int) -> list[Order]:
        """Заказы одного пользователя в порядке возрастания id."""


class Notifier(Protocol):
    def send(self, user_id: int, text: str) -> None:
        """Отправить уведомление пользователю. Может бросить исключение."""
