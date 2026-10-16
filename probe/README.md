# probe — 불편을 수치로 확인한 탐침 2회

본 실험 전에 [experiment-01.md 1절](../experiment-01.md#1-관찰한-불편)의 불편이 느낌인지 확인하려고 실행했다. 본 실험 집계에는 넣지 않는다.

- 일시: 2026-10-16 15시 무렵 · Claude Code 2.1.296 · 모델 `claude-sonnet-5-5`
- 요청: `a.py 내용을 한 줄로 알려줘` (`a.py` 는 `print('hi')` 한 줄)
- A: `claude -p "<요청>" --model claude-sonnet-5-5 --output-format stream-json --verbose --no-session-persistence`
- B: A와 같은 명령에 `--setting-sources project --strict-mcp-config --disable-slash-commands` 를 더함

| 항목 | A (전역 켬) | B (전역 끔) |
| :--- | ---: | ---: |
| 도구 | 358 | 29 |
| 스킬 | 220 | 0 |
| 플러그인 | 24 | 3 (Claude Code 내장) |
| MCP 서버 | 22 | 0 |
| 에이전트 | 44 | 6 |
| 실행된 SessionStart 훅 | 8 | 0 |
| 소요 시간 (`duration_ms`) | 14,665 | 7,754 |
| 턴 수 | 3 | 2 |
| 총 입력 토큰 (input + cache 생성 + cache 읽기) | 181,955 | 63,145 |
| 출력 토큰 | 159 | 112 |
| API 환산 비용 (USD) | 0.2629 | 0.1308 |

두 조건 모두 정답(`print('hi')` 한 줄)을 냈다. 원본 수치는 [`probe_summary.json`](probe_summary.json)에 있다.
