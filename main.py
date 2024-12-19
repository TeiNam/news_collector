from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import schedule
import time
import threading
import logging
from datetime import datetime
import pytz
from typing import Dict
import uvicorn
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

# 스케줄러 상태를 저장할 전역 변수
scheduler_thread = None
is_scheduler_running = False


def run_collector() -> Dict:
    """뉴스 수집 실행"""
    try:
        current_datetime = datetime.now(KST)
        current_date = current_datetime.strftime('%Y%m%d')

        logger.info(f"뉴스 수집 시작: {current_date} {current_datetime.strftime('%H:%M')} KST")
        results = collect_daily_news(current_date)

        total_articles = sum(len(df) for df in results.values())
        logger.info(f"뉴스 수집 완료: 총 {total_articles}개 기사 수집")

        return {"status": "success", "total_articles": total_articles}
    except Exception as e:
        error_msg = f"뉴스 수집 중 오류 발생: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}


def run_scheduler():
    """스케줄러 실행"""
    global is_scheduler_running

    # 스케줄 설정
    schedule.every().day.at("08:00").do(run_collector)
    schedule.every().day.at("11:00").do(run_collector)
    schedule.every().day.at("14:30").do(run_collector)

    logger.info("스케줄러 시작됨 (KST 기준)")
    logger.info("실행 시간: 매일 08:00, 11:00, 14:30")

    while is_scheduler_running:
        schedule.run_pending()
        time.sleep(60)


def start_scheduler_thread():
    """스케줄러 스레드 시작"""
    global scheduler_thread, is_scheduler_running

    if not is_scheduler_running:
        is_scheduler_running = True
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.start()
        return True
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행
    start_scheduler_thread()
    yield
    # 애플리케이션 종료 시 실행
    global is_scheduler_running
    is_scheduler_running = False
    if scheduler_thread:
        scheduler_thread.join()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "News Collector API", "status": "running"}


@app.post("/collector/run")
async def run_collector_manually(background_tasks: BackgroundTasks):
    """수동으로 뉴스 수집 실행"""
    background_tasks.add_task(run_collector)
    return JSONResponse(
        content={
            "message": "뉴스 수집이 백그라운드에서 시작되었습니다.",
            "status": "started"
        }
    )


@app.get("/scheduler/status")
async def get_scheduler_status():
    """스케줄러 상태 확인"""
    return {
        "is_running": is_scheduler_running,
        "next_runs": [
            {
                "job": job.job_func.__name__,
                "next_run": str(job.next_run)
            }
            for job in schedule.get_jobs()
        ]
    }


@app.post("/scheduler/start")
async def start_scheduler():
    """스케줄러 시작"""
    if start_scheduler_thread():
        return {"message": "스케줄러가 시작되었습니다.", "status": "started"}
    return {"message": "스케줄러가 이미 실행 중입니다.", "status": "already_running"}


@app.post("/scheduler/stop")
async def stop_scheduler():
    """스케줄러 중지"""
    global is_scheduler_running
    if is_scheduler_running:
        is_scheduler_running = False
        if scheduler_thread:
            scheduler_thread.join()
        return {"message": "스케줄러가 중지되었습니다.", "status": "stopped"}
    return {"message": "스케줄러가 이미 중지된 상태입니다.", "status": "already_stopped"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )