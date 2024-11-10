import datetime
import os
import pickle
from typing import Any, List, Union
from uuid import uuid4

from google.cloud import storage
from pydantic import Field

from .baseModel import UUID_TRUNCATE, FpBaseModel
from mlv2.db import FpModelRepository
from sqlalchemy.orm import Session, sessionmaker


class SaverBase(FpBaseModel):
    now: datetime.datetime = Field(default_factory=datetime.datetime.now)
    folderNamePrefix: str = "run"
    folderParentPath: str = "save"


class SaverFS(SaverBase):

    def save(self, classInsArr: List[Any]):

        folderNameSuffix = self.now.strftime("%Y-%m-%d_%H-%M-%S")
        folderName = f"{self.folderNamePrefix}_{folderNameSuffix}"
        folderPath = os.path.join(self.folderParentPath, folderName)

        if not os.path.exists(self.folderParentPath):
            os.mkdir(self.folderParentPath)

        if not os.path.exists(folderPath):
            os.mkdir(folderPath)

        for classIns in classInsArr:
            className = type(classIns).__name__
            if hasattr(classIns, "uuid"):
                uuid = classIns.uuid
            else:
                self.logger.warning(f"No uuid found in class {className}")
                uuid = uuid4().hex[:UUID_TRUNCATE]
            fileNameSuffix = uuid

            fileName = f"{className}_{fileNameSuffix}.pickle"
            filePath = os.path.join(folderPath, fileName)
            with open(filePath, "wb") as handle:
                pickle.dump(classIns, handle, protocol=pickle.HIGHEST_PROTOCOL)
            self.logger.info(f"Save {className} to {fileName} successfully")


class SaverGCP(SaverBase):
    hospitalId: int
    credentials: Any
    projectName: str = "daywork-215507"
    storageClient: Any = None
    bucketName: str = "wifi-localization-model-dev"
    bucket: Any = None
    fpModelRepository: FpModelRepository
    Session: Union[Session, sessionmaker]

    def model_post_init(self, __context):
        self.storageClient = storage.Client(
            project=self.projectName, credentials=self.credentials
        )
        self.bucket = self.storageClient.bucket(self.bucketName)

        # Change the "main" path in GCS according to hospitalId
        self.folderParentPath = f"V2_HID_{self.hospitalId}"

    def getFolderName(self):
        folderNameSuffix = self.now.strftime("%Y-%m-%d_%H-%M-%S")
        folderName = f"{self.folderNamePrefix}_{folderNameSuffix}"
        return folderName

    def savePickle(self, classInsArr: List[Any]):

        contents = []
        for classIns in classInsArr:
            className = type(classIns).__name__
            if hasattr(classIns, "uuid"):
                uuid = classIns.uuid
            else:
                self.logger.warning(f"No uuid found in class {className}")
                uuid = uuid4().hex[:UUID_TRUNCATE]

            fileNameSuffix = uuid
            fileName = f"{className}_{fileNameSuffix}.pickle"

            gcpPath = "/".join([self.folderParentPath, self.getFolderName(), fileName])

            blob = self.bucket.blob(gcpPath)
            with blob.open(mode="wb") as handle:
                pickle.dump(classIns, handle, protocol=pickle.HIGHEST_PROTOCOL)
            self.logger.info(
                f"Save {className} to project={self.projectName}, bucket={self.bucketName}, path={gcpPath} successfully"
            )
            row = dict(
                path=gcpPath,
                filename=fileName,
                instanceId=fileNameSuffix,
                className=className,
            )
            contents.append(row)

        row = dict(
            path="/".join([self.folderParentPath, self.getFolderName()]),
            hospitalId=self.hospitalId,
            name=self.folderNamePrefix,
            contents=contents,
        )
        self.fpModelRepository.insert(Session=self.Session, dataArr=[row])

    def saveFile(self, filenameArr: List[str], tempFolderPathLocal="tmp"):
        for filename in filenameArr:
            filepathLocal = os.path.join(tempFolderPathLocal, filename)
            if not os.path.exists(filepathLocal):
                raise Exception(f"Cannot find file: {filepathLocal}")

        for filename in filenameArr:
            filepathLocal = os.path.join(tempFolderPathLocal, filename)
            gcpPath = "/".join([self.folderParentPath, self.getFolderName(), filename])

            # I need to log here because I want to keep as much logging info as possible before upload the log file.
            self.logger.info(
                f"Saving {filename} to project={self.projectName}, bucket={self.bucketName}, path={gcpPath}"
            )

            blob = self.bucket.blob(gcpPath)
            blob.upload_from_filename(filepathLocal)
