from dataclasses import replace

from app.models import Order, Product


class FakeProductRepository:
    def __init__(self, *products: Product) -> None:
        self._items = {product.id: product for product in products}

    def get(self, product_id: int) -> Product | None:
        return self._items.get(product_id)


class FakeOrderRepository:
    def __init__(self) -> None:
        self._items: dict[int, Order] = {}

    def add(self, order: Order) -> Order:
        saved = replace(order, id=len(self._items) + 1)
        self._items[saved.id] = saved
        return saved

    def get(self, order_id: int) -> Order | None:
        return self._items.get(order_id)

    def list_for_user(self, user_id: int) -> list[Order]:
        return [order for order in self.all if order.user_id == user_id]

    @property
    def all(self) -> list[Order]:
        return [self._items[key] for key in sorted(self._items)]


class NotifierSpy:
    def __init__(self) -> None:
        self.messages: list[tuple[int, str]] = []

    def send(self, user_id: int, text: str) -> None:
        self.messages.append((user_id, text))


class FailingNotifier:
    def send(self, user_id: int, text: str) -> None:
        raise TimeoutError("Нет ответа от уведомителя")


class BrokenOrderRepository(FakeOrderRepository):
    def add(self, order: Order) -> Order:
        raise ConnectionError("Хранилище недоступно")
