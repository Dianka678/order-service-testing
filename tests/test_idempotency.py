from dataclasses import replace
from unittest.mock import Mock

import pytest

from app.errors import InvalidQuantity, OutOfStock, ProductNotFound
from app.ports import OrderRepository
from app.service import OrderService
from tests.fakes import FakeOrderRepository, FakeProductRepository, FailingNotifier

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("request_id", ["request-1", ""])
def test_same_request_returns_original_order_and_notifies_once(service, orders, notifier, phone, request_id):
    first = service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id=request_id)
    second = service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id=request_id)
    assert second == first
    assert orders.all == [first]
    assert len(notifier.messages) == 1


@pytest.mark.parametrize("request_ids", [("request-1", "request-2"), (None, None)])
def test_distinct_requests_create_distinct_orders(service, orders, notifier, phone, request_ids):
    first = service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id=request_ids[0])
    second = service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id=request_ids[1])
    assert (first.id, second.id) == (1, 2)
    assert orders.all == [first, second]
    assert len(notifier.messages) == 2


@pytest.mark.parametrize(
    "product_id, quantity, error", [(7, 6, OutOfStock), (999, 1, ProductNotFound), (7, 0, InvalidQuantity)]
)
def test_failed_attempt_is_not_cached(service, orders, notifier, phone, product_id, quantity, error):
    with pytest.raises(error):
        service.place_order(user_id=42, product_id=product_id, quantity=quantity, request_id="retry")
    assert orders.all == []
    assert notifier.messages == []
    order = service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id="retry")
    assert orders.all == [order]
    assert len(notifier.messages) == 1


def test_retry_after_restock_uses_same_request_id(phone, orders, notifier):
    products = Mock()
    products.get.side_effect = [phone, replace(phone, stock=10)]
    service = OrderService(products, orders, notifier)
    with pytest.raises(OutOfStock):
        service.place_order(user_id=42, product_id=phone.id, quantity=6, request_id="restock")
    order = service.place_order(user_id=42, product_id=phone.id, quantity=6, request_id="restock")
    assert order.quantity == 6
    assert orders.all == [order]
    assert len(notifier.messages) == 1


def test_repository_failure_is_not_cached(products, notifier, phone):
    storage = FakeOrderRepository()
    orders = Mock(spec=OrderRepository)
    attempts = 0

    def save(order):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ConnectionError("База недоступна")
        return storage.add(order)

    orders.add.side_effect = save
    service = OrderService(products, orders, notifier)
    with pytest.raises(ConnectionError):
        service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id="retry")
    assert notifier.messages == []
    order = service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id="retry")
    assert order.id == 1
    assert storage.all == [order]
    assert orders.add.call_count == 2
    assert len(notifier.messages) == 1


def test_notification_failure_does_not_create_duplicate(products, orders, phone):
    notifier = Mock()
    notifier.send.side_effect = TimeoutError("Таймаут")
    service = OrderService(products, orders, notifier)
    first = service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id="notify")
    second = service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id="notify")
    assert second == first
    assert orders.all == [first]
    notifier.send.assert_called_once()


def test_services_do_not_share_request_cache(phone):
    products = FakeProductRepository(phone)
    first_orders = FakeOrderRepository()
    second_orders = FakeOrderRepository()
    first_service = OrderService(products, first_orders, FailingNotifier())
    second_service = OrderService(products, second_orders, FailingNotifier())
    first = first_service.place_order(user_id=42, product_id=phone.id, quantity=1, request_id="same")
    second = second_service.place_order(user_id=65, product_id=phone.id, quantity=2, request_id="same")
    assert first.user_id == 42
    assert second.user_id == 65
    assert first_orders.all == [first]
    assert second_orders.all == [second]
