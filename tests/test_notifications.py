import logging
from unittest.mock import Mock

import pytest

from app.errors import InvalidQuantity, OutOfStock, ProductNotFound
from app.ports import Notifier
from app.service import OrderService
from tests.fakes import BrokenOrderRepository, FailingNotifier

pytestmark = pytest.mark.unit


def test_notification_sent_once_after_success(service, notifier, phone):
    service.place_order(user_id=65, product_id=phone.id, quantity=1)
    notifier.messages.clear()
    order = service.place_order(user_id=42, product_id=phone.id, quantity=3)
    assert len(notifier.messages) == 1
    user_id, text = notifier.messages[0]
    assert user_id == 42
    assert str(order.id) in text
    assert str(order.total) in text


@pytest.mark.parametrize(
    "product_id, quantity, error",
    [(999, 1, ProductNotFound), (7, 6, OutOfStock), (7, 0, InvalidQuantity), (7, -1, InvalidQuantity)],
)
def test_failed_orders_do_not_notify(service, notifier, orders, product_id, quantity, error):
    with pytest.raises(error):
        service.place_order(user_id=42, product_id=product_id, quantity=quantity)
    assert notifier.messages == []
    assert orders.all == []


def test_failing_notifier_keeps_saved_order(products, orders, phone, caplog):
    service = OrderService(products, orders, FailingNotifier())
    with caplog.at_level(logging.WARNING):
        order = service.place_order(user_id=42, product_id=phone.id, quantity=2)
    assert orders.get(order.id) == order
    assert len(orders.all) == 1
    assert any(record.levelno >= logging.WARNING for record in caplog.records)


@pytest.mark.parametrize("error", [TimeoutError("Таймаут"), RuntimeError("Ошибка отправки"), ValueError("Ошибка данных")])
def test_mock_notifier_failure_does_not_escape(products, orders, phone, error):
    notifier = Mock(spec=Notifier)
    notifier.send.side_effect = error
    service = OrderService(products, orders, notifier)
    order = service.place_order(user_id=42, product_id=phone.id, quantity=2)
    assert orders.get(order.id) == order
    notifier.send.assert_called_once()
    recipient, text = notifier.send.call_args.args
    assert recipient == 42
    assert str(order.id) in text
    assert str(order.total) in text


def test_repository_failure_is_propagated_without_notification(products, notifier, phone):
    orders = BrokenOrderRepository()
    service = OrderService(products, orders, notifier)
    with pytest.raises(ConnectionError):
        service.place_order(user_id=42, product_id=phone.id, quantity=1)
    assert orders.all == []
    assert notifier.messages == []


def test_notification_happens_after_persistence(products, orders, phone):
    notifier = Mock(spec=Notifier)
    observed = []

    def observe(user_id, text):
        observed.append((user_id, orders.list_for_user(user_id)))

    notifier.send.side_effect = observe
    service = OrderService(products, orders, notifier)
    order = service.place_order(user_id=42, product_id=phone.id, quantity=1)
    assert observed == [(42, [order])]
    notifier.send.assert_called_once()
