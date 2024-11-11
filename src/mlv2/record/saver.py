import datetime
import os
import pickle
from typing import Any, List
from uuid import uuid4

from pydantic import Field

from mlv2.utils import UUID_TRUNCATE, FpBaseModel
from .dbRepositories import FpModelRepository
from .storageRepository import GcpRepository


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
    storageRepository: GcpRepository
    fpModelRepository: FpModelRepository

    def model_post_init(self, __context):
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

            pathArr = [self.folderParentPath, self.getFolderName(), fileName]

            # Upload
            path = self.storageRepository.storePickle(
                classIns=classIns, pathArr=pathArr
            )

            cRow = dict(
                path=path,
                fileName=fileName,
                instanceId=fileNameSuffix,
                className=className,
            )
            contents.append(cRow)

        data = dict(
            path="/".join([self.folderParentPath, self.getFolderName()]),
            hospitalId=self.hospitalId,
            name=self.folderNamePrefix,
            contents=contents,
        )

        # Write to DB
        self.fpModelRepository.insertModelRecord(data=data)

    def saveFile(self, fileNameArr: List[str], tempFolderPathLocal="tmp"):
        for fileName in fileNameArr:
            filePathLocal = os.path.join(tempFolderPathLocal, fileName)
            if not os.path.exists(filePathLocal):
                raise Exception(f"Cannot find file: {filePathLocal}")

        contents = []
        for fileName in fileNameArr:
            filePathLocal = os.path.join(tempFolderPathLocal, fileName)

            pathArr = [self.folderParentPath, self.getFolderName(), fileName]

            path = self.storageRepository.storeFile(
                pathArr=pathArr, filePathLocal=filePathLocal
            )

            cRow = dict(
                path=path,
                fileName=fileName,
                instanceId="",
                className="",
            )
            contents.append(cRow)

            data = dict(
                path="/".join([self.folderParentPath, self.getFolderName()]),
                hospitalId=self.hospitalId,
                name=self.folderNamePrefix,
                contents=contents,
            )
        # Write to DB
        self.fpModelRepository.insertModelRecord(data=data)
