from services.minio_client import minio_client, BUCKET_NAME
from fastapi import UploadFile

def upload_to_minio(task_id:str,file:UploadFile):
    object_name = f"input/{task_id}_{file.filename}"
    minio_client.put_object(
        BUCKET_NAME,
        object_name,
        file.file,
        length=-1,
        part_size=10*1024*1024
    )

    return object_name