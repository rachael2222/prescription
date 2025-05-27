import os
from dotenv import load_dotenv

# .env 파일 로드 (있는 경우)
load_dotenv()

# API 설정 - 환경 변수에서 가져오기
API_CONFIG = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "UPSTAGE_API_KEY": os.getenv("UPSTAGE_API_KEY", ""),
    "DUR_API_KEY": os.getenv("DUR_API_KEY", ""),
    "DUR_API_BASE_URL": os.getenv("DUR_API_BASE_URL", "http://apis.data.go.kr/1471000/DURPrdlstInfoService03")
}

def get_api_keys():
    """API 키 반환"""
    return API_CONFIG 