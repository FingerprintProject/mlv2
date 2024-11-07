from typing import Dict, Any, List
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from .logger import Logger
from .pipeline import Pipeline
import pprint
import pandas as pd

UUID_TRUNCATE = 8


class FpBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: str = Field(default_factory=lambda: uuid4().hex[:UUID_TRUNCATE])
    logger: Logger = Field(
        default_factory=lambda: Logger(name=__name__, includeDateTimeInFilename=False)
    )
    pipeline: Pipeline = Field(default_factory=Pipeline)
    info: Dict = {}
    isFitted: bool = False

    def __repr__(self):
        """Return class instance representation without logger and pipeline"""
        repr = {
            k: v for k, v in self.__dict__.items() if k not in ["logger", "pipeline"]
        }
        repr = {**repr, **dict(__name__=type(self).__name__)}
        return pprint.pformat(repr)

    def __str__(self):
        return self.__repr__()

    def addInfo(self, data: Dict[str, Any]):
        self.info = {**self.info, **data}

    def preventRefit(self):
        if self.isFitted:
            raise Exception(f"Refitting is not allowed for {type(self).__name__}")

    def getUniqueIdx(self, idxList: List[Any]) -> pd.Series:
        return self.uuid[:4] + "_" + pd.Series(idxList).astype(str)
