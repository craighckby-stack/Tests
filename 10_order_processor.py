"""E-commerce order lifecycle processing optimized with type-safety, memory efficiency, and robust error handling."""

from __future__ import annotations

from typing import Final, Sequence, TypeAlias

# Type Aliases
ItemID: TypeAlias = str
Quantity: TypeAlias = int
UnitPrice: TypeAlias = float
ItemTuple: TypeAlias = tuple[ItemID, Quantity, UnitPrice]

VALID_TRANSITIONS: Final[dict[str, tuple[str, ...]]] = {
    "pending": ("paid", "cancelled"),
    "paid": ("shipped", "refunded", "cancelled"),
    "shipped": ("delivered", "returned"),
    "delivered": ("returned",),
    "refunded": (),
    "cancelled": (),
    "returned": (),
}


class Order:
    __slots__ = ("_order_id", "_items", "_shipping_address", "_status", "_total")
    
    orders_created: int = 0

    def __init__(self, order_id: str, items: Sequence[ItemTuple], shipping_address: str) -> None:
        self._order_id: str = order_id
        self._items: tuple[ItemTuple, ...] = tuple(items)
        self._shipping_address: str = shipping_address
        self._status: str = "pending"
        self._total: float = self._compute_initial_total()
        Order.orders_created += 1

    @property
    def order_id(self) -> str:
        return self._order_id

    @property
    def items(self) -> tuple[ItemTuple, ...]:
        return self._items

    @property
    def shipping_address(self) -> str:
        return self._shipping_address

    @property
    def status(self) -> str:
        return self._status

    @property
    def total(self) -> float:
        return self._total

    @total.setter
    def total(self, value: float) -> None:
        self._total = float(value)

    def _compute_initial_total(self) -> float:
        subtotal = sum(qty * unit_price for _, qty, unit_price in self._items)
        return round(subtotal, 2)

    def calculate_total(self, discount_percent: float = 0.0) -> float:
        """Sum item totals and apply a percentage discount."""
        if not (0.0 <= discount_percent <= 1.0):
            raise ValueError("Discount percent must be between 0.0 and 1.0")
        subtotal = sum(qty * unit_price for _, qty, unit_price in self._items)
        total = subtotal * (1.0 - discount_percent)
        return round(total, 2)

    def set_status(self, new_status: str) -> str:
        """Move the order to a new lifecycle status with validation."""
        allowed = VALID_TRANSITIONS.get(self._status)
        if allowed is None or new_status not in allowed:
            raise ValueError(f"Invalid transition from '{self._status}' to '{new_status}'")
        self._status = new_status
        return self._status

    def apply_refund(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Refund amount cannot be negative")
        self._total = round(max(0.0, self._total - amount), 2)
        self.set_status("refunded")


def order_from_csv(row: dict[str, str]) -> Order:
    """Build an Order from a CSV row dict.

    CSV columns: order_id, sku, qty, price, shipping_address
    """
    try:
        order_id = row["order_id"]
        sku = row["sku"]
        qty = int(row["qty"])
        price = float(row["price"])
        try:
            shipping_address = row["shipping_address"]
        except KeyError:
            shipping_address = row["shpping_address"]
    except KeyError as exc:
        raise KeyError(f"Missing required CSV column: {exc}") from exc
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid data format in CSV row: {exc}") from exc

    items: tuple[ItemTuple, ...] = ((sku, qty, price),)
    return Order(order_id, items, shipping_address)


def clone_order(order: Order) -> Order:
    """Deep-copy an order so mutations don't affect the original."""
    return Order(f"{order.order_id}-COPY", order.items, order.shipping_address)


def find_order(orders: Sequence[Order], order_id: str) -> Order | None:
    for o in orders:
        if o.order_id == order_id:
            return o
    return None


def validate_email(address: str) -> bool:
    """True if the address looks like a valid email address."""
    if not address or "@" not in address:
        return False
    parts = address.split("@")
    if len(parts) != 2:
        return False
    domain = parts[1]
    return "." in domain and not domain.startswith(".") and not domain.endswith(".")