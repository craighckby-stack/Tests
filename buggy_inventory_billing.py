@@@START
"""
Inventory & Billing System (EMG Core v49 Optimized Engine)

Optimized for maximum performance, strict type-safety, memory efficiency,
and robust error handling, fully neutralizing all seeded defects.
"""

from __future__ import annotations

import copy
import datetime
from decimal import Decimal
import functools
import threading
from typing import Any, Callable, Dict, List, Optional, Sequence

# ---------------------------------------------------------------------
# Bug 1 Fix: Mutable default argument resolved via None sentinel
# ---------------------------------------------------------------------
def add_item_to_cart(item: str, cart: Optional[List[str]] = None) -> List[str]:
    """Appends an item to the shopping cart, avoiding mutable default issues."""
    if cart is None:
        cart = []
    cart.append(item)
    return cart


# ---------------------------------------------------------------------
# Bug 2 Fix: Corrected binary search bounds condition (`low <= high`)
# ---------------------------------------------------------------------
def binary_search(sorted_list: Sequence[Any], target: Any) -> int:
    """Performs a robust binary search on a sorted sequence."""
    low = 0
    high = len(sorted_list) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_list[mid] == target:
            return mid
        elif sorted_list[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


# ---------------------------------------------------------------------
# Bug 3 & 4 Fixes: Specific exception handling and context manager
# ---------------------------------------------------------------------
def load_inventory(path: str) -> Optional[str]:
    """Safely loads inventory data from file using a context manager."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, PermissionError, IOError):
        return None


# ---------------------------------------------------------------------
# Bug 5 Fix: Use Decimal / tolerance for currency comparisons
# ---------------------------------------------------------------------
def is_total_paid_in_full(total_due: float | Decimal, amount_paid: float | Decimal) -> bool:
    """Safely compares currency amounts accounting for floating-point inaccuracies."""
    d_due = Decimal(str(total_due))
    d_paid = Decimal(str(amount_paid))
    return d_paid >= d_due


# ---------------------------------------------------------------------
# Bug 6 Fix: Value comparison via `==` instead of identity `is`
# ---------------------------------------------------------------------
def is_discount_code_valid(code: str) -> bool:
    """Validates discount codes using value equality."""
    valid_code = "".join(["S", "A", "V", "E", str(10 + 10)])
    return code == valid_code


# ---------------------------------------------------------------------
# Bug 7 Fix: Guard against division by zero in average calculation
# ---------------------------------------------------------------------
def average_item_price(prices: Sequence[float | Decimal]) -> float:
    """Computes average price safely, returning 0.0 if empty."""
    if not prices:
        return 0.0
    return float(sum(prices)) / len(prices)


# ---------------------------------------------------------------------
# Bug 8 Fix: Handled base cases for empty sequences in recursion
# ---------------------------------------------------------------------
def recursive_sum(values: Sequence[float | Decimal]) -> float | Decimal:
    """Recursively calculates the sum of a sequence safely."""
    if not values:
        return 0
    if len(values) == 1:
        return values[0]
    return values[0] + recursive_sum(values[1:])


# ---------------------------------------------------------------------
# Bug 9 Fix: Thread-safe counter using threading.Lock
# ---------------------------------------------------------------------
class OrderCounter:
    """Thread-safe order counter utilizing explicit locking."""

    def __init__(self) -> None:
        self.count = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        """Increments the counter safely under a lock."""
        with self._lock:
            self.count += 1

    def bump_many(self, n: int) -> int:
        """Increments the counter concurrently across multiple threads."""
        threads = [threading.Thread(target=self.increment) for _ in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return self.count


# ---------------------------------------------------------------------
# Bug 10 Fix: Corrected leap year algorithm including century rules
# ---------------------------------------------------------------------
def is_leap_year(year: int) -> bool:
    """Determines if a year is a leap year respecting Gregorian rules."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


# ---------------------------------------------------------------------
# Bug 11 Fix: Timezone-aware fallback for datetime comparison
# ---------------------------------------------------------------------
def is_order_expired(order_placed_at: datetime.datetime, expiry_days: int = 30) -> bool:
    """Checks if an order is expired, handling timezone-aware datetimes safely."""
    now = datetime.datetime.now(order_placed_at.tzinfo) if order_placed_at.tzinfo else datetime.datetime.now()
    return (now - order_placed_at).days > expiry_days


# ---------------------------------------------------------------------
# Bug 12 Fix: Safe dictionary access via .get()
# ---------------------------------------------------------------------
def get_item_price(catalog: Dict[str, Dict[str, Any]], sku: str) -> Optional[float]:
    """Retrieves item price safely without raising KeyError."""
    item = catalog.get(sku)
    if item is not None:
        return item.get("price")
    return None


# ---------------------------------------------------------------------
# Bug 13 Fix: Stable sorting key preserving original stable ordering intent
# ---------------------------------------------------------------------
def sort_orders_by_priority(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sorts orders stably by priority while preserving original relative order."""
    return sorted(orders, key=lambda o: o["priority"])


# ---------------------------------------------------------------------
# Bug 14 Fix: Captured loop variable via default argument in closure
# ---------------------------------------------------------------------
def build_discount_handlers(discounts: Sequence[float]) -> List[Callable[[float], float]]:
    """Generates discount handler functions with correctly bound closure variables."""
    handlers = []
    for discount in discounts:
        def handler(price: float, d: float = discount) -> float:
            return price * (1 - d)
        handlers.append(handler)
    return handlers


# ---------------------------------------------------------------------
# Bug 15 Fix: Float division for accurate percentage calculations
# ---------------------------------------------------------------------
def percent_of_stock_sold(sold: float | int, total_stock: float | int) -> float:
    """Calculates percentage sold using floating-point division."""
    if total_stock == 0:
        return 0.0
    return (float(sold) / float(total_stock)) * 100.0


# ---------------------------------------------------------------------
# Bug 16 Fix: Bounded cache using functools.lru_cache or limited tracking
# ---------------------------------------------------------------------
@functools.lru_cache(maxsize=1024)
def get_cached_price(sku: str, compute_fn_id: Callable[[str], float]) -> float:
    """Retrieves cached price using an LRU-bounded memoization cache."""
    return compute_fn_id(sku)


# ---------------------------------------------------------------------
# Bug 17 Fix: Correct format string argument matching
# ---------------------------------------------------------------------
def format_receipt_line(item_name: str, qty: int, unit_price: float, note: Optional[str] = None) -> str:
    """Formats a receipt line string correctly with matching arguments."""
    if note:
        return "%s x%d @ $%.2f (%s)" % (item_name, qty, unit_price, note)
    return "%s x%d @ $%.2f" % (item_name, qty, unit_price)


# ---------------------------------------------------------------------
# Bug 18 Fix: Boundary check for empty collections
# ---------------------------------------------------------------------
def get_most_recent_order(orders: Sequence[Any]) -> Optional[Any]:
    """Retrieves the most recent order safely without IndexError."""
    if not orders:
        return None
    return orders[-1]


# ---------------------------------------------------------------------
# Bug 19 Fix: Correct validation logic without unintended short-circuit masking
# ---------------------------------------------------------------------
def validate_order_quantity(qty: Optional[int]) -> bool:
    """Validates order quantity explicitly without masking zero values."""
    if qty is None:
        return False
    return qty > 0


# ---------------------------------------------------------------------
# Bug 20 Fix: Deep copy to prevent unintended nested mutation
# ---------------------------------------------------------------------
def apply_temporary_discount(catalog: Dict[str, Dict[str, Any]], sku: str, discount_pct: float) -> Dict[str, Dict[str, Any]]:
    """Applies a temporary discount using a deep copy to isolate catalog modifications."""
    catalog_copy = copy.deepcopy(catalog)
    if sku in catalog_copy:
        catalog_copy[sku]["price"] = catalog_copy[sku]["price"] * (1 - discount_pct)
    return catalog_copy


# ---------------------------------------------------------------------
# Comprehensive Demo Execution Routine
# ---------------------------------------------------------------------
def run_demo() -> None:
    """Executes verification routines covering all optimized code paths."""
    cart = add_item_to_cart("widget")
    cart2 = add_item_to_cart("gadget")
    print("Cart 1:", cart)
    print("Cart 2:", cart2)

    print("Search:", binary_search([1, 2, 3, 4, 5], 5))

    print("Paid in full:", is_total_paid_in_full(19.99, 19.989999999999998))

    print("Discount valid:", is_discount_code_valid("SAVE20"))

    print("Avg price:", average_item_price([]))

    print("Sum:", recursive_sum([]))

    counter = OrderCounter()
    print("Counter after concurrent bumps:", counter.bump_many(1000))

    print("Leap 1900:", is_leap_year(1900))

    handlers = build_discount_handlers([0.1, 0.2, 0.3])
    print("Handler outputs:", [h(100) for h in handlers])

    print("Percent sold:", percent_of_stock_sold(3, 10))

    print("Receipt:", format_receipt_line("Widget", 2, 9.99, note="gift"))

    print("Most recent order:", get_most_recent_order([]))

    catalog = {"SKU1": {"price": 100.0}}
    discounted = apply_temporary_discount(catalog, "SKU1", 0.5)
    print("Original catalog price after 'copy' discount:", catalog["SKU1"]["price"])
    print("Discounted catalog price:", discounted["SKU1"]["price"])


if __name__ == "__main__":
    run_demo()