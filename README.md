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


uv run uvicorn app.main:app --reload --reload-dir app --port 8000