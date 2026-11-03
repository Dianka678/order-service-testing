from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def calculate_discount(price: Decimal, percent: int) -> Decimal:
    if price < 0 or not 0 <= percent <= 100:
        raise ValueError("Некорректные данные")
    result = price * (100 - percent) / 100
    return result.quantize(CENT, rounding=ROUND_HALF_UP)


def volume_discount_percent(quantity: int) -> int:
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным")
    if quantity >= 50:
        return 10
    if quantity >= 10:
        return 5
    return 0


def calculate_total(unit_price: Decimal, quantity: int) -> Decimal:
    percent = volume_discount_percent(quantity)
    return calculate_discount(unit_price * quantity, percent)
