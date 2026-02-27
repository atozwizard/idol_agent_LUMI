"""
핵심 설정 및 공통 모듈

이 패키지에서 애플리케이션 전반에 걸쳐 사용되는
설정, 프롬프트, 유틸리티를 관리합니다.

모듈:
    - config.py: 환경변수 설정 관리
"""

# __init__.py : 이 파일이 있어야 해당 디렉토리를 패키지로 인식합니다. 이게 없으면 단순 디렉토리로 취급.
#
from app.core.config import settings

__all__ = ["settings"]

# __all__ : 해당 모듈이나 패키지에서 from xxx import * 할 때 내보낼 이름 목록을 명시적으로 지정하는 qustn
