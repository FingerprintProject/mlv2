import datetime
import os
import pickle
from typing import Any, List, Optional
from uuid import uuid4

import pandas as pd
from pydantic import BaseModel, Field, validate_call

from mlv2.utils import FpBaseModel

from .dbRepositories import FpModelRepository
from .storageRepository import GcsRepository
from .saver import MODEL_NAME_PREFIX


class DataSchema(BaseModel):
    classIns: Any
    fileName: str
    className: str
    instanceId: str


class LoaderBase(FpBaseModel):
    modelName: str
    now: datetime.datetime = Field(default_factory=datetime.datetime.now)
    folderParentPath: Optional[str] = None
    data: List[DataSchema] = []


class LoaderFs(FpBaseModel):

    @validate_call
    def fit(self, folderPath: str):
        """TODO: I should be able to use keyword to search for latest folder"""
        self.preventRefit()

        if not os.path.exists(folderPath):
            raise Exception("Folder not found.")

        # Filer only pickle files
        sr = pd.Series(os.listdir(folderPath))
        filt = sr.apply(lambda fn: ".pickle" in fn)
        sr = sr[filt]
        fileNameList = sr.values

        # Read data
        data = []
        for fileName in fileNameList:
            filePath = os.path.join(folderPath, fileName)
            with open(filePath, "rb") as handle:
                classIns = pickle.load(handle)
            className = type(classIns).__name__
            if hasattr(classIns, "uuid"):
                uuid = classIns.uuid
            else:
                uuid = ""
            tmp = dict(
                classIns=classIns, fileName=fileName, className=className, uuid=uuid
            )
            data.append(DataSchema(**tmp))

        self.data = data
        self.isFitted = True

    def chooseFolder(self, keyword):
        """TODO: Search for latest folder using keyword"""
        pass

    @validate_call
    def pick(self, searches: List[str]):

        if not self.isFitted:
            raise Exception("Not loaded")

        matches = []
        for d in self.data:
            searchStr = f"{d.className}{d.uuid}{d.fileName}"
            sr = pd.Series(searches)
            isMatched = sr.apply(lambda s: s in searchStr).any()
            if isMatched:
                matches.append(d)

        if len(matches) == 0:
            raise Exception("Cannot find any match")
        elif len(matches) != 1:
            raise Exception("Found more than one result. Narrow your search")
        else:
            return matches[0].classIns


class LoaderGcp(LoaderBase):
    hospitalId: int
    fpModelRepository: FpModelRepository
    storageRepository: GcsRepository

    def model_post_init(self, __context):
        # Change the "main" path in GCS according to hospitalId
        self.folderParentPath = f"{MODEL_NAME_PREFIX}_{self.hospitalId}"

    def fit(self, name):
        pickleContents = self.fpModelRepository.getModelRecord(
            data=dict(name=name, hospitalId=self.hospitalId)
        )
        for pc in pickleContents:
            path = pc["path"]
            classIns = self.storageRepository.loadPickle(path=path)
            tmp = dict(
                classIns=classIns,
                fileName=pc["fileName"],
                className=pc["className"],
                instanceId=pc["instanceId"],
            )
            self.data.append(DataSchema(**tmp))

        self.isFitted = True

    @validate_call
    def pick(self, searches: List[str]):

        if not self.isFitted:
            raise Exception("Not loaded")

        matches = []
        for d in self.data:
            searchStr = f"{d.className}{d.instanceId}{d.fileName}"
            sr = pd.Series(searches)
            isMatched = sr.apply(lambda s: s in searchStr).any()
            if isMatched:
                matches.append(d)

        if len(matches) == 0:
            raise Exception("Cannot find any match")
        elif len(matches) != 1:
            raise Exception("Found more than one result. Narrow your search")
        else:
            return matches[0].classIns
