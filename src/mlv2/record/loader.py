from typing import Any, List, Union

import pandas as pd
from pydantic import BaseModel, validate_call

from ..utils import FpBaseModel, logPipeline
from .dbRepositories import FpModelRepository
from .storageRepository import FsRepository, GcsRepository


class DataSchema(BaseModel):
    classIns: Any
    fileName: str
    className: str
    instanceId: str


class Loader(FpBaseModel):
    data: List[DataSchema] = []
    hospitalId: int
    fpModelRepository: FpModelRepository
    storageRepository: Union[GcsRepository, FsRepository]

    @logPipeline()
    def fitFromModelName(self, name):
        modelId, pickleContents = self.fpModelRepository.getModelRecord(
            data=dict(name=name, hospitalId=self.hospitalId)
        )
        data = []
        for pc in pickleContents:
            path = pc["path"]
            classIns = self.storageRepository.loadPickle(path=path)
            tmp = dict(
                classIns=classIns,
                fileName=pc["fileName"],
                className=pc["className"],
                instanceId=pc["instanceId"],
            )
            data.append(DataSchema(**tmp))
        self.data = data
        return modelId

    @logPipeline()
    def fitFromPath(self, path):
        """Make sure that path contains forward slash or double backslash, not single backslash"""

        # Conform with forward convention for filepath
        pathFixed = path.replace("\\", "/")

        # Read data
        filePathList = self.storageRepository.getModelFilePath(path=pathFixed)
        data = []
        for filePath in filePathList:
            classIns = self.storageRepository.loadPickle(path=filePath)
            className = type(classIns).__name__
            uuid = classIns.uuid if hasattr(classIns, "uuid") else ""
            tmp = dict(
                classIns=classIns,
                fileName=filePath.split("/")[-1],
                className=className,
                instanceId=uuid,
            )
            data.append(DataSchema(**tmp))
        self.data = data

    @validate_call
    def pick(self, searches: List[str]):

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
