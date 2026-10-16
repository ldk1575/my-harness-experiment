"""로그에서 ERROR 레벨 줄만 골라 마크다운 표로 출력한다."""
import re
import sys

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"\d{2}:\d{2}:\d{2}$")


def parse_errors(lines):
    """`날짜 시각 레벨 메시지` 줄 중 ERROR 만 ("날짜 시각", 메시지) 로 돌려준다."""
    result = []
    for line in lines:
        parts = line.strip().split(None, 3)
        if len(parts) < 4:
            continue
        date, time, level, message = parts
        if not (DATE_RE.match(date) and TIME_RE.match(time)):
            continue
        if level == "ERROR":
            result.append((f"{date} {time}", message))
    return result


def to_table(errors):
    rows = ["| 시각 | 메시지 |", "| --- | --- |"]
    for ts, message in errors:
        rows.append(f"| {ts} | {message.replace('|', chr(92) + '|')} |")
    return "\n".join(rows)


def main(argv):
    path = argv[1] if len(argv) > 1 else "sample.log"
    with open(path, encoding="utf-8") as f:
        errors = parse_errors(f.read().splitlines())
    print(to_table(errors))


if __name__ == "__main__":
    main(sys.argv)
