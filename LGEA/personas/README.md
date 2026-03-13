# LGEA Personas

`LGEA/personas/`는 현재 브랜치의 기준 페르소나와 abuse 질문 카테고리 메타데이터를 관리한다.

원칙:
- 시스템 페르소나는 현재 브랜치 `app/core/prompts.py`의 `RESPONSE_PROMPT`를 사용한다.
- `drug`, `bomb`, `adult`는 별도 브랜치 프롬프트가 아니라 질문 카테고리 식별자다.
- 연구 러너는 현재 페르소나를 유지한 채 카테고리별 질문셋만 바꿔서 실행한다.

핵심 필드:
- `persona_id`: 질문 카테고리 식별자
- `source_branch`: 현재는 항상 `current_branch`
- `source_file`: 기준 시스템 프롬프트 위치
- `response_policy_shift`: 해당 카테고리에서 관찰하려는 안전 응답 초점
