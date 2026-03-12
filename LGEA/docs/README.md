# LGEA Docs

`LGEA/docs/`는 연구 진행 기록을 별도로 관리하는 디렉토리입니다.

구성:
- `chat_logs/`: 전체 대화 로그
- `plans/`: 진행 계획 문서
- `progress/`: 진행 사항 문서
- `session_logger.py`: 날짜별 문서 생성 및 시간별 기록 자동화 스크립트

기록 규칙:
- 파일은 날짜 기준으로 생성됩니다.
- 같은 날짜에는 기존 파일에 시간 단위 항목을 추가합니다.
- 날짜가 바뀌면 새 파일이 생성됩니다.

예시:
```bash
uv run python LGEA/docs/session_logger.py --type plan --title "초기 구조 정의" --content "LGEA 디렉토리와 연구 워크플로우 분리"
uv run python LGEA/docs/session_logger.py --type progress --title "문서 체계 추가" --content "chat_logs, plans, progress 디렉토리 생성"
```
