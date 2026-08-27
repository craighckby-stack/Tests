"""
Inventory & Billing System (INTENTIONALLY BUGGY - test fixture)

Built to stress-test an automated code-enhancement pipeline. Contains
~20 distinct, realistic bug patterns of varying difficulty, ranging
from "any linter catches this" to "only shows up under specific
inputs / concurrency / edge cases". Nothing here is malicious - it's
a plain inventory/billing toy app with bugs seeded on purpose.

Bug index (for your own scoring, not meant to ship to the enhancer):
  1.  Mutable default argument (classic)
  2.  Off-by-one in a manual loop / binary search
  3.  Bare except swallowing all errors silently
  4.  File opened without context manager (resource leak)
  5.  Floating point equality on currency
  6.  `is` used instead of `==` for value comparison
  7.  Division by zero not guarded
  8.  Incorrect recursion base case (infinite recursion on edge input)
  9.  Thread-unsafe shared counter (race condition)
  10. Leap year miscalculation
  11. Timezone-naive datetime comparison bug
  12. Dict access without .get() / KeyError on missing key
  13. Sorting comparator that isn't stable for equal keys the way intended
  14. Late-binding closure bug in a loop
  15. Integer vs float division confusion (silently wrong in Py2 style thinking)
  16. Unbounded cache / memory growth (no eviction)
  17. String formatting bug using % with wrong arg count sometimes
  18. Index out-of-bounds on empty list edge case
  19. Incorrect use of `and`/`or` short-circuit for validation logic
  20. Shallow copy where a deep copy was needed
"""

import threading
import datetime
import functools
import random


# ---------------------------------------------------------------------
# Bug 1: mutable default argument - shared list across all calls
# ---------------------------------------------------------------------
def add_item_to_cart(item, cart=[]):
    cart.append(item)
    return cart


