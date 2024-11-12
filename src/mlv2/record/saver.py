import datetime
import os
from typing import Any, List, Optional, Union
from uuid import uuid4

from pydantic import Field

from mlv2.utils import UUID_TRUNCATE, FpBaseModel

from .dbRepositories import FpModelRepository
from .storageRepository import FsRepository, GcsRepository


class Saver(FpBaseModel):
    modelName: str
    now: datetime.datetime = Field(default_factory=datetime.datetime.now)
    hospitalId: int
    storageRepository: Union[GcsRepository, FsRepository]
    fpModelRepository: FpModelRepository
    folderParentL1: str = "save_V2"
    folderParentL2: Optional[str] = None

    def model_post_init(self, __context):
        # Change the level-2 path corresponding to hospitalId
        self.folderParentL2 = f"{self.hospitalId}"

    def getFolderName(self):
        folderNameSuffix = self.now.strftime("%Y-%m-%d_%H-%M-%S")
        folderName = f"{self.modelName}_{folderNameSuffix}"
        return folderName

    def savePickle(self, classInsArr: List[Any], makeActive=False):

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

            pathArr = [
                self.folderParentL1,
                self.folderParentL2,
                self.getFolderName(),
                fileName,
            ]

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
            path="/".join(
                [self.folderParentL1, self.folderParentL2, self.getFolderName()]
            ),
            hospitalId=self.hospitalId,
            name=self.modelName,
            contents=contents,
            makeActive=makeActive,
        )

        # Write to DB
        self.fpModelRepository.insertModelRecord(data=data)

    def saveFile(self, fileNameArr: List[str], tempFolderPathSource="tmp"):
        for fileName in fileNameArr:
            filePathSource = os.path.join(tempFolderPathSource, fileName)
            if not os.path.exists(filePathSource):
                raise Exception(f"Cannot find file: {filePathSource}")

        contents = []
        for fileName in fileNameArr:
            filePathSource = os.path.join(tempFolderPathSource, fileName)

            pathArr = [
                self.folderParentL1,
                self.folderParentL2,
                self.getFolderName(),
                fileName,
            ]

            path = self.storageRepository.storeFile(
                pathArr=pathArr, filePathSource=filePathSource
            )

            cRow = dict(
                path=path,
                fileName=fileName,
                instanceId="",
                className="",
            )
            contents.append(cRow)

            data = dict(
                path="/".join(
                    [self.folderParentL1, self.folderParentL2, self.getFolderName()]
                ),
                hospitalId=self.hospitalId,
                name=self.modelName,
                contents=contents,
                makeActive=False,
            )
        # Write to DB
        self.fpModelRepository.insertModelRecord(data=data)
