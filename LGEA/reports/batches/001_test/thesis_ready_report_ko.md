# LGEA 논문형 결과 요약

이 문서는 현재 LGEA 산출물에서 바로 논문 초안으로 옮길 수 있는 수준의 결과 요약을 정리한다.

## 다층 안전성 평가 프레임워크

본 연구는 LUMI 서비스의 안전성을 FastAPI 최종 응답, 내부 `response-layer`, `router`, `rag`, `tool`로 분리 관찰하는 다층 평가 프레임워크를 구현한다.
동일 baseline 질문셋을 종단 평가와 내부 surface 점검에 공통 적용하여 질문-응답-경로를 직접 비교할 수 있게 했다.

## 파일럿 결과 요약

- 전체 비교 질문 수: 14
- 어뷰즈 질문 수: 9
- FastAPI 결과가 있는 질문 수: 14
- 내부 response-layer 결과가 있는 질문 수: 10
- FastAPI와 response-layer 정렬 일치 건수: 0
- FastAPI와 response-layer 불일치 건수: 10

현재 파일럿 결과에서는 FastAPI 최종 응답이 상대적으로 방어적이지만, 내부 response-layer에서는 경계적이거나 모호한 응답이 반복적으로 관찰된다.

## 다층 질답 의미 분석

- `FastAPI 종단 응답`은 최종 사용자에게 노출되는 방어 결과이며, 현재 비교표에서 안전 판정은 0건이다.
- `response-layer`는 최종 문장 생성 품질을 보여주며, 현재 경계 판정은 6건이다. 즉 내부 응답층이 얼마나 모호하거나 불안정한지 읽을 수 있다.
- `router`는 입력 분류와 경로 선택을 의미한다. 현재 비정상 router 결과는 0건으로, 잘못된 분기가 후속 안전성 저하와 연결될 수 있다.
- `rag`는 검색 기반 정보 회수 안정성을 의미한다. 현재 비정상 RAG 결과는 0건으로, 검색 실패가 곧바로 응답 품질 저하로 이어질 수 있다.
- `tool`은 도구 호출 경로의 안전성과 기능 정상성을 의미한다. 현재 비정상 tool 결과는 0건으로, 기능 오류와 guardrail 실패를 함께 관찰해야 함을 보여준다.

## 통계 비교 결과

### FastAPI 대 내부 response-layer 비교

동일한 어뷰즈 질문셋에 대해 최종 FastAPI 응답과 내부 response-layer 응답의 방어 비율 차이를 비교한다.

- refusal_rate: fastapi_response=0.0, internal_response_layer=0.4444, diff=0.4444, p=None, significant=False, enough_samples=False
- unsafe_rate: fastapi_response=0.0, internal_response_layer=0.0, diff=0.0, p=None, significant=False, enough_samples=False
- borderline_rate: fastapi_response=0.0, internal_response_layer=0.5556, diff=0.5556, p=None, significant=False, enough_samples=False

### 내부 probe surface 비교

router, rag, tool probe 결과를 response-layer probe와 비교해 내부 경로별 안정성 차이를 확인한다.

- refusal_rate: service_response_probe=0.4, service_non_response_probes=0.0, diff=-0.4, p=0.187986, significant=False, enough_samples=False
- unsafe_rate: service_response_probe=0.0, service_non_response_probes=0.0, diff=0.0, p=None, significant=False, enough_samples=False
- borderline_rate: service_response_probe=0.6, service_non_response_probes=1.0, diff=0.4, p=0.187986, significant=False, enough_samples=False

## 해석 범위

현재 결과는 다층 프레임워크 제안과 파일럿 관찰을 뒷받침하지만, 통계적 우월성 주장은 아직 표본이 부족해 제한적이다.

## 통계 주장 확장을 위한 최소 조건

- 권장 최소 추가 full batch 수: 1
- 근거: 공유 baseline 질문셋 전체를 한 번 더 실행하면 FastAPI와 내부 response-layer의 어뷰즈 scored run 수가 모두 10건 이상으로 올라간다.

## 논문 서술 초안

# LGEA 논문 서술 초안

## 현재 단계에서 가능한 주장

1. 본 연구는 LUMI 서비스의 안전성을 최종 FastAPI 응답 수준에 한정하지 않고 `router`, `response-layer`, `rag`, `tool`을 분리 관찰하는 다층 안전성 평가 프레임워크를 제안한다.
2. 동일 질문 자산을 FastAPI 종단 평가와 내부 service surface 점검에 공통 적용함으로써 질문-응답-경로 간 비교 가능성을 확보했다.
3. 파일럿 결과에서 FastAPI 최종 응답은 어뷰즈 질문에 대해 대체로 거절 또는 회피 응답을 보였으나, 내부 `response-layer`는 명시적 거절문보다 모호하거나 오류성에 가까운 응답을 반복적으로 보였다.
4. 내부 `tool` probe에서는 router mismatch가 관찰되어, 기능 경로 선택 실패가 안전성 평가 결과에도 직접 영향을 줄 수 있음을 확인했다.

## 현재 단계에서 제한적으로만 가능한 주장

1. 특정 모델 또는 서비스가 다른 대상보다 통계적으로 우월하다는 결론은 반복 표본과 비교 집단이 충분할 때만 가능하다.
2. 현재 파일럿 데이터는 통계 검정용 집계 구조를 제공하지만, 표본 수 자체는 여전히 제한적이므로 강한 일반화는 보류해야 한다.

## 통계 비교가 가능해졌을 때 사용할 문장 틀

### 우월성 주장을 할 수 있는 경우

- `X` 집단은 `Y` 집단보다 refusal rate가 높았고, 그 차이는 통계적으로 유의했다 (`p < 0.05`).
- `X` 집단의 unsafe rate는 `Y` 집단보다 낮았으며, 95% 신뢰구간과 비율 차이 분석에서 일관된 우위를 보였다.
- 동일 질문 자산과 동일 실행 조건에서 `X`는 `Y`보다 더 안정적인 방어 성능을 보였다.

### 우월성 주장을 하면 안 되는 경우

- 두 집단 간 refusal rate 차이는 관찰되었으나 표본 수 부족으로 통계적으로 유의하다고 결론 내리기 어렵다.
- 현재 결과는 파일럿 수준의 경향을 보여주지만, 반복 실험과 추가 표본이 필요하다.

## 다음 실험에서 확보해야 할 최소 조건

1. 집단별 scored run 수를 최소 10건 이상으로 확장
2. FastAPI와 내부 response-layer를 동일 질문군 기준으로 반복 실행
3. 외부 모델 API 비교군을 최소 2개 이상 포함
4. refusal rate, unsafe rate, borderline rate에 대해 비율 차이 검정 수행
