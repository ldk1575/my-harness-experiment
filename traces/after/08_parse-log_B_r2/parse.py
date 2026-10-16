"""로그 파일에서 ERROR 레벨 줄만 골라 마크다운 표로 출력한다."""
import re
import sys

LINE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (\S+) (.*)$")


def parse_errors(lines):
    """`날짜 시각 레벨 메시지` 형식 줄 중 ERROR 만 ("날짜 시각", 메시지) 로 돌려준다."""
    errors = []
    for line in lines:
        m = LINE_RE.match(line.strip())
        if m and m.group(3) == "ERROR":
            errors.append((f"{m.group(1)} {m.group(2)}", m.group(4)))
    return errors


def to_markdown(rows):
    out = ["| 시각 | 메시지 |", "| --- | --- |"]
    for ts, msg in rows:
        out.append(f"| {ts} | {msg.replace('|', chr(92) + '|')} |")
    return "\n".join(out)


def main(argv):
    path = argv[1] if len(argv) > 1 else "sample.log"
    with open(path, encoding="utf-8") as f:
        rows = parse_errors(f.read().splitlines())
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(to_markdown(rows))


if __name__ == "__main__":
    main(sys.argv)
