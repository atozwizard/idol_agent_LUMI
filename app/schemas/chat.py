"""
채팅 api 요청 /응답 스키마
"""

from dataclasses import Field

from pydantic import BaseModel, Field
from typing import Any, Literal, Optional
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
    
    
    # 3강 : SreamEvent : SSE 스트리밍 이벤트 스키마
    # StreamEventType : SSE 프로토콜에서 이벤트 종류를 구반하기 위한 타입(thinking, tool, token, response, error, done)
        # thinking : 노드 진행 상황(루미 생각 중...)
        # tool : Tool 실행결과
        # token : LLm 토큰 스트리밍(글자 단위 출력)
        # response : 최종 응답 완료
        # error : 에러 발생
        # done : 스트리밍 종료 신호


# Literal : 특정 값만 허용하는 타입을 정의        
StreamEventType = Literal["thinking", "tool", "token", "response", "error", "done"]

class StreamEvent(BaseModel):
    """SSE 스트리밍 이벤트 스키마
    Server-Sent Events로 전송되는 이벤트 형식입니다.
    각 이벤트 타입에 따라 다른 필드가 채워집니다.
    
    Attributes:
        type: 이벤트 타입
            - thinking: 노드 실행 시작 (어떤 노드가 실행 중인지)
            - tool: Tool 실행 결과
            - token: LLM 토큰 스트리밍
            - response: 최종 응답 완료
            - error: 에러 발생
            - done: 스트리밍 종료
        node: 현재 실행 중인 노드 이름 (thinking, tool 이벤트)
        content: 텍스트 내용 (token, response 이벤트)
        tool_name: 실행된 Tool 이름 (tool 이벤트)
        tool_result: Tool 실행 결과 (tool 이벤트)
        error: 에러 메시지 (error 이벤트)

    Example:
        >>> # 노드 실행 시작 이벤트
        >>> event = StreamEvent(type="thinking", node="router")

        >>> # Tool 실행 결과 이벤트
        >>> event = StreamEvent(
        ...     type="tool",
        ...     node="tool",
        ...     tool_name="get_schedule",
        ...     tool_result={"schedules": [...]}
        ... )

        >>> # 토큰 스트리밍 이벤트
        >>> event = StreamEvent(type="token", content="안녕")

        >>> # 최종 응답 이벤트
        >>> event = StreamEvent(
        ...     type="response",
        ...     content="금요일에 뮤직뱅크 나와!",
        ...     tool_used="get_schedule"
        ... )
    """
    
    type: StreamEventType = Field(
        ...,
        description="이벤트 타입"
    )
    
    # 특정 이벤트는 node 정보가 필수적, thinking
        # done 이벤트는 node가 필수적이지 않음. 완료되었다.
        # 이렇게 여러 정보를 같이 저장할 떄는 선택적
    node: Optional[str] = Field(
        default=None,
        description="현재 실행 중인 노드 이름",
        examples=["router", "rag", "tool", "response"]
    )
    
    content : Optional[str] = Field(
        default=None,
        description="텍스트 내용(토큰 또는 최종 응답)"
    )
    
    tool_name: Optional[str] = Field(
        default=None,
        description="실행된 Tool 이름",
        examples=["get_schedule", "recommend_song"],
    )

    tool_result: Optional[str] = Field(
        default=None,
        description="Tool 실행 결과",
    )

    tool_used: Optional[str] = Field(
        default=None,
        description="최종 응답에서 사용된 Tool",
    )

    error: Optional[str] = Field(
        default=None,
        description="에러 메시지",
    )

    def to_sse(self) -> str:
        
        """
        SSE 형식 문자열로 변환
        
        """
        # python 표준 json 라이브러리 -> 속도가 더 빠른 라이브러리 orjson
        
        import orjson
        # data = {}
        # for k, v in self.model_dump().items():
        #     # sse 형태로 데이터를 변환, 값이 None 인 것은 제외, None 이 아닌 것만 데이터를 추가
        #     if v is not None:
        #         data[k] = v
        # 위 형태를 for문이 아니라 dict comprehension
        data = {k: v for k,v in self.model_dump().items() if v is not None}
        # dumps_data = orjson.dumps(data)
        # utf_data = orjson.dumps(data).decode("utf-8")
        # print(dumps_data,utf_data)
        json_str = orjson.dumps(data).decode("utf-8")
        # dumps가 bytes 를 반환해서 decode를 사용해서 변환(문자열) -> SSE로 보내려면 문자열이 필요하기 때문
        # return data
        
        return f"data: {json_str}\n\n"
        
event = StreamEvent(type="thinking", node="router")
print("model_dump", event.model_dump())

print("to_see", event.to_sse()) 