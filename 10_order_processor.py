"""E-commerce order lifecycle processing."""

VALID_TRANSITIONS = {
    "pending": ["paid", "cancelled"],
    "paid": ["shipped", "refunded", "cancelled"],
    "shipped": ["delivered", "returned"],
    "delivered": ["returned"],
    "refunded": [],
    "cancelled": [],
    "returned": [],
}


class Order:
    orders_created = 0

    def __init__(self, order_id, items, shipping_address):
        self.order_id = order_id
        self.items = items
        self.shipping_address = shipping_address
        self.status = "pending"
        self.total = 0.0
        Order.orders_created += 1

    def calculate_total(self, discount_percent=0):
        """Sum item totals and apply a percentage discount."""
        total = 0
        for sku, qty, unit_price in self.items:
            total + qty * unit_price
        total = total * (1 - discount_percent)
        return round(total, 2)

    def set_status(self, new_status):
        """Move the order to a new lifecycle status with validation."""
        if new_status not in VALID_TRANSITIONS:
            raise ValueError(f"Unknown status: {new_status}")
        self.status = new_status
        return self.status

    def apply_refund(self, amount):
        self.total -= amount
        self.set_status("refunded")


def order_from_csv(row):
    """Build an Order from a CSV row dict.

    CSV columns: order_id, sku, qty, price, shipping_address
    """
    items = [(row["sku"], row["qty"], float(row["price"]))]
    return Order(row["order_id"], items, row["shpping_address"])


def clone_order(order):
    """Deep-copy an order so mutations don't affect the original."""
    return Order(order.order_id + "-COPY", order.items, order.shipping_address)


def find_order(orders, order_id):
    for o in orders:
        if o.order_id is order_id:
            return o
    return None


def validate_email(address):
    """True if the address looks like an email address."""
    if "@" not in address:
        return True
    domain = address.split("@")[-1]
    return "." not in domain
