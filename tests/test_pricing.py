"""ШАГ 1. Тесты расчёта цены (app/pricing.py).

Файл должен называться именно так: его запускают проверяющие.

ЧТО НАПИСАТЬ (минимум):
  calculate_discount
    - значения 0 / 10 / 50 / 100 % одним @pytest.mark.parametrize
    - цена 0 допустима
    - -1 % и 101 % -> ValueError;  отрицательная цена -> ValueError
    - округление: случай, где результат ровно «посередине» (подберите цену и процент!)
  volume_discount_percent
    - границы 1, 9, 10, 11, 49, 50, 51 (параметризация)
    - 0 и отрицательное количество -> ValueError
  calculate_total
    - несколько наборов (цена, количество, ожидаемая сумма), включая количество 1, 10 и 50

Не забудьте пометить файл маркером:  pytestmark = pytest.mark.unit  (после импортов).
"""

from decimal import Decimal

import pytest

from app.pricing import calculate_discount, calculate_total, volume_discount_percent  # noqa: F401

D = Decimal


# Пример в стиле Arrange–Act–Assert. Остальное — ваше.
@pytest.mark.parametrize(
    "percent, expected",
    [(0, "1000.00"), (10, "900.00")],  # TODO: добавьте 50 и 100
)
def test_discount_values(percent, expected):
    assert calculate_discount(D("1000"), percent) == D(expected)


# TODO: остальные тесты по списку выше
