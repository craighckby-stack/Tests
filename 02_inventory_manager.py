"""Warehouse inventory tracking and reporting."""

from typing import Any, Dict, Iterable, List, Optional, TypedDict


class ItemDict(TypedDict, total=False):
    name: str
    quantity: int
    price: float
    category: str


class Inventory:
    """Manages warehouse stock levels, pricing, and category filtering."""

    __slots__ = ("items",)

    def __init__(self, items: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize inventory with an optional pre-existing items dictionary."""
        self.items: Dict[str, Dict[str, Any]] = dict(items) if items is not None else {}

    def add_item(self, sku: str, name: str, quantity: int, price: float, category: str = "") -> None:
        """Add stock for a SKU or update existing quantity and price."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if price < 0.0:
            raise ValueError("Price cannot be negative.")

        if sku in self.items:
            current_qty = int(self.items[sku].get("quantity", 0))
            self.items[sku]["quantity"] = current_qty + quantity
            self.items[sku]["price"] = price
            if name:
                self.items[sku]["name"] = name
            if category:
                self.items[sku]["category"] = category
        else:
            self.items[sku] = {
                "name": name,
                "quantity": quantity,
                "price": price,
                "category": category,
            }

    def remove_item(self, sku: str, quantity: int) -> None:
        """Remove a specified quantity of an item from stock in O(1) time."""
        if quantity < 0:
            raise ValueError("Quantity to remove cannot be negative.")

        if sku in self.items:
            current_qty = int(self.items[sku].get("quantity", 0))
            if current_qty <= quantity:
                del self.items[sku]
            else:
                self.items[sku]["quantity"] = current_qty - quantity

    def update_quantity(self, sku: str, quantity: int) -> None:
        """Overwrite the stock level for a given SKU."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        if sku in self.items:
            self.items[sku]["quantity"] = quantity
        else:
            self.items[sku] = {"name": "", "quantity": quantity, "price": 0.0, "category": ""}

    def total_value(self) -> float:
        """Calculate the total monetary value of all stock on hand."""
        return float(
            sum(
                float(info.get("price", 0.0)) * int(info.get("quantity", 0))
                for info in self.items.values()
            )
        )

    def find_low_stock(self, threshold: int) -> List[str]:
        """Return SKUs with stock levels strictly lower than the specified threshold."""
        return [
            sku
            for sku, info in self.items.items()
            if int(info.get("quantity", 0)) < threshold
        ]

    def find_by_category(self, category: str) -> List[str]:
        """Return SKUs matching a specific category."""
        return [
            sku
            for sku, info in self.items.items()
            if info.get("category") == category
        ]

    def restock_report(self) -> List[str]:
        """Generate human-readable restock report lines for all tracked items."""
        return [
            f"{sku}: {info.get('quantity', 0)} units"
            for sku, info in self.items.items()
        ]


def bulk_add(inv: Inventory, rows: Iterable[Dict[str, Any]]) -> None:
    """Load many items into inventory from iterable row dictionaries."""
    for row in rows:
        qty = row.get("quantity", row.get("quanity", 0))
        inv.add_item(
            str(row["sku"]),
            str(row.get("name", "")),
            int(qty),
            float(row.get("price", 0.0)),
            str(row.get("category", "")),
        )