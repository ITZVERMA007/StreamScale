from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from app.db.database import get_db
from app.core.job_store import job_store
from app.services.s3_service import generate_presigned_upload_url
from app.services.queue_service import enqueue_transcode_task
from worker.tasks.ffmpeg import RESOLUTIONS
from app.core.limiter import limiter
import uuid
import os


router = APIRouter()

allowed_extensions = {".mp4",".mkv",".mov"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB limit

class UploadRequest(BaseModel):
    filename:str
    filesize:int

    @validator('filesize')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError("File size must be positive")
        if v > MAX_FILE_SIZE:
            raise ValueError(f"File exceeds maximum size of {MAX_FILE_SIZE / (1024**2):.1f}MB")
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or len(v) > 255:
            raise ValueError("Invalid filename")
        # Prevent path traversal
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError("Invalid characters in filename")
        return v
        
@router.post("/upload")
@limiter.limit("10/minute")
async def upload_file(request: Request, upload_request: UploadRequest, db: Session = Depends(get_db)):
    # Basic validation for file is being done at this step
    if not upload_request.filename:
        raise HTTPException(status_code=400,detail="No file uploaded")
    _,ext = os.path.splitext(upload_request.filename)
    if ext.lower() not in allowed_extensions:
        raise HTTPException(status_code=400,detail="Unsupported file type")
    
    # job id for the transcoding task is being generated over here
    job_id = str(uuid.uuid4())
   
    
    object_name = f"input/{job_id}_{upload_request.filename}"   

    # Generating the presigned URL for uploading the file
    upload_url = generate_presigned_upload_url(object_name)
    
    if not upload_url:
        raise HTTPException(status_code=500,detail="upload URL not generated")
    
    # Storing the file details in the database
    resolutions_to_process = list(RESOLUTIONS.keys())
    job_store.create_job(
        db = db,
        job_id = job_id,
        original_filename=upload_request.filename,
        input_object_name=object_name,
        resolutions=resolutions_to_process
    )

    # returning the task id to the user
    return{
        "task_id":job_id,
        "status":"queued",
        "filename":upload_request.filename,
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
