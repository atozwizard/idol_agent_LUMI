"""
pydantic-settings를 사용한 타입 안전한 설정 관리

Pruduction에서는 환경변수를 통해 설정을 주입받는다.
이 모듈은 환경변수를 타입 세이프하게 파싱하고 검증한다.

사용법:
    from app.core import settings

    api_key = settings.upstage_api_key

"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


# pydantic_settings: Pydantic 기반의 설정 관리 라이브러리.
# 환경변수, .env 파일, 기타 소스를 읽어서 클래스 필드에 매핑.
class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스

    pydantic_settiings 를 사용해서 환경변수를 자동으로 로드
    .env 파일 -> Load -> Settings에 추가한다.

    """

    model_config = SettingsConfigDict(
        env_file=".env",
    )
    # Literal : 변수가 가질 수 있는 값을 제한하는 타입 힌트
    environment: Literal["development", "staging", "production", "test"] = "development"

    debug: bool = True

    upstage_api_key: str = ""
    llm_model: str = "solar-pro2"

    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # SUPABASE_URL: str
    # SUPABASE_KEY: str

    host: str = "0.0.0.0"
    port: int = 8000

    openweathermap_api_key: str = ""
    city_name: str = "서울"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


# lru_cache(Least Recently Used Cache) :
# 싱글톤 패턴과 유사한 효과를 내는 데코레이터
# 함수의 반환값(결과)를 캐싱(저장), 동일한 입력에 대해 빠르게 결과를 반환하도록 하는 데코레이터
# 싱글톤 패턴
# 단 하나만 존재해야 하는 것을 보장하는 패턴
# 카페에서 주문받는 pos 시스템이 1대만 있어야 함
# 앱 전체에서 설정값이 1개만 있으면 됨- 다 가져다 씀.
@lru_cache
def get_settings() -> Settings:
    """
    설정 객체를 반환하는 함수

    lru_cache 데코레이터로 캐싱하여, 애플리케이션 전체에서 동일한 설정 객체를 사용하도록 보장
    """
    return Settings()


# 전역 설정 객체, 다른 모듈에서 from app.core import settings로 가져다 씀
settings = get_settings()
