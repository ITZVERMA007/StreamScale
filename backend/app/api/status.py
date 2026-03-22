from fastapi import APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from app.core.celery_app import celery_app
from app.services.minio_client import minio_client,BUCKET_NAME
from datetime import timedelta
from app.db.database import get_db
from app.core.job_store import job_store
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Endpoint to check the status of the desired task with the help of task id which is being generated at the time of file upload
@router.get("/tasks/{task_id}/status")
def get_status(task_id:str,db: Session = Depends(get_db)):

    try:
        job = job_store.get_job(db,task_id)
        if not job:
            raise HTTPException(status_code=404,detail="Job not found in the database")
        # This is checking for the status of the task by connecting the backend to the redis
        result  = AsyncResult(task_id,app=celery_app)

        if result.state == "PROGRESS":
            progress_data = result.info if isinstance(result.info,dict) else {}
            tasks = progress_data.get("tasks",{})

            # Gets the percent complete for the keys present in the RESOLUTIONS which are the original resolutions
            active_progress_values = [ data.get("progress",0) for data in tasks.values()]
            overall_progress = sum(active_progress_values)/ len(active_progress_values) if active_progress_values else 0

            return{
                "task_id":task_id,
                "state":"Processing",
                "overall_progress":int(overall_progress),
                "details":tasks,
                "filename":job.original_filename
            }

        elif job.status == "SUCCESS":
            downloads = {}
            for res in job.resolutions:
                object_name = f"output/{task_id}_{res}.mp4"
                try:
                    # presigned URL is used to create a temporary URL for the output file stored in minio to download the file
                    presigned_url = minio_client.presigned_get_object(
                        BUCKET_NAME,
                        object_name,
                        expires=timedelta(hours=1)
                        )
                    downloads[res] = presigned_url
                except Exception as e:
                    logger.error(f"Failed to generate URL for {object_name}:{e}")

            return {
                "task_id":task_id,
                "state":"COMPLETED",
                "overall_progress":100,
                "download_urls":downloads,
                "filename":job.original_filename
            }
        elif job.status == "FAILURE":
            return {
                "task_id":task_id,
                "state":"Failed",
                "overall_progress":0,
                "error":"Processing failed, please try again.",
            }

        return {
            "task_id":task_id,
            "state":"Queued",
            "overall_progress":0,
            "filename":job.original_filename
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"api error:{e}")
        raise HTTPException(status_code=500,detail="Internal Server Error")