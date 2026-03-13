# LGEA Prompts

`LGEA/prompts/`는 연구 실행 시 사용할 현재 브랜치 prompt bundle 선택기를 둔다.

원칙:
- 모든 테스트는 현재 브랜치 `app/core/prompts.py`를 기준으로 한다.
- `plain`, `drug`, `bomb`, `adult`는 시스템 프롬프트 파일 분기가 아니라 테스트 프로필 이름이다.
- `drug`, `bomb`, `adult` 프로필은 동일한 `RESPONSE_PROMPT`를 사용하되, 질문셋과 보고 메타데이터만 달라진다.

현재 파일:
- `branch_prompt_loader.py`: 현재 브랜치 prompt bundle 로더
- `drug_prompt.py`: `drug` 테스트 프로필용 bundle
- `bomb_prompt.py`: `bomb` 테스트 프로필용 bundle
- `adult_prompt.py`: `adult` 테스트 프로필용 bundle
- `prompt_selector.py`: 테스트 프로필별 bundle 선택기
