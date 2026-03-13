# Persona Source Inventory

현재 운영 방향에서 이 문서는 `브랜치별 유해 프롬프트 출처 추적`이 아니라 `현재 기준 페르소나와 질문 카테고리의 역할 정의`를 위한 인벤토리로 사용한다.

원칙:
- 실험 기준 시스템 페르소나는 현재 브랜치 `app/core/prompts.py`의 `RESPONSE_PROMPT`다.
- `drug`, `bomb`, `adult`는 질문 카테고리이며, 별도 시스템 프롬프트 소스가 아니다.
- 연구 보고서는 실제 질문/응답 로그를 남기되 유해 내용을 확대 재생산하지 않는다.

## Sources

| persona_id | source_branch | source_file | target_sections | evaluation_focus | status |
| --- | --- | --- | --- | --- | --- |
| `drug` | `current_branch` | `app/core/prompts.py` | `RESPONSE_PROMPT` | 약물 관련 abuse 질문에 대한 거절, 대안 제시, 정책 준수 여부 | active |
| `bomb` | `current_branch` | `app/core/prompts.py` | `RESPONSE_PROMPT` | 폭발물 관련 abuse 질문에 대한 거절, 안전 경계 유지 여부 | active |
| `adult` | `current_branch` | `app/core/prompts.py` | `RESPONSE_PROMPT` | 성적 고수위 요청에 대한 경계 설정과 전환 응답 여부 | active |

## Normalization Notes

- 세 카테고리는 동일한 시스템 페르소나를 공유한다.
- 질문 카테고리만 달라지고, 모델별 응답 차이를 관찰한다.
- 연구용 공통 포맷에서는 아래 항목으로 정규화한다.
  - `persona_id`
  - `source_branch`
  - `source_file`
  - `prompt_targets`
  - `injection_style`
  - `response_policy_shift`

## Execution Notes

1. 현재 브랜치의 `RESPONSE_PROMPT`를 기준으로 사용한다.
2. `drug`, `bomb`, `adult` 질문 세트를 분리한다.
3. 러너는 카테고리와 질문 ID를 기준으로 실행 매트릭스를 만든다.
4. 질문과 응답은 로그 및 보고서에 함께 남긴다.
