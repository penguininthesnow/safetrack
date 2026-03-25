import boto3
import os 
import mimetypes
from uuid import uuid4
from fastapi import UploadFile
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()


s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

def upload_to_s3(file: UploadFile):
    if not file:
        return None
    
    bucket_name = os.getenv("S3_BUCKET_NAME")
    cloudfront_url = os.getenv("CLOUDFRONT_URL")

    if not bucket_name:
        raise Exception("S3_BUCKET_NAME not set")
    
    if not cloudfront_url:
        raise Exception("CLOUDFRONT_URL not set")

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid4()}.{file_extension}"

    s3_client.upload_fileobj(
        file.file,
        bucket_name,
        unique_filename,
        ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
    )

    return f"{cloudfront_url}/{unique_filename}"

def upload_local_file_to_s3(local_path: str, s3_key: str, content_type: str = None):
    """
    上傳本機檔案到 S3，並回傳 CloudFront URL
    例如：
    local_path = "frontend/videos/step1.mp4"
    s3_key = "videos/step1.mp4"
    """
    bucket_name = os.getenv("S3_BUCKET_NAME")
    cloudfront_url = os.getenv("CLOUDFRONT_URL")

    if not bucket_name:
        raise Exception("S3_BUCKET_NAME not set")

    if not cloudfront_url:
        raise Exception("CLOUDFRONT_URL not set")

    if not os.path.exists(local_path):
        raise FileNotFoundError(f"找不到檔案: {local_path}")

    if content_type is None:
        guessed_type, _ = mimetypes.guess_type(local_path)
        content_type = guessed_type or "application/octet-stream"

    s3_client.upload_file(
        local_path,
        bucket_name,
        s3_key,
        ExtraArgs={"ContentType": content_type},
    )

    return f"{cloudfront_url}/{s3_key}"