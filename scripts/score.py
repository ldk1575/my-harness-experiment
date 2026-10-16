"""experiment-01 채점 · 집계 — 실행 폴더의 원본 로그를 읽어 traces/ 와 결과 표를 만든다.

  python scripts/score.py --work D:/harness-runs/exp01

만드는 것
  traces/runs/<run_id>.jsonl    stream-json 로그에서 개인정보를 가린 사본
  traces/results/<run_id>.json  채점 결과(공개 · 숨긴 테스트) + 로그에서 뽑은 지표
  traces/results.csv            18회 전체 표
  traces/summary.md             작업 × 조건 중앙값 표와 사전 판정식 적용 결과

가리는 것: hook 이벤트의 출력 본문(전역 메모리 · 플러그인 안내문이 들어 있다),
init 메시지의 긴 목록(개수와 플러그인 이름만 남긴다), commands_changed 의 명령 목록(개수만),
사용자 이름이 든 로컬 경로.
"""
import argparse
import csv
import getpass
import json
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TASK_ORDER = ["parse-log", "refactor-util", "fix-failing"]
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SCRUB = [
    (re.compile(r"[A-Za-z]:(\\\\|\\|/)Users(\\\\|\\|/)[^\\/\"']+", re.I), "<HOME>"),
    (re.compile(r"/c/Users/[^/\"']+", re.I), "<HOME>"),
    (re.compile(re.escape(getpass.getuser()), re.I), "<USER>"),
    (re.compile(r"[\w.+-]+@gmail\.com", re.I), "<EMAIL>"),
]


def scrub(text):
    for pat, rep in SCRUB:
        text = pat.sub(rep, text)
    return text


def sanitize_event(m):
    if m.get("type") == "system" and str(m.get("subtype", "")).startswith("hook"):
        keep = {k: m[k] for k in ("type", "subtype", "hook_name", "hook_event") if k in m}
        keep["output"] = "<생략: 전역 훅 출력>"
        return keep
    if m.get("type") == "system" and m.get("subtype") == "commands_changed":
        m = dict(m)
        for k, v in list(m.items()):
            if isinstance(v, list):
                m[k + "_count"] = len(v)
                m[k] = "<생략>"
        return m
    if m.get("type") == "system" and m.get("subtype") == "init":
        m = dict(m)
        for k in ("tools", "mcp_servers", "slash_commands", "terminal_slash_commands", "skills", "agents"):
            if isinstance(m.get(k), list):
                m[k + "_count"] = len(m[k])
                m[k] = "<생략>"
        if isinstance(m.get("plugins"), list):
            m["plugins"] = [p.get("name") if isinstance(p, dict) else p for p in m["plugins"]]
        for k in ("memory_paths", "scratchpad_path", "messaging_socket_path", "powershell_path"):
            if k in m:
                m[k] = "<생략>"
    return m


def total_input(u):
    return u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)


def metrics(jsonl):
    d = {"hooks_started": 0, "tool_calls": {}, "first_request_input": None, "result": None}
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if m.get("type") == "system" and m.get("subtype") == "hook_started":
            d["hooks_started"] += 1
        elif m.get("type") == "system" and m.get("subtype") == "init":
            for k in ("tools", "skills", "plugins", "mcp_servers"):
                d[k + "_count"] = len(m.get(k) or [])
        elif m.get("type") == "assistant":
            msg = m.get("message", {})
            if d["first_request_input"] is None and msg.get("usage"):
                d["first_request_input"] = total_input(msg["usage"])
            for b in msg.get("content", []):
                if b.get("type") == "tool_use":
                    d["tool_calls"][b["name"]] = d["tool_calls"].get(b["name"], 0) + 1
        elif m.get("type") == "result":
            d["result"] = m
    r = d.pop("result") or {}
    u = r.get("usage", {})
    d.update(
        result_subtype=r.get("subtype"), is_error=r.get("is_error"),
        duration_ms=r.get("duration_ms"), num_turns=r.get("num_turns"),
        cost_usd=round(r.get("total_cost_usd", 0) or 0, 4),
        input_tokens=u.get("input_tokens"), cache_creation=u.get("cache_creation_input_tokens"),
        cache_read=u.get("cache_read_input_tokens"), output_tokens=u.get("output_tokens"),
        total_input=total_input(u) if u else None,
        permission_denials=len(r.get("permission_denials") or []),
        edits=sum(v for k, v in d["tool_calls"].items() if k in EDIT_TOOLS),
        skill_calls=d["tool_calls"].get("Skill", 0),
        tool_calls_total=sum(d["tool_calls"].values()),
    )
    return d


