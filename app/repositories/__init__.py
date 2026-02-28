from loguru import logger

from app.core.config import settings
from app.repositories.rag import RAGRepository

__all__ = ["RAGRepository"]


_supabase_client = None


def get_supabase_client():
    """Supabase 클라이언트 반환(싱글톤 패턴)

    init.py 에 있는 이유 -> schedule.py에서 사용하고, fan_letter.py에서도 사용->반복되서 사용"""
    global _supabase_client
    if _supabase_client is None and settings.SUPABASE_URL and settings.SUPABASE_KEY:
        try:
            from supabase import create_client

            _supabase_client = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_KEY
            )
            logger.info("Supabase 클라이언트 초기화 성공")
        except Exception as e:
            logger.warning(f"Supabase 클라이언트 초기화 실패: {e}")
            _supabase_client = None

    return _supabase_client
