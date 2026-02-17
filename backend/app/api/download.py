from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from app.core.job_store import get_job
from worker.tasks.ffmpeg import RESOLUTIONS
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

processed_dir = "/data/processed"

# Route and function to get the processed file
@router.get("/download/{task_id}/{res_key}")
async def download_video(task_id:str,res_key:str):
    if res_key not in RESOLUTIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid resolution. Available:{list(RESOLUTIONS.keys())}"
        )
    job = get_job(task_id)
    if not job:
        raise HTTPException(status_code=404,detail="Task not found")
    
    # Making the file path to access the file
    file_name = f"{task_id}_{res_key}.mp4"
    file_path = os.path.join(processed_dir,file_name)

    # Checking if the file exists or not
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404,detail="File not found on the disk")
    
    original_file_name = job.get("filename","video/mp4")
    
    base_name = os.path.splitext(original_file_name)[0]
    download_name = f"{base_name}_{res_key}.mp4"
    # Returning the file as 
    return FileResponse(
        path=file_path,
        media_type='video/mp4',
        filename=f"transcoded_{download_name}"
    )


