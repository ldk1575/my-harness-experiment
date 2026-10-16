"""refactor-util 작업 확인용 테스트 (공개). 작업 전에는 타입 힌트와 독스트링이 없어 실패한다."""
import inspect
import unittest

import util

FUNCS = [util.slugify, util.chunk, util.safe_div]


class RefactorUtilTest(unittest.TestCase):
    def test_every_parameter_and_return_is_annotated(self):
        for f in FUNCS:
            sig = inspect.signature(f)
            for name, p in sig.parameters.items():
                self.assertIsNot(p.annotation, inspect.Parameter.empty, f"{f.__name__}({name}) 타입 힌트 없음")
            self.assertIsNot(sig.return_annotation, inspect.Signature.empty, f"{f.__name__} 반환 타입 힌트 없음")

    def test_every_function_has_docstring(self):
        for f in FUNCS:
            self.assertTrue((f.__doc__ or "").strip(), f"{f.__name__} 독스트링 없음")


if __name__ == "__main__":
    unittest.main()