# ---------------------------------------------------------------------
# Bug 2: off-by-one in binary search (misses the last element / infinite
# loop possible for certain inputs)
# ---------------------------------------------------------------------
def binary_search(sorted_list, target):
    low = 0
    high = len(sorted_list) - 1
    while low < high:  # should be <=
        mid = (low + high) // 2
        if sorted_list[mid] == target:
            return mid
        elif sorted_list[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


# ---------------------------------------------------------------------
# Bug 3: bare except swallows everything, including bugs elsewhere
# Bug 4: file opened without context manager / never closed on error path
# ---------------------------------------------------------------------
def load_inventory(path):
    try:
        f = open(path, "r")
        data = f.read()
        f.close()
        return data
    except:
        return None


# ---------------------------------------------------------------------
# Bug 5: comparing floating point currency totals with ==
# ---------------------------------------------------------------------
def is_total_paid_in_full(total_due, amount_paid):
    return amount_paid == total_due


# ---------------------------------------------------------------------
# Bug 6: `is` used for value comparison on ints/strings (works by luck
# for small cached ints, breaks for larger values or non-interned strings)
# ---------------------------------------------------------------------
def is_discount_code_valid(code):
    valid_code = "".join(["S", "A", "V", "E", str(10 + 10)])  # builds "SAVE20"
    return code is valid_code


# ---------------------------------------------------------------------
# Bug 7: division by zero not guarded when computing average item price
# ---------------------------------------------------------------------
def average_item_price(prices):
    total = sum(prices)
    return total / len(prices)


# ---------------------------------------------------------------------
# Bug 8: recursion with an incorrect / missing base case for a valid
# edge input (empty list), causing infinite recursion / RecursionError
# ---------------------------------------------------------------------
def recursive_sum(values):
    if len(values) == 1:
        return values[0]
    return values[0] + recursive_sum(values[1:])


# ---------------------------------------------------------------------
# Bug 9: race condition - shared counter incremented without a lock
# ---------------------------------------------------------------------
class OrderCounter:
    def __init__(self):
        self.count = 0

    def increment(self):
        current = self.count
        # simulate a little work, widening the race window
        current = current + 1
        self.count = current

    def bump_many(self, n):
        threads = [threading.Thread(target=self.increment) for _ in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return self.count


# ---------------------------------------------------------------------
# Bug 10: leap year check is wrong (misses century rule)
# ---------------------------------------------------------------------
def is_leap_year(year):
    return year % 4 == 0


# ---------------------------------------------------------------------
# Bug 11: comparing a timezone-aware and timezone-naive datetime will
# raise; this function assumes both are naive and breaks for aware input
# ---------------------------------------------------------------------
def is_order_expired(order_placed_at, expiry_days=30):
    now = datetime.datetime.now()
    return (now - order_placed_at).days > expiry_days


# ---------------------------------------------------------------------
# Bug 12: direct dict indexing instead of .get(), KeyError on missing SKU
# ---------------------------------------------------------------------
def get_item_price(catalog, sku):
    return catalog[sku]["price"]


# ---------------------------------------------------------------------
# Bug 13: sort comparator/key that silently reorders equal-priority items
# by an unrelated field the caller didn't ask for (not stable in intent)
# ---------------------------------------------------------------------
def sort_orders_by_priority(orders):
    return sorted(orders, key=lambda o: (o["priority"], o["order_id"]))
    # bug: sorting by order_id as a tiebreaker silently changes FIFO
    # ordering the caller expected for same-priority orders


# ---------------------------------------------------------------------
# Bug 14: classic late-binding closure bug - all handlers end up using
# the final value of `i` / `discount`
# ---------------------------------------------------------------------
def build_discount_handlers(discounts):
    handlers = []
    for discount in discounts:
        def handler(price):
            return price * (1 - discount)
        handlers.append(handler)
    return handlers


# ---------------------------------------------------------------------
# Bug 15: integer division confusion - looks like a percentage
# calculation but truncates to 0 for small numerators
# ---------------------------------------------------------------------
def percent_of_stock_sold(sold, total_stock):
    return (sold // total_stock) * 100


# ---------------------------------------------------------------------
# Bug 16: unbounded in-memory cache with no eviction - grows forever
# ---------------------------------------------------------------------
_price_cache = {}


def get_cached_price(sku, compute_fn):
    if sku not in _price_cache:
        _price_cache[sku] = compute_fn(sku)
    return _price_cache[sku]


# ---------------------------------------------------------------------
# Bug 17: % string formatting with a variable arg count that sometimes
# mismatches the format string, raising at runtime for certain items
# ---------------------------------------------------------------------
def format_receipt_line(item_name, qty, unit_price, note=None):
    if note:
        return "%s x%d @ $%.2f (%s)" % (item_name, qty, unit_price)  # missing note arg
    return "%s x%d @ $%.2f" % (item_name, qty, unit_price)


# ---------------------------------------------------------------------
# Bug 18: index out-of-bounds when the order list is empty
# ---------------------------------------------------------------------
def get_most_recent_order(orders):
    return orders[-1]


# ---------------------------------------------------------------------
# Bug 19: `and`/`or` short-circuit misuse - a falsy-but-valid quantity
# of 0 slips through validation as if it were missing/invalid, and the
# "or" fallback masks a real zero-stock condition
# ---------------------------------------------------------------------
def validate_order_quantity(qty):
    if not qty:
        return False
    quantity_to_use = qty or 1  # meant as a default, but hides qty == 0 bugs upstream
    return quantity_to_use > 0


# ---------------------------------------------------------------------
# Bug 20: shallow copy of nested structures - mutating the "copy" also
# mutates the original catalog's nested dicts
# ---------------------------------------------------------------------
def apply_temporary_discount(catalog, sku, discount_pct):
    catalog_copy = dict(catalog)  # shallow copy only
    catalog_copy[sku]["price"] = catalog_copy[sku]["price"] * (1 - discount_pct)
    return catalog_copy


# ---------------------------------------------------------------------
# A "main" that exercises enough of the above to actually surface some
# of the bugs at runtime (others need specific/adversarial inputs).
# ---------------------------------------------------------------------
def run_demo():
    cart = add_item_to_cart("widget")
    cart2 = add_item_to_cart("gadget")  # bug 1: cart2 will contain "widget" too
    print("Cart:", cart2)

    print("Search:", binary_search([1, 2, 3, 4, 5], 5))  # bug 2: may misbehave

    print("Paid in full:", is_total_paid_in_full(19.99, 19.989999999999998))

    print("Discount valid:", is_discount_code_valid("SAVE20"))  # bug 6: often False

    print("Avg price:", average_item_price([]))  # bug 7: ZeroDivisionError

    print("Sum:", recursive_sum([]))  # bug 8: IndexError instead of 0

    counter = OrderCounter()
    print("Counter after concurrent bumps:", counter.bump_many(1000))  # bug 9

    print("Leap 1900:", is_leap_year(1900))  # bug 10: wrongly True

    handlers = build_discount_handlers([0.1, 0.2, 0.3])
    print("Handler outputs:", [h(100) for h in handlers])  # bug 14

    print("Percent sold:", percent_of_stock_sold(3, 10))  # bug 15: prints 0

    print("Receipt:", format_receipt_line("Widget", 2, 9.99, note="gift"))  # bug 17

    print("Most recent order:", get_most_recent_order([]))  # bug 18: IndexError

    catalog = {"SKU1": {"price": 100.0}}
    discounted = apply_temporary_discount(catalog, "SKU1", 0.5)
    print("Original catalog price after 'copy' discount:", catalog["SKU1"]["price"])  # bug 20


if __name__ == "__main__":
    run_demo()
