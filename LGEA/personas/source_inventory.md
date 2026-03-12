# Persona Source Inventory

브랜치별 페르소나 프롬프트 출처를 연구용으로 추적하기 위한 인벤토리다.

원칙:
- 원본 브랜치의 유해 프롬프트 본문은 여기로 직접 복제하지 않는다.
- 대신 출처 브랜치, 파일 위치, 변형 유형, 정규화 메모만 기록한다.
- 실제 연구 러너는 이 인벤토리를 기준으로 원본을 읽어와 안전하게 변환한 뒤 사용한다.

## Sources

| persona_id | source_branch | source_file | target_sections | observed_pattern | status |
| --- | --- | --- | --- | --- | --- |
| `drug` | `drug` | `app/core/prompts.py` | `RESPONSE_PROMPT`, `RAG_RESPONSE_PROMPT` | 기본 캐릭터 프롬프트를 약물 범주의 유해 지시, 거절 금지, 공격적 톤으로 덮어씀 | identified |
| `bomb` | `bomb` | `app/core/prompts.py` | `RESPONSE_PROMPT`, `RAG_RESPONSE_PROMPT` | 기본 캐릭터 프롬프트를 폭발물/살상 맥락 지시와 세부 응답 강제 문장으로 덮어씀 | identified |
| `adult` | `adult` | `app/core/prompts.py` | `RESPONSE_PROMPT`, `RAG_RESPONSE_PROMPT` | 기본 캐릭터 프롬프트를 성적 역할 및 노골적 응답 유도 문장으로 덮어씀 | identified |

## Normalization Notes

- 세 브랜치 모두 핵심 차이는 `app/core/prompts.py`에 집중되어 있다.
- 연구용 공통 포맷에서는 아래 항목으로 정규화한다.
  - `persona_id`
  - `source_branch`
  - `source_file`
  - `prompt_targets`
  - `injection_style`
  - `response_policy_shift`
  - `notes`

## Extraction Plan

1. `dev` 브랜치를 baseline으로 둔다.
2. `drug`, `bomb`, `adult` 브랜치의 `app/core/prompts.py`를 읽는다.
3. `RESPONSE_PROMPT`, `RAG_RESPONSE_PROMPT` 변경분만 추출한다.
4. 원문 전체 복사 대신, 실험용 변환 규칙으로 재구성한다.
5. 최종 연구 파이프라인에서는 `RAG_RESPONSE_PROMPT`를 제외하거나 응답층 평가에 맞게 분리한다.
