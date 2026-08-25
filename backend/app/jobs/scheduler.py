from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.db.session import SessionLocal
from app.jobs.scoring_cycle import run_full_scoring_cycle

SCHEDULER_TIMEZONE = "Asia/Karachi"
MORNING_RUN_HOUR = 6
MIDDAY_RUN_HOUR = 12


def _run_scheduled_cycle() -> None:
    db = SessionLocal()
    try:
        run_full_scoring_cycle(db, get_settings())
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=SCHEDULER_TIMEZONE)
    scheduler.add_job(_run_scheduled_cycle, CronTrigger(hour=MORNING_RUN_HOUR, minute=0))
    scheduler.add_job(_run_scheduled_cycle, CronTrigger(hour=MIDDAY_RUN_HOUR, minute=0))
    scheduler.start()
    return scheduler
