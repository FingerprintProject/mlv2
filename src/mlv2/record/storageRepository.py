import pickle
from typing import Any, Optional
import os
from google.auth import default
from google.cloud import storage

from mlv2.utils import FpBaseModel
import shutil


class FsRepository(FpBaseModel):

    def storePickle(self, classIns, pathArr):
        folderPath = os.path.join(*pathArr[:-1])
        filePath = os.path.join(*pathArr)

        if not os.path.exists(folderPath):
            os.makedirs(folderPath, exist_ok=True)

        with open(filePath, "wb") as handle:
            pickle.dump(classIns, handle, protocol=pickle.HIGHEST_PROTOCOL)

        self.logger.info(
            f"Save {type(classIns).__name__}, path={filePath} successfully"
        )

        # I want to store path in DB in the same format even though the separator in Windows is \, not /
        return "/".join(pathArr)

    def storeFile(self, filePathSource, pathArr):
        folderPathDes = os.path.join(*pathArr[:-1])
        filePathDes = os.path.join(*pathArr)

        if not os.path.exists(folderPathDes):
            os.makedirs(folderPathDes, exist_ok=True)

        # os.rename(filePathSource, filePathDes)
        shutil.copy(filePathSource, filePathDes)
        self.logger.info(f"Save {filePathSource},  path={filePathDes} successfully")

        # I want to store path in DB in the same format even though the separator in Windows is \, not /
        return "/".join(pathArr)

    def loadPickle(self, path):

        # Recreate file path with correct separator
        pathArr = path.split("/")
        filePath = os.path.join(*pathArr)

        with open(filePath, "rb") as handle:
            classIns = pickle.load(handle)
        return classIns


class GcsRepository(FpBaseModel):
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

    def storeFile(self, filePathSource, pathArr):
        gcpPath = "/".join(pathArr)
        blob = self.bucket.blob(gcpPath)
        blob.upload_from_filename(filePathSource)
        self.logger.info(
            f"Save {filePathSource}, bucketName={self.bucketName}, path={gcpPath} successfully"
        )
        return gcpPath

    def loadPickle(self, path):
        blob = self.bucket.blob(path)
        with blob.open(mode="rb") as f:
            classIns = pickle.load(f)
        return classIns
