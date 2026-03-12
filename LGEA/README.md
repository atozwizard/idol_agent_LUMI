# LGEA

`LGEA`는 기존 `LUMI` 서비스 코드와 분리된 연구 전용 워크스페이스입니다.

원칙:
- 기존 `app/`, `docs/`, `scripts/`, `tests/` 구조는 유지합니다.
- 연구용 자산은 이 디렉토리 아래에서 별도로 관리합니다.
- 기획 문서는 `docs/LGEA/`에 두고, 실행 자산과 산출물은 `LGEA/`에 둡니다.

현재 확정된 연구 범위:
- 목표: 모델별 API 자체의 guardrail 붕괴 특성 비교
- 대상: LLM 응답층만 평가, RAG 제외
- 변수: 모델 목록, 브랜치별 페르소나, 공격 유형/강도
- 결과물: 논문용 상세 리포트

디렉토리 구조:
- `configs/`: 실험 설정 파일
- `personas/`: 브랜치별 페르소나 프롬프트를 정규화해 저장
- `prompts/`: 공격 생성기 및 Judge용 프롬프트
- `runner/`: 실험 실행기
- `judge/`: 자동 평가기
- `analysis/`: 통계 및 시각화 코드
- `data/`: 중간 산출물과 원시 결과
- `reports/`: 논문용 표, 그래프, 요약 리포트
- `docs/`: 날짜별 대화 로그, 진행 계획, 진행 사항 문서

참고 문서:
- `docs/LGEA/LGEA_projectspec.md`
- `docs/LGEA/project_additional.md`
