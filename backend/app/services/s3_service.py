from app.services.s3_client import s3_client, BUCKET_NAME
from botocore.exceptions import ClientError

def generate_presigned_upload_url(object_name: str, expiration=3600):
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
        print(f"Generated URL: {response}")
        return response
    except ClientError as e:
        print(f"Error generating pre-signed URL: {e}")
        return None

def generate_presigned_download_url(object_name: str, filename: str, expiration=3600):
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': object_name,
                                                            'ResponseContentDisposition': f'attachment; filename="{filename}"'},
                                                    ExpiresIn=expiration)
        return response
    except ClientError as e:
        print(f"Error generating pre-signed URL: {e}")
        return None
