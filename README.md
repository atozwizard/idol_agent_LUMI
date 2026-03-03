# AI Backend Engineering(Service Deployment, LLMOps) Starter Code

## 환경 설정

```bash
# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
```

## 실행

```bash
# Docker 이미지 빌드
docker build -t lumi-agent .

# Docker Compose로 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 종료
docker-compose down
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


# service deploy 3강
## 오늘 할 일 (목표)
- 2강에서 만든 MVP -> 개선
- 스트리밍을 구현할 예정, 노드 상태 + 토큰 스트리밍을 동시에 보여주기
- 실시간 스트리밍 !

## TODO
- [v] app/schemas/chat.py : StreamEvent, to_see()
- [v] app/api/routes/chat.py : SSE 구현, stream_with_status 함수
    - [V] SSE 엔드포인트 추가
- [v] app/ui.py : 스트리밍 데이터를 받아서 처리할 수 있도록 함수
- [v] UI에서 확인을 할 예정
- [v] router쪽의 이슈 해결을 위한 코드

## 정리
- SSE 구현을 위해서 어떻게 하는가?
- yield 이벤트 발생 -> 이벤트 형태 정의 -> 그거에 맞게 로직
- stream_with_status 로직 : 읽어보기
- 바닥부터 다 구현이 아니라, 일단 구현된 것을 읽을 수 있는지? -> 이해가 되는지?


uv run uvicorn app.main:app --reload --reload-dir app --port 8000

# service deploy 5강
## 오늘 할 일
- docker에 대한 이해(기본 명령어)
- dockerfile, docker-compose.yml
- api/routes/health.py

## docker 사용 흐름
-1) docker image를 가져다가 바로 쓴다 -> docker image가 저장된 registry에서 검색 후 활용
    - docker hub, github registry
-2) 특정 도커 이미지를 ㅋ기반으로 나만의 이미지를 만들어서 활용 -> docker images 보이도록 docker image build
    - 컨테이너를 실행할 때는 docker run
-3) docker compose 사용해서 캠핑 풀세트를 만들어서 활용


# llmops 1강
## 오늘 할 일
- 파일을 100% 이해하는 것이 목표가 아님
- 코드의 흐름을 파악하면서 어디서 호출이 되고, 그 호출이 어떻게 활용되는지?
- lite llm

## todo
- [v] app/core/config.py
- [v] app/core/llm.py : 코드 읽기에 집중, 이전 코드와 어떤 부분이 바뀌는지?
- [v] app/graph/nodes.py
- [v] 성능 최적화



## llm.py 핵심
- get_llm : 과거에는 chatupstage -> litellmchatmodel. 입구. env 설정에 따라서 litellmchatmodel 반환, chatupstage 반환
- litellmchatmodel : litellm의 핵심기능을 감싼 클래스, basechatmodel 상속 -> 약속
    - _get_router() : retry, fallback
    - _agenerate, _astream : 실제 호출
    - 캐시 : dict


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
