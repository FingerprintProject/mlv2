from typing import Any, List, Union

import pandas as pd
from pydantic import BaseModel, validate_call

from mlv2.utils import FpBaseModel

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

    def fitFromModelName(self, name):
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

    def fitFromPath(self, path):
        pass

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