def median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, type=Path)
    args = ap.parse_args()
    out_runs = REPO / "traces" / "runs"
    out_res = REPO / "traces" / "results"
    out_runs.mkdir(parents=True, exist_ok=True)
    out_res.mkdir(parents=True, exist_ok=True)

    rows = []
    for res_file in sorted((args.work / "results").glob("*.json")):
        res = json.loads(res_file.read_text(encoding="utf-8"))
        raw = args.work / "raw" / f"{res['run_id']}.jsonl"
        met = metrics(raw)
        clean = []
        for line in raw.read_text(encoding="utf-8").splitlines():
            try:
                clean.append(json.dumps(sanitize_event(json.loads(line)), ensure_ascii=False))
            except json.JSONDecodeError:
                pass
        (out_runs / raw.name).write_text(scrub("\n".join(clean)) + "\n", encoding="utf-8")
        res["passed"] = bool(res["visible_ok"] and res["hidden_ok"] and res["test_file_unchanged"])
        res["metrics"] = met
        (out_res / res_file.name).write_text(scrub(json.dumps(res, ensure_ascii=False, indent=2)), encoding="utf-8")
        rows.append(res)

    fields = ["index", "task", "condition", "rep", "passed", "visible_ok", "hidden_ok", "test_file_unchanged",
              "duration_ms", "num_turns", "total_input", "first_request_input", "cache_read", "cache_creation",
              "output_tokens", "cost_usd", "edits", "tool_calls_total", "skill_calls", "permission_denials",
              "hooks_started", "tools_count", "skills_count", "plugins_count", "mcp_servers_count", "wall_s"]
    with open(REPO / "traces" / "results.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            flat = {**r, **r["metrics"]}
            w.writerow({k: flat.get(k) for k in fields})

    # 작업 × 조건 집계와 사전 판정식
    lines = ["# summary — 작업 × 조건 (3회씩)", "",
             "| 작업 | 조건 | 통과 | 총 입력 토큰 중앙값 | 첫 요청 입력 중앙값 | 캐시 쓰기 중앙값 | 소요 시간 중앙값(초) | API 밖 시간 중앙값(초) | 턴 중앙값 | 수정 중앙값 | 스킬 호출 합 | 권한 거부 합 | 비용 합(USD) |",
             "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    agg = {}
    for t in TASK_ORDER:
        for c in ("A", "B"):
            rs = [r for r in rows if r["task"] == t and r["condition"] == c]
            if not rs:
                continue
            ms = [r["metrics"] for r in rs]
            a = {
                "n": len(rs), "passed": sum(r["passed"] for r in rs),
                "tok": median([m["total_input"] for m in ms]),
                "first": median([m["first_request_input"] for m in ms]),
                "sec": (median([m["duration_ms"] for m in ms]) or 0) / 1000,
                "cache_w": median([m["cache_creation"] for m in ms]),
                # 실행기 벽시계 시간 - API 소요 시간: 시작 · 훅 · 채점(양 조건 같음)에 든 시간
                "outside": median([r["wall_s"] - r["metrics"]["duration_ms"] / 1000 for r in rs]),
                "turns": median([m["num_turns"] for m in ms]), "edits": median([m["edits"] for m in ms]),
                "skills": sum(m["skill_calls"] for m in ms), "denials": sum(m["permission_denials"] for m in ms),
                "cost": round(sum(m["cost_usd"] for m in ms), 4),
            }
            agg[(t, c)] = a
            lines.append(f"| {t} | {c} | {a['passed']}/{a['n']} | {a['tok']:,.0f} | {a['first']:,.0f} | {a['cache_w']:,.0f} | {a['sec']:.1f} | {a['outside']:.1f} | "
                         f"{a['turns']} | {a['edits']} | {a['skills']} | {a['denials']} | {a['cost']} |")

    if len(agg) < 2 * len(TASK_ORDER):
        lines += ["", "(작업 × 조건이 다 채워지지 않아 판정하지 않음)"]
        (REPO / "traces" / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines))
        return
    cond1 = all(agg[(t, "B")]["passed"] >= agg[(t, "A")]["passed"] for t in TASK_ORDER)
    cheaper = [t for t in TASK_ORDER
               if agg[(t, "B")]["tok"] < agg[(t, "A")]["tok"] and agg[(t, "B")]["sec"] < agg[(t, "A")]["sec"]]
    cond2 = len(cheaper) >= 2
    verdict = "지지" if (cond1 and cond2) else "기각"
    lines += ["", "## 사전 판정식 적용", "",
              f"- ① 품질 유지 (세 작업 모두 B 통과 ≥ A): **{'만족' if cond1 else '불만족'}**",
              f"- ② 비용 감소 (토큰 · 시간 중앙값이 둘 다 작은 작업 2개 이상): **{'만족' if cond2 else '불만족'}** — 해당 작업: {', '.join(cheaper) or '없음'}",
              f"- 판정: **{verdict}**"]
    (REPO / "traces" / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
