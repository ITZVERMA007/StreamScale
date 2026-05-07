import os
from celery import Celery

# Celery configuration - uses REDIS_URL from environment (Railway/Redis Cloud)
# Falls back to localhost for local development
REDIS_URL = os.getenv("REDIS_URL") or os.getenv("CELERY_BROKER_URL")

if not REDIS_URL:
    # Local development fallback
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    REDIS_URL = f"redis://{redis_host}:{redis_port}/0"

# Instantiate Celery 
celery_app = Celery(
    "streamscale_worker",
    broker = REDIS_URL,
    backend = REDIS_URL,
    include=[
        "worker.tasks.transcode",
        "worker.tasks.cleanup",
    ]
)

# Celery Beat Schedule - Periodic cleanup tasks
celery_app.conf.beat_schedule = {
    # Run database cleanup once per day at 2 AM UTC
    "cleanup-old-jobs-daily": {
        "task": "worker.tasks.cleanup.cleanup_old_jobs",
        "schedule": 86400.0,  # 24 hours in seconds
    },
    # Run temp file cleanup once per day at 3 AM UTC
    "cleanup-temp-files-daily": {
        "task": "worker.tasks.cleanup.cleanup_orphaned_temp_files",
        "schedule": 86400.0,  # 24 hours in seconds
    },
}

celery_app.conf.update(
    task_serializer = "json",
    accept_content = ["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,

    task_track_started=True,
    task_time_limit=30 * 60,
    worker_concurrency=4,
)