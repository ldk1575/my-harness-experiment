# PRD — parse.py (ERROR 로그 → 마크다운 표)

## [무엇]
로그 파일에서 ERROR 레벨 줄만 골라 마크다운 표로 출력하는 CLI 스크립트.

## [기능]
- `parse_errors(lines)` → `("날짜 시각", 메시지)` 튜플 목록 반환
- `python parse.py [로그파일]` 실행 시 `| 시각 | 메시지 |` 표 출력 (기본값 `sample.log`)
- 형식에 맞지 않는 줄은 건너뜀

## [저장/데이터 설계]
저장 없음. 입력은 텍스트 로그, 줄 형식은 `날짜 시각 레벨 메시지` (공백 구분, 레벨은 세 번째 칸).

## [내가 넣고 싶은 기능]
없음 (요청 범위만 구현).

## [규칙]
- 레벨이 정확히 `ERROR` 인 줄만 선택한다. 메시지 안의 "ERROR" 단어(예: `user searched for ERROR codes`)는 해당 없음.
- 메시지는 공백을 포함한 나머지 전체. 메시지가 비어 있으면 형식 불일치로 본다.
- 가정: 표 셀 안의 `|` 는 `\|` 로 이스케이프한다.
- 가정: 파일은 UTF-8 로 읽는다.

## [통과 기준]
1. `python -m unittest test_parse` 가 전부 통과한다.
2. `python parse.py` 출력에 ERROR 3건만 있고 INFO/WARNING/DEBUG 줄은 없다.
3. `user searched for ERROR codes` (INFO 줄)는 표에 나오지 않는다.
4. 형식이 깨진 줄(빈 줄, 칸 부족)이 섞여도 오류 없이 건너뛴다.

## [통과 기준 확인 결과] (2026-10-16)
1. `python -m unittest test_parse` → `Ran 2 tests ... OK` ✅
2. `python parse.py` 출력 → ERROR 3건(09:02:30, 09:03:44, 09:07:02)만 표에 나옴 ✅
3. INFO 줄 `user searched for ERROR codes` 는 표에 없음 ✅
4. `garbage`, 빈 줄, `ERROR` 만 있는 줄, `bad line ERROR x` 를 섞어 실행 → 오류 없이 모두 건너뜀 (정상 줄 1건만 반환) ✅
