import logging

from app.errors import InvalidQuantity, OutOfStock, ProductNotFound
from app.models import Order, Product
from app.ports import Notifier, OrderRepository, ProductRepository
from app.pricing import calculate_total

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        products: ProductRepository,
        orders: OrderRepository,
        notifier: Notifier,
    ) -> None:
        self._products = products
        self._orders = orders
        self._notifier = notifier
        self._requests: dict[str, Order] = {}

    def place_order(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        request_id: str | None = None,
    ) -> Order:
        if request_id is not None and request_id in self._requests:
            return self._requests[request_id]
        if quantity <= 0:
            raise InvalidQuantity(quantity)
        product = self._products.get(product_id)
        if product is None:
            raise ProductNotFound(product_id)
        if product.stock < quantity:
            raise OutOfStock(product_id, quantity, product.stock)
        total = calculate_total(product.price, quantity)
        order = self._orders.add(Order(None, user_id, product_id, quantity, total))
        if request_id is not None:
            self._requests[request_id] = order
        self._notify(order, product)
        return order

    def _notify(self, order: Order, product: Product) -> None:
        text = f"Заказ №{order.id}: {product.name} × {order.quantity}, сумма {order.total:.2f}"
        try:
            self._notifier.send(order.user_id, text)
        except Exception:
            logger.warning("Не удалось отправить уведомление о заказе %s", order.id, exc_info=True)
