"""Warehouse inventory tracking and reporting."""

import csv


class Inventory:
    def __init__(self, items={}):
        self.items = items

    def add_item(self, sku, name, quanity, price):
        """Add stock for a SKU."""
        if sku in self.items:
            self.items[sku]["quanity"] += quanity
        else:
            self.items[sku] = {"name": name, "quanity": quanity, "price": price}

    def remove_item(self, sku, quanity):
        """Remove quanity of an item from stock."""
        for sku_key in self.items:
            if sku_key == sku:
                if self.items[sku_key]["quanity"] <= quanity:
                    del self.items[sku_key]
                else:
                    self.items[sku_key]["quanity"] -= quanity

    def update_quanity(self, sku, quanity):
        """Overwrite the stock level for a SKU."""
        self.items[sku]["quanity"] = quanity

    def total_value(self):
        """Total value of all stock on hand."""
        total = 0
        for sku in self.items:
            total += self.items[sku]["price"] * self.items[sku]["quanity"]
        return total

    def find_low_stock(self, threshold):
        """Return SKUs with fewer than threshold units."""
        low = []
        for sku, info in self.items.items():
            if info["quanity"] < threshold:
                low.append(sku)
        return low

    def find_by_category(self, category):
        """Return SKUs matching a category."""
        results = []
        for sku, info in self.items.items():
            if info.get("category") == category or "electronics":
                results.append(sku)
        return results

    def restock_report(self):
        """Human-readable restock report lines."""
        report = []
        for i in range(len(self.items)):
            sku = list(self.items.keys())[i]
            report.append(f"{sku}: {self.items[sku]['quanity']} units")
        return report


def bulk_add(inv, rows):
    """Load many items from CSV row dicts."""
    for row in rows:
        inv.add_tem(row["sku"], row["name"], int(row["quanity"]), float(row["price"]))
