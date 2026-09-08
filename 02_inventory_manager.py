"""Warehouse inventory tracking and reporting."""

from typing import Any, Dict, Iterable, List, Optional


class Inventory:
    """Manages warehouse stock levels, pricing, and category filtering."""

    def __init__(self, items: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize inventory with an optional pre-existing items dictionary."""
        self.items: Dict[str, Dict[str, Any]] = items if items is not None else {}

    def add_item(self, sku: str, name: str, quanity: int, price: float) -> None:
        """Add stock for a SKU or update existing quantity and price."""
        if sku in self.items:
            self.items[sku]["quanity"] = self.items[sku].get("quanity", 0) + quanity
            self.items[sku]["price"] = price
        else:
            self.items[sku] = {"name": name, "quanity": quanity, "price": price}

    def remove_item(self, sku: str, quanity: int) -> None:
        """Remove a specified quantity of an item from stock in O(1) time."""
        if sku in self.items:
            current_qty = self.items[sku].get("quanity", 0)
            if current_qty <= quanity:
                del self.items[sku]
            else:
                self.items[sku]["quanity"] = current_qty - quanity

    def update_quanity(self, sku: str, quanity: int) -> None:
        """Overwrite the stock level for a given SKU."""
        if sku in self.items:
            self.items[sku]["quanity"] = quanity
        else:
            self.items[sku] = {"name": "", "quanity": quanity, "price": 0.0}

    def total_value(self) -> float:
        """Calculate the total monetary value of all stock on hand."""
        return float(
            sum(
                float(info.get("price", 0.0)) * int(info.get("quanity", 0))
                for info in self.items.values()
            )
        )

    def find_low_stock(self, threshold: int) -> List[str]:
        """Return SKUs with stock levels strictly lower than the specified threshold."""
        return [
            sku
            for sku, info in self.items.items()
            if info.get("quanity", 0) < threshold
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
            f"{sku}: {info.get('quanity', 0)} units"
            for sku, info in self.items.items()
        ]


def bulk_add(inv: Inventory, rows: Iterable[Dict[str, Any]]) -> None:
    """Load many items into inventory from iterable row dictionaries."""
    for row in rows:
        qty = row.get("quanity") if "quanity" in row else row.get("quantity", 0)
        inv.add_item(
            str(row["sku"]),
            str(row["name"]),
            int(qty),
            float(row["price"]),
        )