# Константы
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21

# Купоны и скидки
COUPON_SAVE10_RATE = 0.10
COUPON_SAVE20_RATE = 0.20
COUPON_SAVE20_FALLBACK_RATE = 0.05
COUPON_SAVE20_MIN_SUBTOTAL = 200
COUPON_VIP_DISCOUNT = 50
COUPON_VIP_MIN_SUBTOTAL = 100
COUPON_VIP_FALLBACK_DISCOUNT = 10


def parse_request(request: dict) -> tuple:
    """Извлекает данные из запроса."""
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency", DEFAULT_CURRENCY)
    return user_id, items, coupon, currency


def validate_request(user_id, items) -> None:
    """Валидирует обязательные поля запроса."""
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    for item in items:
        _validate_item(item)


def _validate_item(item: dict) -> None:
    """Валидирует отдельный товар."""
    if "price" not in item or "qty" not in item:
        raise ValueError("item must have price and qty")
    if item["price"] <= 0:
        raise ValueError("price must be positive")
    if item["qty"] <= 0:
        raise ValueError("qty must be positive")


def calculate_subtotal(items: list) -> int:
    """Считает сумму всех товаров без скидок."""
    return sum(item["price"] * item["qty"] for item in items)


def calculate_discount(coupon: str, subtotal: int) -> int:
    """Вычисляет скидку на основе купона и суммы заказа."""
    if not coupon:
        return 0

    if coupon == "SAVE10":
        return int(subtotal * COUPON_SAVE10_RATE)

    if coupon == "SAVE20":
        rate = COUPON_SAVE20_RATE if subtotal >= COUPON_SAVE20_MIN_SUBTOTAL else COUPON_SAVE20_FALLBACK_RATE
        return int(subtotal * rate)

    if coupon == "VIP":
        return COUPON_VIP_DISCOUNT if subtotal >= COUPON_VIP_MIN_SUBTOTAL else COUPON_VIP_FALLBACK_DISCOUNT

    raise ValueError("unknown coupon")


def calculate_tax(amount: int) -> int:
    """Вычисляет налог от суммы."""
    return int(amount * TAX_RATE)


def generate_order_id(user_id, items_count: int) -> str:
    """Генерирует идентификатор заказа."""
    return f"{user_id}-{items_count}-X"


def process_checkout(request: dict) -> dict:
    """Обрабатывает оформление заказа."""
    user_id, items, coupon, currency = parse_request(request)
    validate_request(user_id, items)

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(coupon, subtotal)
    total_after_discount = max(subtotal - discount, 0)
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    return {
        "order_id": generate_order_id(user_id, len(items)),
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
