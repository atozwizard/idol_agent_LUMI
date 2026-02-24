"""
채팅 api 요청 /응답 스키마
"""

from dataclasses import Field

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class ChatRequest(BaseModel):
    """ 
    채팅 요청 스키마
    
    클라이언트에서 서버로 보내는 채팅 메시지 형식
    
    Attributes:
        message: 사용자 메시지 내용
        sessiion_id: 세션 식별자
        user_id: 사용자 식별자(선택-optional)
    
    """
    # Field : 필드에 대한 추가적인 정보(메타데이터)와 검증 조건 설정
    message: str = Field(
        ..., #필수 필드임을 나타냄
        min_length=1, # 최소 길이 1
        max_length=2000, # 최대 길이 2000
        description="사용자 메시지 내용", # 필드 설명
        example=["오늘 방송 언제야", "노래 추천해줘"], # 예시값
    )
    
    session_id: str = Field(
        ..., #필수 필드임을 나타냄
        min_length=1, # 최소 길이 1
        max_length=100, # 최대 길이 100
        description="세션 식별자", # 필드 설명
        example=["user123", "session-abc-123"], # 예시값
    )
    
    user_id: Optional[str] = Field(
        default=None, # 선택적 필드임을 나타냄
        max_length=100, # 최대 길이 100
        description="사용자 식별자 (선택)", # 필드 설명
        example=["user123", "user-abc-123"], # 예시값
    )
    
    
class ChatResponse(BaseModel):
    """ 
    채팅 응답 스키마
    
    서버에서 클라이언트로 보내는 채팅 메시지 형식
    
    Attributes:
        message: 루미의 응답 메시지
        tool_used: 사용된 tool 이름
        cached: 캐시된 응답 여부
        timestamp: 응답 생성 시간
    
    Example:
        >>> response = ChatResponse(
        ...     message="금요일에 뮤직뱅크 나와!",
        ...     tool_used="get_schedule",
        ... )
    """
    # Field : 필드에 대한 추가적인 정보(메타데이터)와 검증 조건 설정
    message: str = Field(
        ..., #필수 필드임을 나타냄
        description="루미의 응답 메시지", # 필드 설명
    
    )
    
    tool_used: Optional[str] = Field(
        default=None, # 선택적 필드임을 나타냄
        description="사용된 tool 이름", # 필드 설명
        examples = ["get_schedule", None] # 예시값
    
    )
    
    cached: bool = Field(
        default=False, 
        description="캐시된 응답 여부", # 필드 설명
    
    )
    # default vs default_factory
    # default : 모든 인스턴스가 같은 값을 공유
    # default_factory : 인스턴스 생성할 때마다 함수를 호출해서 새로운 값을 생성
    # 비유(생일케이크)
        # default = cacke : 모든 손님이 같은 케이크 1개 를 나눠 먹음
        # default_factory = make_cake : 손님이 올 떄마다 새로운 케이크 1개씩 만들어서 줌
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="응답 생성 시간(UTC)" # 필드 설명 UTC-영국시간-서버에서는 주로 UTC 사용
    )
    