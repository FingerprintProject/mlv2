import datetime
import os
import pickle
from typing import Any, List
from pydantic import Field
from uuid import uuid4

from .baseModel import FpBaseModel


class PkSaver(FpBaseModel):

    folderNamePrefix: str = "run"
    folderParentPath: str = "save"
    now: datetime.datetime = Field(default_factory=datetime.datetime.now)

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
                uuid = uuid4().hex
            fileNameSuffix = uuid[:5]

            fileName = f"{className}_{fileNameSuffix}.pickle"
            filePath = os.path.join(folderPath, fileName)
            with open(filePath, "wb") as handle:
                pickle.dump(classIns, handle, protocol=pickle.HIGHEST_PROTOCOL)
            self.logger.info(f"Save {className} to {fileName} successfully")
