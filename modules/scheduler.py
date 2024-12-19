import schedule
import time
import logging
from datetime import datetime
import pytz
from utils.naver_search_api_collector import collect_daily_news

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def run_collector():
    """스케줄된 시간에 뉴스 수집기를 실행하는 함수"""
    try:
        current_datetime = datetime.now(KST)
        current_date = current_datetime.strftime('%Y%m%d')

        logger.info(f"뉴스 수집 시작: {current_date} {current_datetime.strftime('%H:%M')} KST")
        results = collect_daily_news(current_date)

        total_articles = sum(len(df) for df in results.values())
        logger.info(f"뉴스 수집 완료: 총 {total_articles}개 기사 수집")

    except Exception as e:
        logger.error(f"뉴스 수집 중 오류 발생: {str(e)}", exc_info=True)

def setup_schedule():
    """스케줄러 설정 (한국 시간 기준)"""
    # 아침 8시
    schedule.every().day.at("08:00").do(run_collector)
    # 오전 11시
    schedule.every().day.at("12:00").do(run_collector)
    # 오후 2시 30분
    schedule.every().day.at("14:30").do(run_collector)
    # 오후 8시 00분
    schedule.every().day.at("20:00").do(run_collector)

    logger.info("뉴스 수집 스케줄러 시작됨 (KST 기준)")
    logger.info("실행 시간: 매일 08:00, 11:00, 14:30, 20:00")

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크
        except Exception as e:
            logger.error(f"스케줄러 오류: {str(e)}", exc_info=True)
            time.sleep(300)  # 오류 발생 시 5분 대기 후 재시도

if __name__ == "__main__":
    setup_schedule()