from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.errors import InvalidQuantity, OutOfStock, ProductNotFound
from app.models import Product
from app.ports import ProductRepository
from app.service import OrderService
from tests.fakes import FakeProductRepository

pytestmark = pytest.mark.unit


def test_successful_order_is_saved(service, orders, phone):
    order = service.place_order(user_id=42, product_id=phone.id, quantity=2)
    assert (order.id, order.user_id, order.product_id, order.quantity, order.total) == (
        1, 42, 7, 2, Decimal("200.00")
    )
    assert orders.get(order.id) == order
    assert orders.all == [order]


def test_missing_product_leaves_repository_empty(service, orders):
    with pytest.raises(ProductNotFound) as error:
        service.place_order(user_id=42, product_id=999, quantity=1)
    assert error.value.product_id == 999
    assert orders.all == []


@pytest.mark.parametrize("quantity", [6, 100])
def test_insufficient_stock_leaves_repository_empty(service, orders, phone, quantity):
    with pytest.raises(OutOfStock) as error:
        service.place_order(user_id=42, product_id=phone.id, quantity=quantity)
    assert (error.value.product_id, error.value.requested, error.value.available) == (7, quantity, 5)
    assert orders.all == []


def test_order_can_use_entire_stock(service, orders, phone):
    order = service.place_order(user_id=42, product_id=phone.id, quantity=5)
    assert order.quantity == 5
    assert order.total == Decimal("500.00")
    assert orders.get(order.id) == order


@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_invalid_quantity_leaves_repository_empty(service, orders, phone, quantity):
    with pytest.raises(InvalidQuantity) as error:
        service.place_order(user_id=42, product_id=phone.id, quantity=quantity)
    assert error.value.quantity == quantity
    assert orders.all == []


@pytest.mark.parametrize("quantity", [0, -1])
def test_quantity_is_checked_before_product_lookup(orders, notifier, quantity):
    products = Mock(spec=ProductRepository)
    products.get.side_effect = AssertionError("Товар не должен запрашиваться")
    service = OrderService(products, orders, notifier)
    with pytest.raises(InvalidQuantity):
        service.place_order(user_id=42, product_id=999, quantity=quantity)
    products.get.assert_not_called()
    assert orders.all == []
    assert notifier.messages == []


@pytest.mark.parametrize(
    "quantity, expected", [(1, "0.99"), (9, "8.91"), (10, "9.41"), (49, "46.08"), (50, "44.55"), (100, "89.10")]
)
def test_order_total_includes_volume_discount(service, orders, bulk_item, quantity, expected):
    order = service.place_order(user_id=42, product_id=bulk_item.id, quantity=quantity)
    assert order.total == Decimal(expected)
    assert order.quantity == quantity
    assert order.product_id == bulk_item.id
    assert orders.get(order.id) == order


def test_consecutive_orders_get_different_ids(service, orders, phone):
    first = service.place_order(user_id=42, product_id=phone.id, quantity=1)
    second = service.place_order(user_id=43, product_id=phone.id, quantity=2)
    assert (first.id, second.id) == (1, 2)
    assert orders.all == [first, second]


def test_zero_stock_is_rejected(orders, notifier):
    product = Product(23, "Нет в наличии", Decimal("3.00"), 0)
    service = OrderService(FakeProductRepository(product), orders, notifier)
    with pytest.raises(OutOfStock):
        service.place_order(user_id=42, product_id=23, quantity=1)
    assert orders.all == []
    assert notifier.messages == []


def test_product_repository_error_is_propagated(orders, notifier):
    products = Mock(spec=ProductRepository)
    products.get.side_effect = ConnectionError("Каталог недоступен")
    service = OrderService(products, orders, notifier)
    with pytest.raises(ConnectionError):
        service.place_order(user_id=42, product_id=7, quantity=1)
    assert orders.all == []
    assert notifier.messages == []
