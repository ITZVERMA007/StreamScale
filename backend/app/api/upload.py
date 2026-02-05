from fastapi import APIRouter, UploadFile, File,HTTPException
import uuid
import os
from app.core.job_store import create_job

router = APIRouter()

upload_dir = "app/uploads"
allowed_extensions = {".mp4",".mkv",".mov"}

@router.post("/upload")
async def upload_file(file:UploadFile = File(...)):

    # Basic validation for file is being done at this step
    if not file.filename:
        raise HTTPException(status_code=400,detail="No file uploaded")
    _,ext = os.path.splitext(file.filename)
    if ext.lower() not in allowed_extensions:
        raise HTTPException(status_code=400,detail="Unsupported file type")
    
    # task id for the transcoding task is being generated over here
    task_id = str(uuid.uuid4())


    #saving the file locally 
    os.makedirs(upload_dir,exist_ok=True)
    file_location = os.path.join(upload_dir,f"{task_id}_{file.filename}")

    with open(file_location,"wb") as f:
        f.write(await file.read())

    #creatig a job entry in the job_store
    create_job(task_id,file.filename)   

    # returning the task id to the user
    return{
        "task_id":task_id,
        "status":"File uploaded successfully",
        "filename":file.filename
    }