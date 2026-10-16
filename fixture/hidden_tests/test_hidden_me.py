"""fix-failing 숨긴 테스트. 고친 코드가 공개 테스트의 숫자만 맞춘 것이 아니라 일반적으로 맞는지 본다."""
import unittest

from cart import Cart


class HiddenCartTest(unittest.TestCase):
    def test_total_with_repeated_add(self):
        c = Cart()
        c.add("pen", 1000)
        c.add("pen", 1000, qty=2)
        c.add("cup", 4500, qty=2)
        self.assertEqual(c.total(), 12000)

    def test_coupon_edges(self):
        c = Cart()
        c.add("pen", 1000, qty=4)
        self.assertEqual(c.apply_coupon(0), 4000)
        self.assertEqual(c.apply_coupon(100), 0)
        self.assertEqual(c.apply_coupon(25), 3000)

    def test_existing_behavior_kept(self):
        c = Cart()
        with self.assertRaises(ValueError):
            c.add("pen", 1000, qty=0)
        c.remove("not-there")
        self.assertEqual(c.total(), 0)


if __name__ == "__main__":
    unittest.main()
