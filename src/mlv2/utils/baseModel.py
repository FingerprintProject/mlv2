from typing import Dict, Any
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from .logger import Logger
from .pipeline import Pipeline
import pprint


class FpBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: str = Field(default_factory=lambda: uuid4().hex)
    logger: Logger = Field(default_factory=lambda: Logger(name=__name__))
    pipeline: Pipeline = Field(default_factory=Pipeline)
    info: Dict = {}

    def __repr__(self):
        return pprint.pformat(dict(name=type(self).__name__, id=self.uuid))

    def addInfo(self, data: Dict[str, Any]):
        self.info = {**self.info, **data}
