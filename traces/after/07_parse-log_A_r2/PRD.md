# PRD — parse.py (ERROR 로그 → 마크다운 표)

## [무엇]
`sample.log` 에서 ERROR 레벨 줄만 골라 마크다운 표로 출력하는 작은 CLI 스크립트.

## [기능]
- `parse_errors(lines)` → `[("날짜 시각", 메시지), ...]` 튜플 목록 반환
- `python parse.py [로그파일]` 실행 (기본값 `sample.log`) → `| 시각 | 메시지 |` 표 출력
- 형식에 맞지 않는 줄은 건너뛴다 (예외를 내지 않는다)

## [저장/데이터 설계]
- 저장 없음. 입력은 텍스트 로그, 출력은 stdout.
- 줄 형식: `YYYY-MM-DD HH:MM:SS LEVEL 메시지` — 레벨은 **세 번째 칸**(공백 구분).

## [내가 넣고 싶은 기능]
- 없음 (요청 범위만 구현).

## [규칙 / 가정]
- 레벨 판정은 세 번째 칸이 정확히 `ERROR` 일 때만. 메시지 안의 "ERROR" 단어는 무시한다
  (예: `INFO user searched for ERROR codes` 는 제외).
- 날짜·시각이 `YYYY-MM-DD HH:MM:SS` 모양이 아니거나, 레벨/메시지가 없는 줄은 형식 불일치로 건너뜀.
- 메시지 안의 `|` 는 표가 깨지지 않도록 `\|` 로 이스케이프.
- ERROR 줄이 없으면 헤더만 출력.
- 파일은 UTF-8 로 읽고 stdout 도 UTF-8 로 맞춘다 (Windows 콘솔 대비).

## [통과 기준]
1. `python -m unittest test_parse` 가 전부 통과한다.
2. `python parse.py` 출력에 ERROR 3건만 있고 INFO/WARNING/DEBUG 메시지는 없다.
3. "ERROR codes" 가 메시지에 들어있는 INFO 줄은 표에 나오지 않는다.
4. 형식이 깨진 줄(빈 줄, 짧은 줄, 날짜 아닌 줄)이 섞여도 오류 없이 건너뛴다.
5. 메시지에 `|` 가 있어도 표 열이 늘어나지 않는다.
