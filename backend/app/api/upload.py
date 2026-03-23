from fastapi import APIRouter, HTTPException , Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.core.job_store import job_store
from app.services.minio_service import generate_presigned_upload_url
from app.services.queue_service import enqueue_transcode_task
from worker.tasks.ffmpeg import RESOLUTIONS
import uuid
import os


router = APIRouter()

allowed_extensions = {".mp4",".mkv",".mov"}

class UploadRequest(BaseModel):
    filename:str
@router.post("/upload")
async def upload_file(request:UploadRequest,db: Session = Depends(get_db)):
    # Basic validation for file is being done at this step
    if not request.filename:
        raise HTTPException(status_code=400,detail="No file uploaded")
    _,ext = os.path.splitext(request.filename)
    if ext.lower() not in allowed_extensions:
        raise HTTPException(status_code=400,detail="Unsupported file type")
    
    # job id for the transcoding task is being generated over here
    job_id = str(uuid.uuid4())
   
    
    object_name = f"input/{job_id}_{request.filename}"   

    # Generating the presigned URL for uploading the file
    upload_url = generate_presigned_upload_url(object_name)
    
    if not upload_url:
        raise HTTPException(status_code=500,detail="upload URL not generated")
    
    # Storing the file details in the database
    resolutions_to_process = list(RESOLUTIONS.keys())
    job_store.create_job(
        db = db,
        job_id = job_id,
        original_filename=request.filename,
        input_object_name=object_name,
        resolutions=resolutions_to_process
    )
    #enqueueing the transcoding task to the worker
    enqueue_transcode_task(job_id,object_name)

    # returning the task id to the user
    return{
        "task_id":job_id,
        "status":"queued",
        "filename":request.filename,
        "upload_url":upload_url
    }

@router.post("/process/{job_id}")
async def start_processing(job_id:str,db:Session=Depends(get_db)):

    job = job_store.get_job(db,job_id)
    if not job:
        raise HTTPException(status_code=404,detail="Job not found")
    
    # Task is ready for the celery worker
    enqueue_transcode_task(job_id,job.input_object_name)

    job_store.update_job_status(db,job_id,status="QUEUED")

    return {
        "task_id":job_id,
        "status":"queued",
        "message": "Transcoding successfully queued"
    }
