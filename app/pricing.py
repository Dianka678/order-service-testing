"""Расчёт цены. ШАГ 1 практики."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def calculate_discount(price: Decimal, percent: int) -> Decimal:
    """Цена после скидки `percent` процентов, округлённая до копеек (half-up).

    Уже реализовано: ваша задача — написать для неё тесты (tests/test_pricing.py).
    """
    if price < 0 or not 0 <= percent <= 100:
        raise ValueError("Некорректные данные")
    result = price * (100 - percent) / 100
    return result.quantize(CENT, rounding=ROUND_HALF_UP)


def volume_discount_percent(quantity: int) -> int:
    """Скидка за объём в процентах.

    1-9 шт. -> 0, 10-49 шт. -> 5, 50 и больше -> 10.
    Количество <= 0 -> ValueError.
    """
    # TODO (шаг 1): реализуйте по описанию выше
    raise NotImplementedError


def calculate_total(unit_price: Decimal, quantity: int) -> Decimal:
    """Сумма заказа: цена за единицу × количество, затем скидка за объём.

    Используйте volume_discount_percent и calculate_discount.
    Пример: calculate_total(Decimal("100.00"), 10) == Decimal("950.00").
    """
    # TODO (шаг 1)
    raise NotImplementedError
