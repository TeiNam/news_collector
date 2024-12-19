import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Naver API 설정
NAVER_API_CONFIG = {
    'client_id': os.getenv('NAVER_CLIENT_ID'),
    'client_secret': os.getenv('NAVER_CLIENT_SECRET'),
    'base_url': "https://openapi.naver.com/v1/search/news"
}

# 필수 API 키 확인
if not NAVER_API_CONFIG['client_id'] or not NAVER_API_CONFIG['client_secret']:
    raise ValueError("Missing NAVER_CLIENT_ID or NAVER_CLIENT_SECRET in environment variables")

# 검색 설정
SECTIONS = {
    "주식": [
        "코스피 코스닥",
        "증권 주식",
        "금리정책",
        "반도체 SK하이닉스",
        "기업공시",
        "지분매각",
        "외인 기관",
        "환률",
        "S&P"
    ]
}

# 제외할 키워드
EXCLUDE_KEYWORDS = ["포토", "사진", "그래픽", "영상"]

# API 요청 관련 설정
API_REQUEST_CONFIG = {
    'max_retries': 3,
    'retry_delay': 5,  # 초
    'items_per_request': 100,
    'max_items': 1000
}