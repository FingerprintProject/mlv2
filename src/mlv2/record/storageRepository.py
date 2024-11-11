import pickle
from typing import Any, Optional

from google.auth import default
from google.cloud import storage

from mlv2.utils import FpBaseModel


class GcpRepository(FpBaseModel):
    projectName: str = "daywork-215507"
    bucketName: str = "wifi-localization-model-dev"
    storageClient: Any = None
    bucket: Any = None
    credentials: Optional[Any] = None

    def model_post_init(self, __context):
        credentials, _ = default()
        self.credentials = credentials
        self.storageClient = storage.Client(
            project=self.projectName, credentials=self.credentials
        )
        self.bucket = self.storageClient.bucket(self.bucketName)

    def storePickle(self, classIns, pathArr):
        gcpPath = "/".join(pathArr)
        blob = self.bucket.blob(gcpPath)
        with blob.open(mode="wb") as handle:
            pickle.dump(classIns, handle, protocol=pickle.HIGHEST_PROTOCOL)
        self.logger.info(
            f"Save {type(classIns).__name__}, bucketName={self.bucketName}, path={gcpPath} successfully"
        )
        return gcpPath

    def storeFile(self, filePathLocal, pathArr):
        gcpPath = "/".join(pathArr)
        blob = self.bucket.blob(gcpPath)
        blob.upload_from_filename(filePathLocal)
        self.logger.info(
            f"Save {filePathLocal}, bucketName={self.bucketName}, path={gcpPath} successfully"
        )
        return gcpPath
