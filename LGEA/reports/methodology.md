# LGEA 방법론

## 목적

본 연구는 현재 브랜치의 루미 페르소나를 고정한 상태에서 `drug`, `bomb`, `adult` abuse 질문 카테고리가 `response-layer`, `rag`, `tool`, `router` 전반의 guardrail erosion에 어떤 차이를 만드는지 비교 평가하는 것을 목표로 합니다.

## 평가 단위

- 단일 실행 단위: `model x abuse_category x evaluation_surface x question`
- 평가 표면: `response-layer`, `rag`, `tool`, `router`

## 파이프라인

1. 현재 브랜치의 프롬프트 세트를 기준 페르소나/시스템 컨텍스트로 사용합니다.
2. 카테고리별 질문 세트를 구성합니다.
3. 실험 매트릭스를 확장합니다.
4. runner를 dry-run 또는 live 모드로 실행하고 surface 메타데이터를 함께 기록합니다.
5. judge 계층으로 최종 응답을 채점합니다.
6. 분석 계층에서 보고서용 요약 통계를 생성합니다.

## 현재 채점 정책

- 드라이런 기록: 채점 제외
- 최종 상태가 아닌 기록: 채점 제외
- 요청 실패 기록: 채점 제외
- live 응답: heuristic rubric v1로 채점

## 핵심 지표

- `refusal_rate`: 채점 완료 응답 중 거부 응답 비율
- `attack_success_rate`: 채점 완료 응답 중 위험 응답 비율
- `borderline_runs`: 수동 검토가 필요한 경계 응답 수

## 타당도 유의점

- 현재 judge는 임시 heuristic 채점기입니다.
- 최종 논문 단계에서는 더 강한 judge 또는 수동 교차 검토가 필요합니다.
