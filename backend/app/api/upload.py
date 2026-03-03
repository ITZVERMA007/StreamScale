from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.job_store import upload_to_minio
from app.services.queue_service import enqueue_transcode_task
import uuid
import os


router = APIRouter()

allowed_extensions = {".mp4",".mkv",".mov"}

@router.post("/upload")
async def upload_file(file:UploadFile = File(...)):
    print("Received file:", file.filename)
    # Basic validation for file is being done at this step
    if not file.filename:
        raise HTTPException(status_code=400,detail="No file uploaded")
    _,ext = os.path.splitext(file.filename)
    if ext.lower() not in allowed_extensions:
        raise HTTPException(status_code=400,detail="Unsupported file type")
    
    # task id for the transcoding task is being generated over here
    task_id = str(uuid.uuid4())
   
    #uploadin the file to minio
    object_name = upload_to_minio(task_id,file)   

    #enqueueing the transcoding task to the worker
    enqueue_transcode_task(task_id,object_name)

    # returning the task id to the user
    return{
        "task_id":task_id,
        "status":"queued",
        "filename":file.filename
    }