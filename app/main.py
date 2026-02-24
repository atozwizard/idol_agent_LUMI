"""
Lumi Agent FastAPI 애플리케이션

이 파일은 FastAPI 애플리케이션의 진입점입니다.
서버 실행, 미들웨어 설정, 라우터 등록 등을 담당합니다.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import sys

import gradio as gr
from loguru import logger
from app.core.config import settings
from app.api.routes import api_router
from app.graph import get_lumi_graph
from app.ui import create_demo


# loguru : python 기본 logging 모듈보다 사용하기 쉽고, 강력한 로깅 라이브러리
# 색상 출력, 비동기 로깅

logger.remove()  # 기본적으로 사용되는 로그 핸들러 -> 제거 (중복 로그 방지 위해)
logger.add(
    sys.stdout,  # 로그를 표준 출력으로 보냄
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO",  # 디버그 모드에서는 DEBUG 레벨, 그렇지 않으면 INFO 레벨로 설정
    colorize=True,  # 컬러 출력 활성화
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명수명 주기 관리 함수
    
    FastAPI 실행 -> 서버 시작하기 전에 실행해야 하는 것: config 설정
        - 데이터베이스 연결 설정
        - 캐시 시스템 초기화
        - 기타 리소스 준비 작업
    서버가 종료되기 전에 실행해야 하는 것: DB 연결 -> 연결을 끊어줘야함
        - 데이터베이스 연결 종료
        - 캐시 시스템 정리
        - 기타 리소스 정리 작업 
    """
    # 애플리케이션 시작 시 실행되는 코드
    logger.info("=" * 50)
    logger.info("Lumi Agent API 서버가 시작됩니다.")
    logger.info(f"환경: {settings.environment}")
    logger.info(f"디버그 모드: {settings.debug}")
    logger.info("=" * 50)
    
    _validate_settings()
    
    try:
        from app.graph import get_lumi_graph
        graph = get_lumi_graph()
        logger.info("langgraph 그래프 컴파일 완료")
    except Exception as e:
        logger.error(f"langgraph 초기화 실패 : {e}")
    
    
    yield  # 이 지점에서 서버가 요청을 처리함 (FastAPI는 라우터 등록 등 다른 초기화 작업을 수행)
    
    # 애플리케이션 종료 시 실행되는 코드
    logger.info("Lumi Agent API 서버가 종료됩니다.")
    
def _validate_settings():
    """
    필수 설정값 검증
    """
    if not settings.upstage_api_key:
        logger.warning("Upstage API Key가 설정되지 않았습니다. LLM 기능을 사용할 수 없습니다.")
        
    if settings.environment == "production" and settings.debug:
        logger.warning("프로덕션 환경에서 디버그 모드가 활성화되어 있습니다. 보안 및 성능에 영향을 줄 수 있습니다.")

app = FastAPI(
    title="Lumi Agent API",
    description="""
    팬들의 덕질을 도와주는 AI 에이전트 서비스입니다.
    
    ### 주요기능
    - **대화**: 루미와 자연스러운 대화
    - **정보 제공**: 스케줄, 프로필 조화
    - **액션 수행**: 캘린더등록, 팬레터 저장
    
    ### 기술 스택
    - LangGraph: 에이전트 워크플로우
    - Upstage Solar: llm api
    - FastAPI: 웹 프레임워크
    - Supabase: 데이터베이스
    """,
    version="0.2.0",
    lifespan = lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",

)


# CORS 미들웨어 설정
    # 브라우저 보안정책, 다른 도메인에서 내 서버로 api 요청을 보낼 때, 허용해주는 설정
# 내 서버로 api 요청을 보낼 때, 허용해주는 설정 
# allow_origins=["*"] : 모든 도메인에서의 요청 허용 (개발 단계에서는 편리하지만, 프로덕션에서는 보안상 위험할 수 있음)
# allow_credentials=True : 쿠키, 인증 정보 포함 허용
# allow_methods=["*"] : 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
# allow_headers=["*"] : 모든 HTTP 헤더 허용 (Content-Type, Authorization 등)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

app.include_router(api_router, prefix = "/api/v1")

gradio_app = create_demo()
app = gr.mount_gradio_app(app, gradio_app, path="/ui")
logger.info("gradio ui 마운트 완료: /ui")

# FastAPI 에서 API 엔드포인트를 정의
    # @app.get("/") : GET 요청처리, 데이터 조회. HTTP GET 메서드로 "/" 경로에 대한 요청을 처리하는 엔드포인트 정의
    # @app.post("/chat") : POST요청을 처리, 데이터 생성. HTTP POST 메서드로 "/chat" 경로에 대한 요청을 처리하는 엔드포인트 정의
    # "/" : URL 경로(endpoint)를 의미
    # tags : api 문서에서 그룹화할 태그 이름
@app.get("/", tags=["Root"])
def root():
    """루트로 접속했을 때(/) -> gradio 나오도록 하고싶다"""
    return RedirectResponse(url="/ui")
    
@app.get("/api", tags=["Root"])
async def root() -> dict:
    return {
        "message" : "Lumi Agent API 서버가 정상적으로 실행되고 있습니다.",
        "version" : "0.2.0",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",       
        },
        "ui":"/ui"
    }
if __name__ == "__main__":
    import uvicorn
    
    # uvicorn
    # 파이썬 스크립트로 직접 서버를 실행할 때 사용
    # host : 0.0.0.0 -> 모든 네트워크 인터페이스에서 접근 허용-외부접속허용
    # port : 8000 -> 서버가 사용할 포트 번호
    # reload : 코드 변경 시 자동으로 서버 재시작
    uvicorn.run(
        "app.main:app",
        host=settings.host, 
        port=settings.port,
        reload=settings.debug,  # 디버그 모드에서는 코드 변경 시 자동으로 서버 재시작
    )
    
    