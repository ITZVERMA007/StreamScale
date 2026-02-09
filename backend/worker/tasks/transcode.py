from app.core.celery_app import celery_app
import time
import os

@celery_app.task(bind=True)
def transcode_video(self,job_id:str,file_path:str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    for i in range(1,11):
        time.sleep(1)
        self.update_state(
            state="progress",
            meta={
                "progress":i*10,"file_size":file_size
                }
            )
    return {
        "status":"Completed",
        "job_id":job_id
    }