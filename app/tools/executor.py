"""tool 실행 로직

tool executor 클래스가 각 tool의 실행을 담당한다.
tool 이름과 인자를 받아서 적절한 함수를 호출하고 결과를 반환

get_schedule : supabase에서 스케줄 조회
send_fan_letter : supabase에 팬레터 저장
recommend_song : Mock
get_weather : openweathermap 호출
"""

import random
from typing import Any

import httpx
from loguru import logger

from app.core.config import settings
from app.repositories.fan_letter import FanLetterRepository
from app.repositories.schedule import ScheduleRepository

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

# # 🔶 Mock 데이터: 날씨 정보
# MOCK_WEATHER = {
#     "location": "서울",
#     "temperature": 5,
#     "condition": "맑음",
#     "humidity": 45,
#     "wind_speed": 3.2,
# }


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
        user_id: str | None = None,
    ) -> dict[str, Any]:  # dict key 값 str이 들어가고, value는 아무거나 상관없다.
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
                    return await self._send_fan_letter(tool_args, session_id, user_id)

                case "recommend_song":
                    return await self._recommend_song(tool_args)

                case "get_weather":
                    return await self._get_weather(tool_args)

                case _:
                    logger.warning(f"알 수 없는 tool: {tool_name}")
                    return {"success": False, "error": f"알 수 없는 tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool 실행 오류 {e}")
            return {"success": False, "error": str(e)}

    async def _get_schedule(self, args: dict) -> dict:
        """
        supabase에서 스케줄 데이터 조회"""
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        event_type = args.get("event_type", "all")

        logger.info(f"스케줄 조회: {start_date} ~ {end_date}, type={event_type}")

        schedules = await self.schedule_repo.get_schedules(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type if event_type != "all" else None,
        )

        if not schedules:
            return {
                "success": True,
                "data": {
                    "schedules": [],
                    "message": "해당 기간에 예정된 스케줄이 없어요",
                },
            }

        return {
            "success": True,
            "data": {"schedule": schedules, "count": len(schedules)},
        }

    async def _send_fan_letter(
        self, args: dict, session_id: str, user_id: str | None
    ) -> dict:
        """supabase에 팬레터 저장"""

        category = args.get("category", "other")
        message = args.get("message", "")

        logger.info(f"팬레터 저장: category={category}, {message[:50]}...")

        letter_id = await self.fan_letter_repo.create(
            session_id=session_id, user_id=user_id, category=category, message=message
        )

        return {
            "success": True,
            "data": {"letter_id": letter_id, "message": "팬레터가 잘 전달되었어요!"},
        }

    async def _recommend_song(self, args: dict) -> dict:
        """Mock: 하드코딩된 노래 목록에서 추천
        Args:
            args: {"mood": str}
        Returns:
            dict: 추천 노래 정보
        """
        mood = args.get("mood", "happy")
        logger.info(f"노래 추천: mood={mood}")

        songs = LUMI_SONGS.get(mood, LUMI_SONGS["happy"])
        selected = random.choice(songs)

        return {
            "success": True,
            "data": {
                "mood": mood,
                "song": selected["title"],
                "album": selected["album"],
            },
            "mock": True,
        }

    #     async def _get_weather(self, args:dict) -> dict:
    #         """
    #         Mock: 하드코딩된 날씨 정보 반환

    #         Args:
    #             args : {} (파라미터 없음)

    #         Returns:
    #             dict: 날씨 정보
    #         """
    #         logger.info("날씨 조회(Mock)")

    #         return {
    #             "success":True,
    #             "data": MOCK_WEATHER,
    #             "mock":True,

    #         }

    #         # 한국어 날씨 설명과 섭씨온도로 조회
    # url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"

    async def _get_weather(self, args: dict) -> dict:
        """
        위도(lat)와 경도(lon)를 사용하여 현재 날씨 정보 조회
        """
        # args에서 좌표를 가져오고, 없으면 기본값(서울) 사용
        lat = args.get("lat", 37.5665)
        lon = args.get("lon", 126.9780)
        api_key = settings.openweathermap_api_key

        if not api_key:
            logger.error("openweathermap api key가 설정되지 않았습니다.")
            return {"success": False, "message": "API Key missing"}

        # 요청 URL 구성 (f-string 방식)
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"

        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"날씨 조회 시작 (좌표): {lat}, {lon}")
                response = await client.get(url, timeout=5.0)

                # 응답 상태 확인
                response.raise_for_status()
                data = response.json()

                return {
                    "success": True,
                    "data": {
                        "location": data.get("name"),  # 좌표 기준 도시명
                        "weather": data["weather"][0]["description"],  # 한국어 설명
                        "temp": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "feels_like": data["main"]["feels_like"],
                    },
                    "mock": False,
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"날씨 API 오류: {e.response.status_code}")
            return {"success": False, "message": f"API Error: {e.response.status_code}"}
        except Exception as e:
            logger.error(f"날씨 조회 실패: {str(e)}")
            return {"success": False, "message": str(e)}
