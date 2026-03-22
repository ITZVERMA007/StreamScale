from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.core.job_store import job_store
from app.services.minio_client import minio_client,BUCKET_NAME
from worker.tasks.ffmpeg import RESOLUTIONS
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Route and function to get the processed file
@router.get("/download/{task_id}/{res_key}")
async def download_video(job_id:str,res_key:str,db:Session = Depends(get_db)):
    try:
        if res_key not in RESOLUTIONS:
            raise HTTPException(
                status_code=404,
                detail=f"Invalid resolution. Available:{list(RESOLUTIONS.keys())}"
            )
        job = job_store.get_job(db,job_id)
        if not job:
            raise HTTPException(status_code=404,detail="Job not found in the database")
        
        object_name = f"output/{job_id}_{res_key}.mp4"
        try:
            minio_client.stat_object(BUCKET_NAME, object_name)
        except Exception as e:
            logger.error(f"{object_name} not found.. {e}")
            raise HTTPException(status_code=404, detail="File processing or missing")
        
        # Temporary download URL 
        download_url = minio_client.presigned_get_object(
            bucket_name = BUCKET_NAME,
            object_name = object_name,
            expires = timedelta(hours=1)
        )

        return {
            "download_url":download_url,
            "original_filename":job.original_filename,
            "resolution":res_key,
        }
    except HTTPException:raise

    except Exception as e:
        logger.error(f"Download failed for {job_id}:{e}")
        raise HTTPException(status_code=500,detail="Internal Server Error")
