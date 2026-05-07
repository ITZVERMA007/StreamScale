from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.job_store import job_store
from app.services.s3_client import s3_client, BUCKET_NAME
from worker.tasks.ffmpeg import RESOLUTIONS
import logging
from fastapi.responses import RedirectResponse
from app.services.s3_service import generate_presigned_download_url

logger = logging.getLogger(__name__)
router = APIRouter()

# Route and function to get the processed file
@router.get("/download/{job_id}/{res_key}")
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
            s3_client.head_object(Bucket=BUCKET_NAME, Key=object_name)
        except Exception as e:
            logger.error(f"{object_name} not found.. {e}")
            raise HTTPException(status_code=404, detail="File processing or missing")
        
        # Temporary download URL signed for the external environment
        download_url = generate_presigned_download_url(
            object_name=object_name,
            filename=job.original_filename,
            expiration=3600
        )

        return RedirectResponse(url=download_url)
    except HTTPException:raise

    except Exception as e:
        logger.error(f"Download failed for {job_id}:{e}")
        raise HTTPException(status_code=500,detail="Internal Server Error")
