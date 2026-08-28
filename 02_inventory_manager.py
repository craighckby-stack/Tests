"""Warehouse inventory tracking and reporting optimized for performance, safety, and correctness."""

__all__ = ["Item", "Inventory", "bulk_add"]

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import logging
from typing import Final, Any

logger: Final[logging.Logger] = logging.getLogger(__name__)


@dataclass(slots=True, frozen=False)
class Item:
    """Represents a single stock item with strict type safety and memory efficiency."""

    name: str
    quantity: int
    price: Decimal
    category: str | None = None


class Inventory:
    """High-performance, memory-efficient warehouse inventory management system."""

    __slots__ = ("_items",)

    def __init__(self, items: Mapping[str, Item | Mapping[str, Any]] | None = None) -> None:
        """Initialize inventory, normalizing incoming dictionary schemas to Item instances."""
        self._items: dict[str, Item] = {}
        if not items:
            return

        for sku, data in items.items():
            if isinstance(data, Item):
                self._items[sku] = data
            elif isinstance(data, Mapping):
                qty_raw = data.get("quantity", data.get("quanity", 0))
                try:
                    quantity = int(qty_raw)  # type: ignore[arg-type]
                except (TypeError, ValueError):
                    quantity = 0

                price_raw = data.get("price", "0.00")
                try:
                    price = Decimal(str(price_raw))
                except (InvalidOperation, TypeError, ValueError):
                    price = Decimal("0.00")

                category_raw = data.get("category")
                self._items[sku] = Item(
                    name=str(data.get("name", "Unknown")),
                    quantity=quantity,
                    price=price,
                    category=str(category_raw) if category_raw is not None else None,
                )

    def add_item(
        self, sku: str, name: str, quantity: int, price: float | Decimal, category: str | None = None
    ) -> None:
        """Add stock or create a new entry for a SKU."""
        try:
            decimal_price = Decimal(str(price))
        except (InvalidOperation, TypeError, ValueError):
            decimal_price = Decimal("0.00")

        if sku in self._items:
            item = self._items[sku]
            item.quantity += quantity
            if name:
                item.name = name
            if decimal_price > 0:
                item.price = decimal_price
            if category is not None:
                item.category = category
        else:
            self._items[sku] = Item(name=name, quantity=quantity, price=decimal_price, category=category)

    def remove_item(self, sku: str, quantity: int) -> None:
        """Safely remove a quantity of an item from stock, deleting it if stock hits zero or below."""
        item = self._items.get(sku)
        if item is not None:
            if item.quantity <= quantity:
                del self._items[sku]
            else:
                item.quantity -= quantity

    def update_quantity(self, sku: str, quantity: int) -> None:
        """Overwrite the stock level for an existing SKU."""
        if sku not in self._items:
            raise KeyError(f"SKU '{sku}' does not exist in inventory.")
        self._items[sku].quantity = quantity

    def total_value(self) -> Decimal:
        """Calculate the total monetary value of all stock on hand using precise decimal arithmetic."""
        return sum((item.price * item.quantity for item in self._items.values()), Decimal("0.00"))

    def find_low_stock(self, threshold: int) -> list[str]:
        """Return a list of SKUs with fewer units than the specified threshold."""
        return [sku for sku, item in self._items.items() if item.quantity < threshold]

    def find_by_category(self, category: str) -> list[str]:
        """Return SKUs matching the requested category."""
        return [sku for sku, item in self._items.items() if item.category == category]

    def restock_report(self) -> list[str]:
        """Generate human-readable restock report lines efficiently."""
        return [f"{sku}: {item.quantity} units" for sku, item in self._items.items()]


def bulk_add(inv: Inventory, rows: Iterable[Mapping[str, Any]]) -> None:
    """Load multiple items from CSV row dictionaries robustly."""
    for row in rows:
        try:
            sku = str(row["sku"])
            name = str(row["name"])
            qty_raw = row.get("quantity", row.get("quanity", 0))
            quantity = int(qty_raw)  # type: ignore[arg-type]
            price = Decimal(str(row["price"]))
            category_raw = row.get("category")
            category = str(category_raw) if category_raw is not None else None
            
            inv.add_item(sku, name, quantity, price, category=category)
        except (KeyError, ValueError, TypeError, InvalidOperation) as e:
            logger.error("Failed to process row %s due to error: %s", row, e)