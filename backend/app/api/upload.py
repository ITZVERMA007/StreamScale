from fastapi import APIRouter, UploadFile, File, HTTPException , Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.job_store import job_store
from app.services.minio_service import upload_to_minio
from app.services.queue_service import enqueue_transcode_task
from worker.tasks.ffmpeg import RESOLUTIONS
import uuid
import os


router = APIRouter()

allowed_extensions = {".mp4",".mkv",".mov"}

@router.post("/upload")
async def upload_file(file:UploadFile = File(...),db: Session = Depends(get_db)):
    print("Received file:", file.filename)
    # Basic validation for file is being done at this step
    if not file.filename:
        raise HTTPException(status_code=400,detail="No file uploaded")
    _,ext = os.path.splitext(file.filename)
    if ext.lower() not in allowed_extensions:
        raise HTTPException(status_code=400,detail="Unsupported file type")
    
    # job id for the transcoding task is being generated over here
    job_id = str(uuid.uuid4())
   
    #uploadin the file to minio
    object_name = upload_to_minio(job_id,file)   
    
    resolutions_to_process = list(RESOLUTIONS.keys())
    job_store.create_job(
        db = db,
        job_id = job_id,
        original_filename=file.filename,
        input_object_name=object_name,
        resolutions=resolutions_to_process
    )
    #enqueueing the transcoding task to the worker
    enqueue_transcode_task(job_id,object_name)

    # returning the task id to the user
    return{
        "task_id":job_id,
        "status":"queued",
        "filename":file.filename
    }