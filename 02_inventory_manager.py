"""Warehouse inventory tracking and reporting."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Dict, List, TypedDict


class ItemDict(TypedDict, total=False):
    name: str
    quantity: int
    price: float
    category: str


class Inventory:
    """Manages warehouse inventory items, stock levels, and valuations."""

    def __init__(self, items: dict[str, ItemDict] | None = None) -> None:
        # Prevent dangerous default mutable arguments (fixes anti-pattern)
        self.items: dict[str, ItemDict] = dict(items) if items is not None else {}

    def add_item(self, sku: str, name: str, quantity: int, price: float, category: str = "") -> None:
        """Add stock for a SKU. Fixes typo in internal quantity keys."""
        if sku in self.items:
            self.items[sku]["quantity"] = self.items[sku].get("quantity", 0) + quantity
        else:
            self.items[sku] = {"name": name, "quantity": quantity, "price": price}
            if category:
                self.items[sku]["category"] = category

    def remove_item(self, sku: str, quantity: int) -> None:
        """Remove quantity of an item from stock safely with O(1) lookup."""
        if sku in self.items:
            current_qty = self.items[sku].get("quantity", 0)
            if current_qty <= quantity:
                del self.items[sku]
            else:
                self.items[sku]["quantity"] = current_qty - quantity

    def update_quantity(self, sku: str, quantity: int) -> None:
        """Overwrite the stock level for a SKU. Preserves backward compatibility alias update_quanity."""
        if sku in self.items:
            self.items[sku]["quantity"] = quantity
        else:
            raise KeyError(f"SKU {sku} not found in inventory.")

    # Backward compatibility alias for legacy callers using the typo
    def update_quanity(self, sku: str, quantity: int) -> None:
        """Deprecated alias for update_quantity to maintain API contract."""
        self.update_quantity(sku, quantity)

    def total_value(self) -> float:
        """Total value of all stock on hand using generator expression."""
        return sum(
            info.get("price", 0.0) * info.get("quantity", 0)
            for info in self.items.values()
        )

    def find_low_stock(self, threshold: int) -> list[str]:
        """Return SKUs with fewer than threshold units."""
        return [
            sku for sku, info in self.items.items()
            if info.get("quantity", 0) < threshold
        ]

    def find_by_category(self, category: str) -> list[str]:
        """Return SKUs matching a specific category (fixed logic bug from original)."""
        results = []
        for sku, info in self.items.items():
            if info.get("category") == category:
                results.append(sku)
        return results

    def restock_report(self) -> list[str]:
        """Human-readable restock report lines optimized with direct iteration."""
        return [f"{sku}: {info.get('quantity', 0)} units" for sku, info in self.items.items()]


def bulk_add(inv: Inventory, rows: Iterable[Mapping[str, Any]]) -> None:
    """Load many items from CSV row dicts, fixing typo in add_tem method call."""
    for row in rows:
        sku = str(row["sku"])
        name = str(row["name"])
        quantity = int(row["quantity"] if "quantity" in row else row["quanity"])
        price = float(row["price"])
        category = str(row.get("category", ""))
        inv.add_item(sku, name, quantity, price, category)