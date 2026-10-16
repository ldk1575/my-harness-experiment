class Cart:
    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self.items:
            self.items[name]["qty"] += qty
        else:
            self.items[name] = {"price": price, "qty": qty}

    def remove(self, name):
        self.items.pop(name, None)

    def total(self):
        return sum(item["price"] for item in self.items.values())

    def apply_coupon(self, percent):
        """쿠폰 할인율(percent)을 적용한 최종 금액을 돌려준다."""
        return self.total() * percent / 100
