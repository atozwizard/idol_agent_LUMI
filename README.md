# AI Backend Engineering(Service Deployment, LLMOps) Starter Code

## 환경 설정
```
uv sync
```

## 코드 강의
- 바닥부터 구현하는 과정을 보여줄 예정
    - 단, 일부 코드는 구현된 것을 가져와서 사용
- 추천하는 학습 방식
    - 구현하는 흐름을 보기. 처음에 어떤 파일을 수정했는가? 그리고 어떤 파일을 수정했는가?
    - 이런 과정을 잘 파악하는 것이 중요함

## 오늘 할 부분
- 큰 뼈대를 잡을 예정
- 강의 자료에서 Supabase 설정은 했다고 가정
    - app/main.py
    - app/core/config.py
    - app/schemas/chat.py
- .env 설정 ->config.py -> chat.py ->main.py
    - 사용할떄 : main.py를 실행 -> config.py, chat.py

# TODO 정리
- [v] config.py 구현
- [v] schemas/chat.py 구현
    - [v] ChatRequest 클래스 정의
    - [v] ChatResponse 클래스 정의
- [v] main.py 구현
    - [v] Fastapi 앱 인스턴스생성
    - [v] lifespan 함수 정의
    - [v] CORS 미들웨어 추가
    - [v] 루트 엔드포인트 정의
    - [v] __main__ 실행 블록


# service deployment 2강
- langgraph 구현
## 오늘 할 것
- 노트북 파일을 스크립트 파일로 변환
    - 그 과정에서 필요한 것들 추가(DB연결)

## TODO 정리
- [v] graph 구현 : notebook to py
    - [v] state.py
    - [v] nodes.py
        - [v] router : 메시지 의도 분류
            - core/prompt.py
        - [v] rag : 문서검색
            - [v] repositories
        - [v] tool : 툴 실행
            - [v] tools/executor.py
        - [v] response 노드 구현
    - [v] edges.py
    - [v] graph.py
- [v] api server
    - [v] chat.py
- [v] ui.py
- [v] main.py

## 오늘 강의 핵심
- 바닥부터 다 구현을 해야한다가 아님
- 구현하는 과정을 익히기 위해 본것
    - 노트북 파일에서 스크립트로 변화할 때 이렇게 하면 되는구나, 감
    - 코드 복습
    - print
    



uv run uvicorn app.main:app --reload --reload-dir app --port 8000



### 프로젝트 구조

```
app/
├── core/
│   ├── config.py          ← 설정 관리 (pydantic-settings)
│   └── prompts.py         ← 프롬프트 분리
├── schemas/
│   └── chat.py            ← API 요청/응답 모델
├── graph/                  ← 노트북에서 만든 에이전트
│   ├── state.py           ← State 정의
│   ├── nodes.py           ← 노드 구현
│   ├── edges.py           ← 라우팅 로직
│   └── graph.py           ← 그래프 조립 + 싱글톤
├── repositories/           ← DB 접근 계층 (Mock → Real)
│   ├── rag.py             ← RAG 검색 (Supabase pgvector)
│   ├── schedule.py        ← 스케줄 조회
│   └── fan_letter.py      ← 팬레터 저장
├── tools/
│   └── executor.py        ← Tool 실행 (Repository 활용)
├── api/routes/
│   └── chat.py            ← REST API 엔드포인트
└── main.py                ← FastAPI 앱 (lifespan, CORS)
```