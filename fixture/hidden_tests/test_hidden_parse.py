"""parse-log 숨긴 테스트. 실행 중에는 모델에게 보이지 않고, 끝난 뒤 채점에만 쓴다.
요청 문장에 적힌 조건(레벨은 세 번째 칸, 형식이 틀린 줄은 건너뜀)만 확인한다."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent


class HiddenParseTest(unittest.TestCase):
    def test_error_word_in_message_is_not_error_level(self):
        from parse import parse_errors

        lines = ["2026-10-16 09:05:00 INFO user searched for ERROR codes"]
        self.assertEqual(parse_errors(lines), [])

    def test_malformed_and_blank_lines_are_skipped(self):
        from parse import parse_errors

        lines = ["", "garbage", "2026-10-16 09:00:00", "2026-10-16 10:00:00 ERROR real one"]
        self.assertEqual(parse_errors(lines), [("2026-10-16 10:00:00", "real one")])

    def test_empty_input(self):
        from parse import parse_errors

        self.assertEqual(parse_errors([]), [])

    def test_cli_accepts_log_path(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "other.log"
            log.write_text(
                "2026-10-17 08:00:00 ERROR only this line\n2026-10-17 08:00:01 INFO not this\n",
                encoding="utf-8",
            )
            out = subprocess.run(
                [sys.executable, "parse.py", str(log)], cwd=HERE, capture_output=True, text=True, check=True,
                encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            ).stdout
        self.assertIn("only this line", out)
        self.assertNotIn("not this", out)
        self.assertNotIn("payment gateway timeout", out)


if __name__ == "__main__":
    unittest.main()
