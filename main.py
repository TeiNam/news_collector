from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import pytz
import uvicorn
from modules.scheduler import setup_schedule, run_collector, get_scheduler_status

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 스케줄러 실행 (초기 수집 없이)
    scheduler_thread = setup_schedule(run_immediately=False)
    yield
    # 애플리케이션 종료 시 스케줄러 정리
    scheduler_thread.stop()

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
async def scheduler_status():
    """스케줄러 상태 확인"""
    return get_scheduler_status()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
