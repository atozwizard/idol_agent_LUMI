# LGEA 논문형 결과 요약

이 문서는 현재 LGEA 산출물에서 바로 논문 초안에 옮길 수 있는 수준의 결과 요약을 정리한다.

## 다층 평가 프레임워크

본 연구는 LUMI 서비스의 안전성을 FastAPI 최종 응답, 내부 response-layer, router, rag, tool로 분리 관찰하는 다층 평가 프레임워크를 구현했다.
또한 동일 baseline 질문 자산을 종단 평가와 내부 점검에 공통 적용해 질문-응답-경로 간 비교 가능성을 확보했다.

## 파일럿 결과 요약

- 전체 비교 질문 수: 14
- 어뷰즈 질문 수: 9
- FastAPI 결과가 있는 질문 수: 14
- 내부 response-layer 결과가 있는 질문 수: 10
- tool probe router mismatch 건수: 1 probe 중 관찰 보고는 교차 분석 문서를 따른다.

현재 파일럿 결과에서는 FastAPI 최종 응답이 비교적 방어적인 반면, 내부 response-layer는 다수 질문에서 명시적 거절보다는 모호하거나 오류성에 가까운 응답을 보였다.

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

## 해석 수준

현재 파이프라인은 비율 차이 검정과 신뢰구간까지 계산하므로, 통계적 우월성 주장을 위한 형식적 기반은 갖췄다.
다만 현재 표본에서는 `enough_samples=false`가 유지되므로, 현 단계에서 가능한 주장은 `파일럿 경향 보고`와 `다층 프레임워크 제안`까지다.

## 통계 우월성 주장으로 확장하기 위한 최소 조건

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
