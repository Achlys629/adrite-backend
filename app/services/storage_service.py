import boto3
import uuid
from fastapi import HTTPException, UploadFile
from app.core.config import settings

class StorageService:

    @staticmethod
    def get_s3_client():
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    @staticmethod
    def upload_file(file: UploadFile, folder: str = "general") -> str:
        try:
            s3 = StorageService.get_s3_client()

            # Generate unique filename
            file_extension = file.filename.split(".")[-1]
            unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

            # Upload to S3
            s3.upload_fileobj(
                file.file,
                settings.AWS_BUCKET_NAME,
                unique_filename,
                ExtraArgs={"ContentType": file.content_type}
            )

            # Return public URL
            url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            return url

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    @staticmethod
    def delete_file(file_url: str):
        try:
            s3 = StorageService.get_s3_client()

            # Extract key from URL
            key = file_url.split(
                f"{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/"
            )[-1]

            s3.delete_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=key
            )
            return True

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File delete failed: {str(e)}")

    @staticmethod
    def generate_presigned_url(file_url: str, expiry: int = 3600) -> str:
        try:
            s3 = StorageService.get_s3_client()

            # Extract key from URL
            key = file_url.split(
                f"{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/"
            )[-1]

            url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.AWS_BUCKET_NAME,
                    "Key": key
                },
                ExpiresIn=expiry
            )
            return url

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not generate URL: {str(e)}")