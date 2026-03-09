# Day 4. Error Analysis

## 환경 설정

이 미션은 코드 구현이 아닌 **분석 과제**입니다.
Day 3까지 완성한 Lumi 챗봇을 사용합니다.

## 사전 준비

- Day 3까지 완성된 Lumi 챗봇 (Langfuse 연동 완료)
- Langfuse 계정 (Day 3에서 설정 완료)
- Google Spreadsheet 또는 Excel

## 미션 목표

1. 오류 분석의 개념과 중요성 이해
2. 트레이스 데이터를 직접 분석하여 문제점 발견
3. 오류 카테고리 분류 및 우선순위 결정
4. 다음 액션 플랜 수립

## 제출물

1. **스프레드시트** (Google Sheets)
   - 최소 50개 트레이스 분석
   - 카테고리 분류 완료
2. **분석 레포트** (Markdown 파일)
   - `templates/error_analysis_template.md` 형식 참고

## 파일 구조

```
day4-mission/
├── README.md                              # 이 파일
├── templates/
├   ├── LLM-As-a-Judge.gs                  # Apps Script에서 LLM-As-a-Judge 수행
├   └── preprocess_langfuse_export_data.py # Langfuse 데이터 전처리
└── templates/
    └── error_analysis_template.md         # 분석 레포트 템플릿
```
