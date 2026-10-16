"""로그에서 ERROR 레벨 줄만 골라 마크다운 표로 출력한다.

사용법: python parse.py [로그파일]   (기본값: sample.log)
"""
import re
import sys

# 날짜 시각 레벨 메시지 — 레벨은 세 번째 칸
LINE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\S+) (.+)$")


def parse_errors(lines):
    """ERROR 줄만 ("날짜 시각", 메시지) 튜플 목록으로 돌려준다. 형식이 다른 줄은 건너뛴다."""
    errors = []
    for line in lines:
        m = LINE_RE.match(line.strip())
        if not m:
            continue
        timestamp, level, message = m.groups()
        if level == "ERROR":
            errors.append((timestamp, message.strip()))
    return errors


def to_markdown(errors):
    rows = ["| 시각 | 메시지 |", "| --- | --- |"]
    for timestamp, message in errors:
        rows.append(f"| {timestamp} | {message.replace('|', chr(92) + '|')} |")
    return "\n".join(rows)


def main(argv):
    path = argv[1] if len(argv) > 1 else "sample.log"
    with open(path, encoding="utf-8") as f:
        errors = parse_errors(f.read().splitlines())
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(to_markdown(errors))


if __name__ == "__main__":
    main(sys.argv)
