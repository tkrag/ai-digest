import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import DIGEST_HOUR, DIGEST_MINUTE
from app.digest import run_digest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def _schedule_digest():
    scheduler.add_job(
        run_digest,
        trigger=CronTrigger(hour=DIGEST_HOUR, minute=DIGEST_MINUTE),
        id="daily_digest",
        replace_existing=True,
    )
    logger.info("Digest scheduled for %02d:%02d daily", DIGEST_HOUR, DIGEST_MINUTE)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _schedule_digest()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="AI Digest", lifespan=lifespan)


@app.get("/up")
async def healthcheck():
    return {"status": "ok"}


@app.get("/")
async def index():
    jobs = scheduler.get_jobs()
    next_run = jobs[0].next_run_time.isoformat() if jobs else None
    return {"service": "ai-digest", "next_run": next_run}


@app.post("/run")
async def trigger_digest():
    logger.info("Manual digest trigger via /run")
    result = await run_digest()
    return JSONResponse(result)
