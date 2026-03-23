from datetime import timedelta
from app.services.minio_client import minio_client,BUCKET_NAME

# Generates a temporary URL for the frontend so that it directly uploads the file in minio
def generate_presigned_upload_url(object_name:str):
    try:
        upload_url = minio_client.presigned_put_object(
            bucket_name = BUCKET_NAME,
            object_name = object_name,
            expires = timedelta(hours=2)
        )

        # We are converting the URL so that the browser knows where it has to send the file
        upload_url = upload_url.replace("minio:9000","localhost:9000")
        return upload_url
    
    except Exception as e:
        print(f"Error generating pre-signed URL:{e}")
        return None