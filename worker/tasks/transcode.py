import time
from backend.app.core.celery_app import celery_app

@celery_app.task(bind=True)
def dummy_transcode(self,job_id:str):
    for i in range(1,6):
        time.sleep(1)
        self.update_state(
            state="PROGRESS",
            meta={"progress":i*20}
        )
    
    return {
        "status":"Completed",
        "job_id":job_id
    }