import sys


def parse_errors(lines):
    """`날짜 시각 레벨 메시지` 형식 줄 중 ERROR 만 ("날짜 시각", 메시지) 로 돌려준다."""
    result = []
    for line in lines:
        parts = line.strip().split(None, 3)
        if len(parts) < 4:
            continue
        date, time, level, message = parts
        if level == "ERROR":
            result.append((f"{date} {time}", message))
    return result


def main(argv):
    path = argv[1] if len(argv) > 1 else "sample.log"
    with open(path, encoding="utf-8") as f:
        errors = parse_errors(f.read().splitlines())
    print("| 시각 | 메시지 |")
    print("| --- | --- |")
    for ts, msg in errors:
        print(f"| {ts} | {msg.replace('|', chr(92) + '|')} |")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv)
