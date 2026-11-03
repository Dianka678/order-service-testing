from decimal import Decimal

import pytest

from app.pricing import calculate_discount, calculate_total, volume_discount_percent

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "percent, expected", [(0, "1000.00"), (10, "900.00"), (50, "500.00"), (100, "0.00")]
)
def test_discount_values(percent, expected):
    assert calculate_discount(Decimal("1000.00"), percent) == Decimal(expected)


@pytest.mark.parametrize("percent", [0, 10, 50, 100])
def test_zero_price_is_valid(percent):
    assert calculate_discount(Decimal("0.00"), percent) == Decimal("0.00")


@pytest.mark.parametrize("percent", [-1, 101])
def test_invalid_discount_percent(percent):
    with pytest.raises(ValueError):
        calculate_discount(Decimal("100.00"), percent)


@pytest.mark.parametrize("percent", [0, 50, 100])
def test_negative_price_is_rejected(percent):
    with pytest.raises(ValueError):
        calculate_discount(Decimal("-0.01"), percent)


@pytest.mark.parametrize(
    "price, percent, expected",
    [("9.90", 5, "9.41"), ("0.01", 50, "0.01"), ("1.005", 0, "1.01"), ("1.004", 0, "1.00")],
)
def test_discount_rounds_half_up(price, percent, expected):
    result = calculate_discount(Decimal(price), percent)
    assert result == Decimal(expected)
    assert result.as_tuple().exponent == -2


@pytest.mark.parametrize(
    "quantity, expected", [(1, 0), (9, 0), (10, 5), (11, 5), (49, 5), (50, 10), (51, 10), (1000, 10)]
)
def test_volume_discount_boundaries(quantity, expected):
    assert volume_discount_percent(quantity) == expected


@pytest.mark.parametrize("quantity", [0, -1, -50])
def test_nonpositive_quantity_is_rejected(quantity):
    with pytest.raises(ValueError):
        volume_discount_percent(quantity)


@pytest.mark.parametrize(
    "price, quantity, expected",
    [
        ("100.00", 1, "100.00"),
        ("100.00", 10, "950.00"),
        ("100.00", 50, "4500.00"),
        ("0.99", 1, "0.99"),
        ("0.99", 9, "8.91"),
        ("0.99", 10, "9.41"),
        ("0.99", 49, "46.08"),
        ("0.99", 50, "44.55"),
        ("0.99", 100, "89.10"),
        ("0.00", 50, "0.00"),
    ],
)
def test_total(price, quantity, expected):
    result = calculate_total(Decimal(price), quantity)
    assert isinstance(result, Decimal)
    assert result == Decimal(expected)


@pytest.mark.parametrize("quantity", [0, -1])
def test_total_rejects_nonpositive_quantity(quantity):
    with pytest.raises(ValueError):
        calculate_total(Decimal("1.00"), quantity)


def test_total_rejects_negative_price():
    with pytest.raises(ValueError):
        calculate_total(Decimal("-1.00"), 10)
