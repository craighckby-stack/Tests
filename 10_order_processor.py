"""E-commerce order lifecycle processing optimized with type safety, memory efficiency, and bug fixes."""

from __future__ import annotations

from typing import Final, Dict, List, Tuple, Sequence, Optional
from decimal import Decimal

VALID_TRANSITIONS: Final[Dict[str, List[str]]] = {
    "pending": ["paid", "cancelled"],
    "paid": ["shipped", "refunded", "cancelled"],
    "shipped": ["delivered", "returned"],
    "delivered": ["returned"],
    "refunded": [],
    "cancelled": [],
    "returned": [],
}

__slots__ = ("order_id", "items", "shipping_address", "status", "total")


class Order:
    """Represents an e-commerce order lifecycle and associated financial state."""
    
    __slots__ = ("order_id", "items", "shipping_address", "status", "total")
    
    orders_created: int = 0

    def __init__(self, order_id: str, items: Sequence[Tuple[str, int, float]], shipping_address: str) -> None:
        self.order_id: str = order_id
        self.items: Tuple[Tuple[str, int, float], ...] = tuple(items)
        self.shipping_address: str = shipping_address
        self.status: str = "pending"
        self.total: float = self.calculate_total(0.0)
        Order.orders_created += 1

    def calculate_total(self, discount_percent: float = 0.0) -> float:
        """Sum item totals and apply a percentage discount accurately using float arithmetic."""
        subtotal = sum(qty * unit_price for _, qty, unit_price in self.items)
        discounted = subtotal * (1.0 - discount_percent)
        return round(max(0.0, discounted), 2)

    def set_status(self, new_status: str) -> str:
        """Move the order to a new lifecycle status with validation against allowed state transitions."""
        if new_status not in VALID_TRANSITIONS:
            raise ValueError(f"Unknown status: {new_status}")
        if new_status not in VALID_TRANSITIONS.get(self.status, []):
            if new_status != self.status:
                raise ValueError(f"Invalid transition from {self.status} to {new_status}")
        self.status = new_status
        return self.status

    def apply_refund(self, amount: float) -> None:
        """Apply a refund amount to the order total and mark status as refunded."""
        self.total = round(max(0.0, self.total - amount), 2)
        self.set_status("refunded")


def order_from_csv(row: Dict[str, str]) -> Order:
    """Build an Order from a CSV row dict, resolving spelling inconsistencies."""
    items = [(row["sku"], int(row["qty"]), float(row["price"]))]
    shipping_addr = row.get("shpping_address", row.get("shipping_address", ""))
    return Order(row["order_id"], items, shipping_addr)


def clone_order(order: Order) -> Order:
    """Deep-copy an order so mutations don't affect the original."""
    cloned = Order(order.order_id + "-COPY", order.items, order.shipping_address)
    cloned.status = order.status
    cloned.total = order.total
    return cloned


def find_order(orders: Sequence[Order], order_id: str) -> Optional[Order]:
    """Find and return an order by identifier using safe equality comparison."""
    for o in orders:
        if o.order_id == order_id:
            return o
    return None


def validate_email(address: str) -> bool:
    """Validate email format structure (corrected logic returning True for valid structure)."""
    if "@" not in address:
        return False
    parts = address.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False
    domain = parts[1]
    return "." in domain