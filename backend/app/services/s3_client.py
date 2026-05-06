import os
import boto3
from botocore.exceptions import ClientError
import json

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "your-access-key")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "your-secret-key")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "streamscalevideos")

s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def init_s3_bucket():
    try:
        # Create bucket if it doesn't exist
        try:
            s3_client.head_bucket(Bucket=BUCKET_NAME)
            print("Bucket already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                if AWS_REGION == "us-east-1":
                    s3_client.create_bucket(Bucket=BUCKET_NAME)
                else:
                    s3_client.create_bucket(
                        Bucket=BUCKET_NAME,
                        CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                    )
                print("Bucket initialized successfully")
            else:
                raise

        # Read and apply CORS configuration if cors.json exists
        cors_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "cors.json")
        if os.path.exists(cors_path):
            with open(cors_path, 'r') as f:
                cors_config = json.load(f)
            s3_client.put_bucket_cors(
                Bucket=BUCKET_NAME,
                CORSConfiguration={'CORSRules': cors_config}
            )
            print("CORS configuration applied successfully")

        # Cleanup Logic for the bucket using S3 Lifecycle
        lifecycle_config = {
            'Rules': [
                {
                    'ID': 'expire_input_videos',
                    'Filter': {'Prefix': 'input/'},
                    'Status': 'Enabled',
                    'Expiration': {'Days': 1}
                },
                {
                    'ID': 'expire_output_videos',
                    'Filter': {'Prefix': 'output/'},
                    'Status': 'Enabled',
                    'Expiration': {'Days': 7}
                }
            ]
        }
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=BUCKET_NAME,
            LifecycleConfiguration=lifecycle_config
        )
        print("S3 lifecycle cleanup rules applied successfully")

    except Exception as e:
        print(f"Failed to initialize the bucket, CORS or lifecycle rules: {e}")

init_s3_bucket()
