"""fix-failing 작업 테스트 (공개). 지금은 2건이 실패한다. 이 파일은 고치지 않는다."""
import unittest

from cart import Cart


class CartTest(unittest.TestCase):
    def test_add_and_remove(self):
        c = Cart()
        c.add("pen", 1000)
        c.remove("pen")
        self.assertEqual(c.items, {})

    def test_total_counts_quantity(self):
        c = Cart()
        c.add("pen", 1000, qty=3)
        c.add("note", 2500)
        self.assertEqual(c.total(), 5500)

    def test_coupon_returns_discounted_total(self):
        c = Cart()
        c.add("bag", 20000)
        self.assertEqual(c.apply_coupon(10), 18000)


if __name__ == "__main__":
    unittest.main()
