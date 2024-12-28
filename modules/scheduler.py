import schedule
import time
import logging
import threading
from datetime import datetime
import pytz
from utils.naver_search_api_collector import collect_daily_news

logger = logging.getLogger(__name__)

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')


class SchedulerThread(threading.Thread):
    def __init__(self, run_immediately=False):
        super().__init__()
        self.is_running = False
        self.schedule_times = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
        self.run_immediately = run_immediately

    def run(self):
        self.is_running = True

        # 스케줄 등록
        for time_str in self.schedule_times:
            schedule.every().day.at(time_str).do(run_collector)
            logger.info(f"스케줄 등록: {time_str} KST")

        logger.info("뉴스 수집 스케줄러 시작됨")
        logger.info(f"실행 시간: 매일 {', '.join(self.schedule_times)} KST")

        # 옵션이 설정된 경우에만 즉시 실행
        if self.run_immediately:
            logger.info("초기 수집 시작")
            run_collector()

        while self.is_running:
            schedule.run_pending()
            time.sleep(60)

    def stop(self):
        self.is_running = False


def run_collector():
    """뉴스 수집 실행"""
    try:
        current_datetime = datetime.now(KST)
        current_date = current_datetime.strftime('%Y%m%d')

        logger.info(f"뉴스 수집 시작: {current_date} {current_datetime.strftime('%H:%M')} KST")
        results = collect_daily_news(current_date)

        if results:
            total_articles = sum(len(df) for df in results.values())
            logger.info(f"뉴스 수집 완료: 총 {total_articles}개 기사 수집")
            return {"status": "success", "total_articles": total_articles}
        else:
            logger.warning("수집된 기사가 없습니다.")
            return {"status": "warning", "message": "수집된 기사가 없습니다."}

    except Exception as e:
        error_msg = f"뉴스 수집 중 오류 발생: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}


def setup_schedule(run_immediately=False):
    """스케줄러 설정 및 시작"""
    scheduler_thread = SchedulerThread(run_immediately=run_immediately)
    scheduler_thread.start()
    return scheduler_thread


def get_scheduler_status():
    """스케줄러 상태 조회"""
    return {
        "next_runs": [
            {
                "job": job.job_func.__name__,
                "next_run": str(job.next_run)
            }
            for job in schedule.get_jobs()
        ]
    }