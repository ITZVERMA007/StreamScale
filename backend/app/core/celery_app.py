import os
from celery import Celery

# Celery configuration
redis_host = os.getenv("REDIS_HOST","localhost")
redis_port = os.getenv("REDIS_PORT","6379")

REDIS_URL = f"redis://{redis_host}:{redis_port}/0"

#Instantiate Celery 
celery_app = Celery(
    "streamscale_worker",
    broker = REDIS_URL,
    backend = REDIS_URL,
    include=["worker.tasks.transcode",
             ]
)   


celery_app.conf.update(
    task_serializer = "json",
    accept_content = ["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,

    task_track_started=True,
    task_time_limit=30 * 60,
    worker_Concurrency=4,
)