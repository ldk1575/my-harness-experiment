"""experiment-01 실행기 — 작업 3개 × 조건 2개 × 반복 3회를 새 세션으로 돌린다.

조건 A(full): 평소처럼 실행한다. 사용자 전역 계층(~/.claude 의 플러그인 · 스킬 · MCP · 훅 · 설정)이 모두 실린다.
조건 B(minimal): 같은 명령에 아래 세 플래그만 더한다.
  --setting-sources project   사용자 설정(enabledPlugins · hooks · permissions)을 읽지 않는다
  --strict-mcp-config         --mcp-config 로 준 것 외의 MCP 서버를 무시한다(아무것도 주지 않음)
  --disable-slash-commands    스킬을 모두 끈다

사용법:
  python scripts/run_experiment.py --work D:/harness-runs/exp01            # 18회 본 실행
  python scripts/run_experiment.py --work D:/harness-runs/pilot --pilot    # 실행기 점검용 1회 (집계 제외)

실행 폴더는 저장소 밖에 둔다(노드 실행 절차 1번). 작업 폴더에는 fixture 원본만 복사하고
숨긴 테스트(fixture/hidden_tests)는 실행이 끝난 뒤 채점용 복사본에만 넣는다.
"""
import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "fixture"
MODEL = "claude-sonnet-5-5"
TIMEOUT_S = 900

TASKS = {
    "parse-log": {
        "prompt": (
            "sample.log 에서 ERROR 레벨 줄만 골라 마크다운 표로 출력하는 parse.py 를 작성해줘. "
            "조건: 각 줄은 `날짜 시각 레벨 메시지` 형식이고 레벨은 세 번째 칸이다. "
            "parse_errors(lines) 함수는 (\"날짜 시각\", 메시지) 튜플 목록을 돌려준다. "
            "`python parse.py [로그파일]` 로 실행하면(기본값 sample.log) `| 시각 | 메시지 |` 표를 출력한다. "
            "형식에 맞지 않는 줄은 건너뛴다. 끝나면 python -m unittest test_parse 로 확인해줘."
        ),
        "visible_test": "test_parse",
        "hidden_test": "test_hidden_parse",
    },
    "refactor-util": {
        "prompt": (
            "util.py 의 함수 3개(slugify, chunk, safe_div)에 타입 힌트와 독스트링을 추가해줘. "
            "동작은 바꾸지 마. 끝나면 python -m unittest test_util 로 확인해줘."
        ),
        "visible_test": "test_util",
        "hidden_test": "test_hidden_util",
    },
    "fix-failing": {
        "prompt": (
            "python -m unittest test_me 를 실행하면 실패가 2건 나와. "
            "test_me.py 는 고치지 말고 코드를 고쳐서 통과하게 해줘."
        ),
        "visible_test": "test_me",
        "hidden_test": "test_hidden_me",
    },
}

COMMON = [
    "--model", MODEL,
    "--output-format", "stream-json", "--verbose",
    "--no-session-persistence",
    "--permission-mode", "acceptEdits",
    "--max-budget-usd", "3",
    "--allowedTools", "Bash(python:*)", "PowerShell(python:*)",
]
MINIMAL = ["--setting-sources", "project", "--strict-mcp-config", "--disable-slash-commands"]


def schedule():
    """반복마다, 작업마다 A·B 순서를 번갈아 둔다(순서 효과 통제)."""
    runs = []
    for rep in (1, 2, 3):
        for ti, task in enumerate(TASKS):
            order = ("A", "B") if (rep + ti) % 2 == 0 else ("B", "A")
            for cond in order:
                runs.append((task, cond, rep))
    return runs


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_unittest(cwd, module):
    p = subprocess.run(
        [sys.executable, "-m", "unittest", module],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    return p.returncode == 0, (p.stdout + p.stderr)[-2000:]


def one_run(work_root, idx, task, cond, rep):
    spec = TASKS[task]
    run_id = f"{idx:02d}_{task}_{cond}_r{rep}"
    work = work_root / "work" / run_id
    raw = work_root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(FIXTURE / task, work)
    test_file = work / f"{spec['visible_test']}.py"
    test_hash = sha(test_file)

    claude = shutil.which("claude")
    cmd = [claude, "-p", spec["prompt"], *COMMON] + (MINIMAL if cond == "B" else [])
    started = dt.datetime.now().astimezone()
    with open(raw / f"{run_id}.jsonl", "w", encoding="utf-8") as out, open(raw / f"{run_id}.err", "w", encoding="utf-8") as err:
        try:
            p = subprocess.run(cmd, cwd=work, stdout=out, stderr=err, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
            exit_code = p.returncode
        except subprocess.TimeoutExpired:
            exit_code = "timeout"
    ended = dt.datetime.now().astimezone()

    # 채점: 공개 테스트는 작업 폴더 그대로, 숨긴 테스트는 복사본에 넣어서 실행한다.
    visible_ok, visible_log = run_unittest(work, spec["visible_test"])
    grade = work_root / "grade" / run_id
    if grade.exists():
        shutil.rmtree(grade)
    shutil.copytree(work, grade, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(FIXTURE / "hidden_tests" / f"{spec['hidden_test']}.py", grade)
    hidden_ok, hidden_log = run_unittest(grade, spec["hidden_test"])

    result = {
        "run_id": run_id, "index": idx, "task": task, "condition": cond, "rep": rep,
        "started": started.isoformat(timespec="seconds"), "ended": ended.isoformat(timespec="seconds"),
        "wall_s": round((ended - started).total_seconds(), 1), "exit_code": exit_code,
        "visible_ok": visible_ok, "hidden_ok": hidden_ok,
        "test_file_unchanged": sha(test_file) == test_hash,
        "visible_log": visible_log, "hidden_log": hidden_log,
        "files_after": sorted(p.name for p in work.iterdir() if p.is_file()),
    }
    (work_root / "results").mkdir(exist_ok=True)
    (work_root / "results" / f"{run_id}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{ended:%H:%M:%S}] {run_id}: exit={exit_code} visible={visible_ok} hidden={hidden_ok} "
          f"test_unchanged={result['test_file_unchanged']} wall={result['wall_s']}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--pilot", action="store_true", help="fix-failing 을 B 조건으로 1회만 돌려 실행기를 점검한다")
    ap.add_argument("--start", type=int, default=1, help="중단됐을 때 이 번호부터 다시 시작")
    args = ap.parse_args()
    runs = [("fix-failing", "B", 0)] if args.pilot else schedule()
    for idx, (task, cond, rep) in enumerate(runs, 1):
        if idx < args.start:
            continue
        one_run(args.work, idx, task, cond, rep)


if __name__ == "__main__":
    main()
