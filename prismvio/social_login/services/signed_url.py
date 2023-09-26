import datetime

from django.conf import settings
from google import auth
from google.auth.transport import requests
from google.cloud import storage
from loguru import logger

from prismvio.social_login.exceptions import GCSUploadSignedUrlException

try:
    credentials, project_id = auth.default()
    r = requests.Request()
except Exception:
    pass


class GCSService:
    def delete_blobs(self, blobs: list):
        """Deletes google storage files

        Args:
            blobs: List of files need delete

        """
        client = storage.Client()
        for blob in blobs:
            try:
                name = blob.get("name")
                is_private = blob.get("is_private", False)
                if is_private:
                    bucket = client.get_bucket(settings.GCS_PRIVATE_BUCKET_NAME)
                else:
                    bucket = client.get_bucket(settings.GCS_PUBLIC_BUCKET_NAME)
                blob = bucket.blob(name)
                blob.delete()
            except Exception as error:
                logger.exception(error)


class GCSSignedUrlService(GCSService):
    def __init__(self, bucket_name: str, blob_name: str, file_type: str):
        self.bucket_name = bucket_name
        self.blob_name = blob_name
        self.file_type = file_type

    def generate_download_signed_url_v4(self, seconds: int = 604800):
        """Generates a v4 signed URL for downloading a blob.

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        """
        credentials.refresh(r)
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(self.blob_name)
        return blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(seconds=seconds),
            method="GET",
            service_account_email=settings.GCS_SERVICE_ACCOUNT_EMAIL,
            access_token=credentials.token,
        )

    def generate_upload_signed_url_v4(self, seconds: int = 604800):
        """Generates a v4 signed URL for uploading a blob using HTTP PUT.

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        """
        try:
            credentials.refresh(r)
            storage_client = storage.Client(credentials=credentials)
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.blob_name)
            return blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(seconds=seconds),
                method="PUT",
                content_type=self.file_type,
                service_account_email=settings.GCS_SERVICE_ACCOUNT_EMAIL,
                access_token=credentials.token,
            )
        except Exception as error:
            logger.exception(error)
            raise GCSUploadSignedUrlException()
