# LGEA Personas

이 디렉토리는 브랜치별로 흩어진 페르소나 프롬프트를 연구용 공통 포맷으로 변환해 저장하는 위치입니다.

목표:
- `drug`, `bomb`, `adult` 등 브랜치별 프롬프트를 수집
- 공통 스키마로 정규화
- 현재 브랜치의 연구 러너가 직접 로드할 수 있게 관리

예정 포맷:
- `persona_id`
- `source_branch`
- `category`
- `system_prompt`
- `notes`
