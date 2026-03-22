from fastapi import UploadFile
import os
from app.services.minio_client import minio_client,BUCKET_NAME

def upload_to_minio(job_id:str,file:UploadFile)->str:
    object_name = f"input/{job_id}_{file.filename}"
    
    minio_client.put_object(
        BUCKET_NAME,
        object_name,
        file.file,
        part_size=10*1024*1024
    )

    return object_name