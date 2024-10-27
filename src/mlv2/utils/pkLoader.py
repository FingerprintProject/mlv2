import datetime
import os
import pickle
from typing import Any, List
from pydantic import Field, BaseModel, validate_call
from uuid import uuid4
import pandas as pd

from .baseModel import FpBaseModel


class PkLoaderData(BaseModel):
    classIns: Any
    fileName: str
    className: str
    uuid: str


class PkLoader(FpBaseModel):

    data: List[PkLoaderData] = []

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
            data.append(PkLoaderData(**tmp))

        self.data = data
        self.isFitted = True

    def chooseFolder(self, keyword):
        """TODO: Search for latest folder using keyword"""
        pass

    @validate_call
    def get(self, searches: List[str]):

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
