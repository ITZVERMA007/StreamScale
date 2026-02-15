from app.core.celery_app import celery_app
import time
import os
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def transcode_video(self,job_id:str,file_path:str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    logger.info(f"Starting transcoding for job_id: {job_id}")
    for i in range(1,11):
        time.sleep(1)
        self.update_state(
            state="progress",
            meta={
                "progress":i*10,"file_size":file_size
                }
            )
        logger.info(f"Job {job_id} progress: {i*10}%")
    return {
        "status":"Completed",
        "job_id":job_id
    }