"""
Google Cloud Platform service for GCS operations
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

from google.cloud import storage
from google.oauth2 import service_account

from ..config import settings

logger = logging.getLogger(__name__)


class GCPService:
    """Service for Google Cloud Platform operations"""

    def __init__(self):
        self.client = None
        self.project_id = settings.api_gcp_project_id
        self.credentials_path = self._resolve_credentials_path(
            settings.api_google_application_credentials
        )
        self._initialized = False

    def _resolve_credentials_path(self, credentials_path: str | None) -> str | None:
        """Resolve credentials path - if relative, resolve from project root"""
        if not credentials_path:
            return None

        if os.path.isabs(credentials_path):
            # Absolute path, use as is
            return credentials_path
        # Relative path, resolve from project root
        # From src/lus_laboris_api/api/services/ to project root: ../../../
        project_root = Path(__file__).parent.parent.parent.parent.parent
        return str(project_root / credentials_path)

    def _initialize_client(self):
        """Initialize GCS client with credentials"""
        if self._initialized:
            return True

        try:
            # Check if running in Cloud Run (no credentials file needed)
            if os.getenv("K_SERVICE"):  # Cloud Run environment variable
                logger.info("Running in Cloud Run, using default credentials")
                self.client = storage.Client()
                self._initialized = True
                return True
            # Running locally, need credentials file
            if not self.credentials_path:
                logger.warning(
                    "GOOGLE_APPLICATION_CREDENTIALS not set - GCP features will be unavailable"
                )
                return False

            if not os.path.exists(self.credentials_path):
                logger.warning(
                    "Credentials file not found: {self.credentials_path} - GCP features will be unavailable"
                )
                return False

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self.client = storage.Client(credentials=credentials)
            logger.info("GCS client initialized with credentials: {self.credentials_path}")
            self._initialized = True
            return True

        except Exception as e:
            logger.warning(
                "Failed to initialize GCS client: {e!s} - GCP features will be unavailable"
            )
            return False

    def health_check(self) -> dict[str, str]:
        """Check GCS health status"""
        try:
            # Initialize client if not already done
            if not self._initialize_client():
                return {"status": "unavailable", "message": "GCP credentials not configured"}

            # Try to list buckets
            buckets = list(self.client.list_buckets())
            return {
                "status": "connected",
                "buckets_count": len(buckets),
                "project_id": self.client.project,
            }
        except Exception as e:
            logger.exception("GCS health check failed")
            return {"status": "disconnected", "error": str(e)}

    def load_from_gcs_local(
        self,
        filename: str,
        folder: str,
        bucket_name: str,
        use_credentials: bool = True,
        credentials_path: str = "../.gcpcredentials",
    ) -> dict[str, Any]:
        """Load JSON file from GCS for local mode with credentials"""
        try:
            # Construct file path in GCS
            file_path = f"{folder}/{filename}"

            if use_credentials:
                # Use provided credentials path
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError("Credentials file not found: {credentials_path}")

                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                client = storage.Client(credentials=credentials)
            else:
                # Initialize client if not already done
                if not self._initialize_client():
                    raise ConnectionError(
                        "GCP client not initialized. Please configure GOOGLE_APPLICATION_CREDENTIALS"
                    )
                client = self.client

            # Get bucket
            bucket = client.bucket(bucket_name)

            # Check if file exists
            blob = bucket.blob(file_path)
            if not blob.exists():
                raise FileNotFoundError("File not found: gs://{bucket_name}/{file_path}")

            # Download file content
            logger.info("Downloading file from GCS (local mode): gs://{bucket_name}/{file_path}")
            content = blob.download_as_text()

            # Parse JSON
            data = json.loads(content)
            logger.info(
                "Successfully loaded JSON file with {len(data.get('articulos', []))} articles"
            )

            return data

        except Exception as e:
            logger.exception("Failed to load JSON from GCS (local mode)")
            raise

    def load_from_gcs_cloud(self, filename: str, folder: str, bucket_name: str) -> dict[str, Any]:
        """Load JSON file from GCS for cloud mode (automatic credentials)"""
        try:
            # Construct file path in GCS
            file_path = f"{folder}/{filename}"

            # Initialize client if not already done
            if not self._initialize_client():
                raise ConnectionError(
                    "GCP client not initialized. Please configure GOOGLE_APPLICATION_CREDENTIALS"
                )
            client = self.client

            # Get bucket
            bucket = client.bucket(bucket_name)

            # Check if file exists
            blob = bucket.blob(file_path)
            if not blob.exists():
                raise FileNotFoundError("File not found: gs://{bucket_name}/{file_path}")

            # Download file content
            logger.info("Downloading file from GCS (cloud mode): gs://{bucket_name}/{file_path}")
            content = blob.download_as_text()

            # Parse JSON
            data = json.loads(content)
            logger.info(
                "Successfully loaded JSON file with {len(data.get('articulos', []))} articles"
            )

            return data

        except Exception as e:
            logger.exception("Failed to load JSON from GCS (cloud mode)")
            raise

    def load_json_from_gcs(
        self, bucket_name: str, file_path: str, credentials_path: str | None = None
    ) -> dict[str, Any]:
        """Load JSON file from Google Cloud Storage (legacy method)"""
        try:
            # If credentials path is provided, use it for this operation
            if credentials_path and not os.getenv("K_SERVICE"):
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError("Credentials file not found: {credentials_path}")

                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                client = storage.Client(credentials=credentials)
            else:
                # Initialize client if not already done
                if not self._initialize_client():
                    raise ConnectionError(
                        "GCP client not initialized. Please configure GOOGLE_APPLICATION_CREDENTIALS"
                    )
                client = self.client

            # Get bucket
            bucket = client.bucket(bucket_name)

            # Check if file exists
            blob = bucket.blob(file_path)
            if not blob.exists():
                raise FileNotFoundError("File not found: gs://{bucket_name}/{file_path}")

            # Download file content
            logger.info("Downloading file from GCS: gs://{bucket_name}/{file_path}")
            content = blob.download_as_text()

            # Parse JSON
            data = json.loads(content)
            logger.info(
                "Successfully loaded JSON file with {len(data.get('articulos', []))} articles"
            )

            return data

        except Exception as e:
            logger.exception("Failed to load JSON from GCS")
            raise

    def upload_json_to_gcs(
        self,
        data: dict[str, Any],
        bucket_name: str,
        file_path: str,
        credentials_path: str | None = None,
    ) -> bool:
        """Upload JSON data to Google Cloud Storage"""
        try:
            # If credentials path is provided, use it for this operation
            if credentials_path and not os.getenv("K_SERVICE"):
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError("Credentials file not found: {credentials_path}")

                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                client = storage.Client(credentials=credentials)
            else:
                # Initialize client if not already done
                if not self._initialize_client():
                    raise ConnectionError(
                        "GCP client not initialized. Please configure GOOGLE_APPLICATION_CREDENTIALS"
                    )
                client = self.client

            # Get bucket
            bucket = client.bucket(bucket_name)

            # Convert data to JSON string
            json_content = json.dumps(data, ensure_ascii=False, indent=2)

            # Upload to GCS
            blob = bucket.blob(file_path)
            blob.upload_from_string(json_content, content_type="application/json")

            logger.info("Successfully uploaded JSON to GCS: gs://{bucket_name}/{file_path}")
            return True

        except Exception as e:
            logger.exception("Failed to upload JSON to GCS")
            raise

    def list_files_in_bucket(
        self, bucket_name: str, prefix: str = "", credentials_path: str | None = None
    ) -> list[str]:
        """List files in a GCS bucket with optional prefix"""
        try:
            # If credentials path is provided, use it for this operation
            if credentials_path and not os.getenv("K_SERVICE"):
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError("Credentials file not found: {credentials_path}")

                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                client = storage.Client(credentials=credentials)
            else:
                # Initialize client if not already done
                if not self._initialize_client():
                    raise ConnectionError(
                        "GCP client not initialized. Please configure GOOGLE_APPLICATION_CREDENTIALS"
                    )
                client = self.client

            # Get bucket
            bucket = client.bucket(bucket_name)

            # List blobs
            blobs = bucket.list_blobs(prefix=prefix)
            file_paths = [blob.name for blob in blobs]

            logger.info(
                "Found {len(file_paths)} files in bucket {bucket_name} with prefix '{prefix}'"
            )
            return file_paths

        except Exception as e:
            logger.exception("Failed to list files in bucket")
            raise

    def file_exists_in_bucket(
        self, bucket_name: str, file_path: str, credentials_path: str | None = None
    ) -> bool:
        """Check if file exists in GCS bucket"""
        try:
            # If credentials path is provided, use it for this operation
            if credentials_path and not os.getenv("K_SERVICE"):
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError("Credentials file not found: {credentials_path}")

                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                client = storage.Client(credentials=credentials)
            else:
                # Initialize client if not already done
                if not self._initialize_client():
                    raise ConnectionError(
                        "GCP client not initialized. Please configure GOOGLE_APPLICATION_CREDENTIALS"
                    )
                client = self.client

            # Get bucket and blob
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(file_path)

            return blob.exists()

        except Exception as e:
            logger.exception("Failed to check file existence")
            return False

    def get_file_metadata(
        self, bucket_name: str, file_path: str, credentials_path: str | None = None
    ) -> dict[str, Any] | None:
        """Get file metadata from GCS"""
        try:
            # If credentials path is provided, use it for this operation
            if credentials_path and not os.getenv("K_SERVICE"):
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError("Credentials file not found: {credentials_path}")

                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                client = storage.Client(credentials=credentials)
            else:
                # Initialize client if not already done
                if not self._initialize_client():
                    raise ConnectionError(
                        "GCP client not initialized. Please configure GOOGLE_APPLICATION_CREDENTIALS"
                    )
                client = self.client

            # Get bucket and blob
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(file_path)

            if not blob.exists():
                return None

            # Reload to get metadata
            blob.reload()

            return {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "time_created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "md5_hash": blob.md5_hash,
                "etag": blob.etag,
            }

        except Exception as e:
            logger.exception("Failed to get file metadata")
            return None


# Global service instance
gcp_service = GCPService()
