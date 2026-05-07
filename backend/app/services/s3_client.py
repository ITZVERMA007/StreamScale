import os
import boto3
from botocore.exceptions import ClientError
import json
import logging

logger = logging.getLogger(__name__)

# Load AWS configuration from environment
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "streamscalevideos")

# Validate AWS credentials are present
if not AWS_ACCESS_KEY_ID or AWS_ACCESS_KEY_ID == "your-access-key":
    logger.warning("AWS_ACCESS_KEY_ID not set or using placeholder value")
if not AWS_SECRET_ACCESS_KEY or AWS_SECRET_ACCESS_KEY == "your-secret-key":
    logger.warning("AWS_SECRET_ACCESS_KEY not set or using placeholder value")

# Initialize S3 client lazily to allow app to start even if AWS is unavailable
_s3_client = None

def get_s3_client():
    """Get or create S3 client singleton."""
    global _s3_client
    if _s3_client is None:
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            raise ValueError("AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars.")
        _s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    return _s3_client

# Backward compatibility: expose s3_client through property
class S3ClientProxy:
    """Proxy that lazily initializes S3 client on first access."""
    def __getattr__(self, name):
        client = get_s3_client()
        return getattr(client, name)

s3_client = S3ClientProxy()

def init_s3_bucket():
    try:
        client = get_s3_client()
        
        # Create bucket if it doesn't exist
        try:
            client.head_bucket(Bucket=BUCKET_NAME)
            logger.info(f"S3 bucket '{BUCKET_NAME}' already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                if AWS_REGION == "us-east-1":
                    client.create_bucket(Bucket=BUCKET_NAME)
                else:
                    client.create_bucket(
                        Bucket=BUCKET_NAME,
                        CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                    )
                logger.info(f"S3 bucket '{BUCKET_NAME}' created successfully")
            else:
                raise

        # Note: CORS should be configured via AWS Console or CLI for production
        # This automatic setup is for development convenience only
        cors_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "cors.json")
        if os.path.exists(cors_path):
            try:
                with open(cors_path, 'r') as f:
                    cors_config = json.load(f)
                client.put_bucket_cors(
                    Bucket=BUCKET_NAME,
                    CORSConfiguration={'CORSRules': cors_config}
                )
                logger.info("S3 CORS configuration applied")
            except Exception as e:
                logger.warning(f"Could not apply CORS configuration: {e}")

        # Setup lifecycle rules for automatic cleanup
        try:
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
            client.put_bucket_lifecycle_configuration(
                Bucket=BUCKET_NAME,
                LifecycleConfiguration=lifecycle_config
            )
            logger.info("S3 lifecycle rules configured")
        except Exception as e:
            logger.warning(f"Could not configure lifecycle rules: {e}")

    except Exception as e:
        logger.error(f"S3 bucket initialization failed: {e}")
        # Don't raise - allow app to start even if S3 setup fails
        # API endpoints will fail gracefully when S3 operations are attempted

# Initialize on module load but don't block startup
try:
    init_s3_bucket()
except Exception:
    pass  # Logged inside function
