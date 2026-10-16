"""parse-log 작업 확인용 테스트 (공개). 작업 전에는 parse.py 가 없어 실패한다."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent


class ParseLogTest(unittest.TestCase):
    def test_parse_errors_returns_error_lines(self):
        from parse import parse_errors

        lines = (HERE / "sample.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            parse_errors(lines),
            [
                ("2026-10-16 09:02:30", "payment gateway timeout"),
                ("2026-10-16 09:03:44", "order 1042 failed validation: missing address"),
                ("2026-10-16 09:07:02", "disk usage above 95%"),
            ],
        )

    def test_cli_prints_markdown_table(self):
        out = subprocess.run(
            [sys.executable, "parse.py"], cwd=HERE, capture_output=True, text=True, check=True,
                encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        ).stdout
        self.assertIn("| 시각 | 메시지 |", out)
        self.assertIn("payment gateway timeout", out)
        self.assertNotIn("server started", out)
        self.assertNotIn("slow query", out)


if __name__ == "__main__":
    unittest.main()
