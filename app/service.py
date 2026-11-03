"""Сервис оформления заказа. ШАГИ 2, 3 и бонус практики."""

from __future__ import annotations

import logging

from app.errors import InvalidQuantity, OutOfStock, ProductNotFound  # noqa: F401
from app.models import Order, Product
from app.ports import Notifier, OrderRepository, ProductRepository
from app.pricing import calculate_total  # noqa: F401

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        products: ProductRepository,
        orders: OrderRepository,
        notifier: Notifier,
    ) -> None:
        # Зависимости приходят снаружи (DI): сервис сам ничего не создаёт.
        self._products = products
        self._orders = orders
        self._notifier = notifier

    def place_order(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        request_id: str | None = None,
    ) -> Order:
        """Оформить заказ. Порядок действий (важен!):

        1. quantity <= 0                    -> InvalidQuantity
        2. товара нет в репозитории         -> ProductNotFound
        3. на складе меньше, чем запрошено  -> OutOfStock  (ровно столько, сколько есть, — можно)
        4. сумма = calculate_total(цена, количество)
        5. сохранить заказ: self._orders.add(Order(None, user_id, product_id, quantity, total))
           (Order(id=None, ...) — репозиторий вернёт копию с присвоенным id)
        6. отправить уведомление (см. _notify) и вернуть сохранённый заказ

        Ошибки репозитория НЕ перехватываются: исключение уходит наружу,
        уведомление при этом не отправляется.

        БОНУС (идемпотентность): повторный вызов с тем же request_id возвращает тот же
        заказ, не создаёт новый и не отправляет второе уведомление. request_id=None —
        без дедупликации. Неуспешные попытки запоминать не нужно.
        """
        # TODO (шаги 2-3, бонус)
        raise NotImplementedError

    def _notify(self, order: Order, product: Product) -> None:
        """Отправить пользователю уведомление о заказе.

        Текст обязан содержать номер заказа и сумму, например:
        «Заказ №3: Телефон × 2, сумма 200.00». Получатель — order.user_id.
        Если отправка упала (любое исключение), заказ остаётся сохранённым:
        записать предупреждение в logger и НЕ пробрасывать ошибку.
        """
        # TODO (шаг 3)
        raise NotImplementedError
