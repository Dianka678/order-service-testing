"""Тестовые двойники (ШАГИ 2-3). Всё, что нужно сервису, но без базы и без настоящей отправки.

Эти классы должны подходить под контракты из app/ports.py, но НЕ наследуются от них.
"""

from __future__ import annotations

from dataclasses import replace

from app.models import Order, Product


class FakeProductRepository:
    """Fake: товары лежат в словаре. Пример готов — используйте как образец."""

    def __init__(self, *products: Product) -> None:
        self._items = {p.id: p for p in products}

    def get(self, product_id: int) -> Product | None:
        return self._items.get(product_id)


class FakeOrderRepository:
    """Fake заказов (шаг 2). Присваивает id 1, 2, 3, … — как это делает база.

    TODO: реализуйте add / get / list_for_user.
    Подсказка: dataclasses.replace(order, id=...) создаёт копию заказа с новым id;
    список для пользователя — в порядке возрастания id.
    Добавьте также свойство/метод, возвращающее все сохранённые заказы: оно пригодится в проверках.
    """

    def __init__(self) -> None:
        self._items: dict[int, Order] = {}

    def add(self, order: Order) -> Order:
        raise NotImplementedError  # TODO

    def get(self, order_id: int) -> Order | None:
        raise NotImplementedError  # TODO

    def list_for_user(self, user_id: int) -> list[Order]:
        raise NotImplementedError  # TODO


class NotifierSpy:
    """Spy (шаг 3): запоминает, что и кому «отправили», вместо настоящей отправки.

    TODO: в send добавляйте (user_id, text) в список self.messages.
    """

    def __init__(self) -> None:
        self.messages: list[tuple[int, str]] = []

    def send(self, user_id: int, text: str) -> None:
        raise NotImplementedError  # TODO


class FailingNotifier:
    """Stub (шаг 3): уведомление не доходит. TODO: send должен бросать исключение (например, TimeoutError)."""

    def send(self, user_id: int, text: str) -> None:
        raise NotImplementedError  # TODO


class BrokenOrderRepository(FakeOrderRepository):
    """Хранилище заказов, которое «падает» при сохранении (шаг 3). TODO: add бросает ConnectionError."""

    def add(self, order: Order) -> Order:
        raise NotImplementedError  # TODO
