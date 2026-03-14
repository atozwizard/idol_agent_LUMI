# LGEA Prompts

`LGEA/prompts/`는 현재 브랜치의 LUMI 프롬프트 자산과 연구용 질문 확장기를 관리한다.

원칙:
- 모든 평가는 현재 브랜치의 `app/core/prompts.py`를 기준으로 한다.
- `drug`, `bomb`, `adult`는 별도 서비스 프롬프트가 아니라 질문 카테고리와 평가 메타데이터로 구분한다.
- 질문 확장기는 원문보다 더 위험한 실행 정보를 추가하지 않는 범위에서만 변형 질문을 만든다.

현재 파일:
- `branch_prompt_loader.py`: 현재 브랜치 prompt bundle 로더
- `drug_prompt.py`: `drug` 테스트용 prompt bundle
- `bomb_prompt.py`: `bomb` 테스트용 prompt bundle
- `adult_prompt.py`: `adult` 테스트용 prompt bundle
- `prompt_selector.py`: 테스트 프로파일 기준 bundle 선택기
- `question_expander.py`: `solar-pro2` 기반 질문 확장기
