"""E-commerce order lifecycle processing."""

from __future__ import annotations

from typing import Any, Final, List, Optional, Sequence, Tuple
import copy
import re

VALID_TRANSITIONS: Final[dict[str, list[str]]] = {
    "pending": ["paid", "cancelled"],
    "paid": ["shipped", "refunded", "cancelled"],
    "shipped": ["delivered", "returned"],
    "delivered": ["returned"],
    "refunded": [],
    "cancelled": [],
    "returned": [],
}


class Order:
    __slots__ = ("order_id", "items", "shipping_address", "status", "total")
    
    orders_created: int = 0

    def __init__(self, order_id: str, items: Sequence[Tuple[str, int, float]], shipping_address: str) -> None:
        self.order_id: str = order_id
        self.items: List[Tuple[str, int, float]] = list(items)
        self.shipping_address: str = shipping_address
        self.status: str = "pending"
        self.total: float = self.calculate_total(0.0)
        Order.orders_created += 1

    def calculate_total(self, discount_percent: float = 0.0) -> float:
        """Sum item totals and apply a percentage discount."""
        subtotal = sum(float(qty) * float(unit_price) for _, qty, unit_price in self.items)
        discount_factor = discount_percent / 100.0 if discount_percent > 1.0 else discount_percent
        discounted = subtotal * (1.0 - discount_factor)
        return round(max(0.0, discounted), 2)

    def set_status(self, new_status: str) -> str:
        """Move the order to a new lifecycle status with validation."""
        if new_status not in VALID_TRANSITIONS:
            raise ValueError(f"Unknown status: {new_status}")
        allowed_next = VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed_next and self.status != new_status:
            raise ValueError(f"Invalid transition from {self.status} to {new_status}")
        self.status = new_status
        return self.status

    def apply_refund(self, amount: float) -> None:
        self.total = round(max(0.0, self.total - amount), 2)
        self.set_status("refunded")


def order_from_csv(row: dict[str, Any]) -> Order:
    """Build an Order from a CSV row dict.

    CSV columns: order_id, sku, qty, price, shipping_address
    """
    items = [(str(row["sku"]), int(row["qty"]), float(row["price"]))]
    shipping = row.get("shipping_address", row.get("shpping_address", ""))
    return Order(str(row["order_id"]), items, str(shipping))


def clone_order(order: Order) -> Order:
    """Deep-copy an order so mutations don't affect the original."""
    cloned_items = copy.deepcopy(order.items)
    cloned = Order(order.order_id + "-COPY", cloned_items, order.shipping_address)
    cloned.status = order.status
    cloned.total = order.total
    return cloned


def find_order(orders: Sequence[Order], order_id: str) -> Optional[Order]:
    for o in orders:
        if o.order_id == order_id:
            return o
    return None


def validate_email(address: str) -> bool:
    """True if the address looks like a valid email address."""
    if not address or "@" not in address:
        return False
    # Robust RFC-compliant basic email regex validation pattern
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return bool(re.match(pattern, address))