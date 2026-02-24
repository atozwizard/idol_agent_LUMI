""" tool 실행 로직

tool executor 클래스가 각 tool의 실행을 담당한다.
tool 이름과 인자를 받아서 적절한 함수를 호출하고 결과를 반환

get_schedule : supabase에서 스케줄 조회
send_fan_letter : supabase에 팬레터 저장
recommend_song : Mock
get_weather : Mock
"""
from typing import Any, Optional

from app.repositories.schedule import ScheduleRepository
from app.repositories.fan_letter import FanLetterRepository
from loguru import logger
from
# 🔶 Mock 데이터: 루미의 노래 목록



LUMI_SONGS = {
    "happy": [
        {"title": "Shine Bright", "album": "First Light"},
        {"title": "Happy Day", "album": "Luminous"},
        {"title": "Dancing Star", "album": "First Light"},
    ],
    "sad": [
        {"title": "Rainy Day", "album": "Moonlight"},
        {"title": "Missing You", "album": "Luminous"},
    ],
    "energetic": [
        {"title": "Power Up", "album": "Energy"},
        {"title": "Let's Go!", "album": "First Light"},
        {"title": "On Fire", "album": "Energy"},
    ],
    "calm": [
        {"title": "Starlight", "album": "Moonlight"},
        {"title": "Peaceful Night", "album": "Moonlight"},
    ],
    "romantic": [
        {"title": "First Love", "album": "Luminous"},
        {"title": "Heart Beat", "album": "Luminous"},
    ],
}

# 🔶 Mock 데이터: 날씨 정보
MOCK_WEATHER = {
    "location": "서울",
    "temperature": 5,
    "condition": "맑음",
    "humidity": 45,
    "wind_speed": 3.2,
}

class ToolExecutor:
    """
    tool 실행기"""
    
    def __init__(self):
        # toolexecutor 초기화 -> schedule repository, fan letter repository 등 필요한 리포지토리 인스턴스 생성
        self.schedule_repo = ScheduleRepository()
        self.fan_letter_repo = FanLetterRepository()
        
    async def execute(
        self,
        tool_name: str,
        tool_args: dict,
        session_id: str,
        user_id: Optional[str] = None
    ) -> dict[str,Any]: #dict key 값 str이 들어가고, value는 아무거나 상관없다.
        
        """tool 실행한다"""
        logger.info(f"[ToolExecutor] Tool 실행: {tool_name}")
        logger.debug(f"인자 : {tool_args}")
        
        # match-case문 (python 3.10+)
        # 패턴 매칭을 위한 구문, switch-case
        # 각 case 는 tool)name 값과 매칭되어 해당 매서드를 호출
        
        try:
            match tool_name:
                case "get_schedule":
                    return await self._get_schedule(tool_args)
                case "send_fan_letter":
                    return await self._send_fan_letter(
                        tool_args,session_id,user_id
                    )
                
                case "recommend_song":
                    return await self._recommend_song(tool_args)
                
                case "get_weather":
                    return await self._get_weather(tool_args)
                
                case _:
                    logger.warning(f"알 수 없는 tool: {tool_name}")
                    return {
                        "success" : False,
                        "error": f"알 수 없는 tool: {tool_name}"
                    }    
        except Exception as e:
            logger.error(f"Tool 실행 오류 {e}")
            return {
                "success" : False,
                "error" : str(e)
            }
            
    async def _get_schedule(self, args:dict) -> dict:
        """
        supabase에서 스케줄 데이터 조회"""
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        event_type = args.get("event_typs", "all")
        
        logger.info(f"스케줄 조회: {start_date} ~ {end_date}, type={event_type}")
        
        self.schedule_repo.get_schedules(
            start_date = start_date,
            end_date=end_date,
            event_type=event_type if event_type != "all" else None
        )
        
        if not schedules:
            return{
                "success": True,
                "data": {
                    "schedules": [],
                    "message": "해당 기간에 예정된 스케줄이 없어요"
                }
            }
        
        return {
            "success": True,
            "data": {
                "schedule": schedules,
                "count": len(schedules)                
            }
        }
        
        