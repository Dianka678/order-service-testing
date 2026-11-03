"""ШАГ 3. Уведомления и ошибки зависимостей.

ЧТО НАПИСАТЬ (минимум):
  - после успешного заказа отправлено РОВНО ОДНО сообщение; получатель — тот user_id, что передали;
    текст содержит номер заказа и сумму.  Подсказка: возьмите user_id, отличный от product_id!
  - при ProductNotFound и при OutOfStock (параметризация) сообщений нет
  - уведомитель падает (FailingNotifier): place_order всё равно возвращает заказ, заказ сохранён
  - то же самое через unittest.mock: Mock(spec=Notifier) + send.side_effect = TimeoutError(...)
  - репозиторий заказов падает (BrokenOrderRepository): исключение уходит наружу, сообщений нет

Не забудьте пометить файл маркером:  pytestmark = pytest.mark.unit  (после импортов).
"""

from unittest.mock import Mock  # noqa: F401

import pytest

from app.errors import OutOfStock, ProductNotFound  # noqa: F401
from app.ports import Notifier  # noqa: F401
from app.service import OrderService  # noqa: F401
from tests.fakes import BrokenOrderRepository, FailingNotifier  # noqa: F401


def test_notification_sent_once_after_success(service, notifier, phone):
    service.place_order(user_id=42, product_id=phone.id, quantity=3)

    assert len(notifier.messages) == 1
    # TODO: проверьте получателя и содержимое текста


# TODO: остальные тесты по списку выше
