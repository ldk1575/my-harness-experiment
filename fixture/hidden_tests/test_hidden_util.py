"""refactor-util 숨긴 테스트. 요청 문장의 "동작은 바꾸지 마" 조건을 확인한다."""
import unittest

from util import chunk, safe_div, slugify


class HiddenUtilTest(unittest.TestCase):
    def test_slugify_behavior_unchanged(self):
        self.assertEqual(slugify("  Hello, World!  "), "hello-world")
        self.assertEqual(slugify("AI Agent 2기"), "ai-agent-2")
        self.assertEqual(slugify("---"), "")

    def test_chunk_behavior_unchanged(self):
        self.assertEqual(chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])
        self.assertEqual(chunk("abcde", 2), ["ab", "cd", "e"])
        self.assertEqual(chunk([], 3), [])
        with self.assertRaises(ValueError):
            chunk([1], 0)

    def test_safe_div_behavior_unchanged(self):
        self.assertEqual(safe_div(7, 2), 3.5)
        self.assertEqual(safe_div(1, 0), 0)
        self.assertIsNone(safe_div(1, 0, default=None))


if __name__ == "__main__":
    unittest.main()
