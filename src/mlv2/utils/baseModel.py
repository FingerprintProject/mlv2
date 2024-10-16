from typing import Dict
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from .logger import Logger
from .pipeline import Pipeline


class FpBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: str = Field(default_factory=lambda: uuid4().hex)
    logger: Logger = Field(default_factory=lambda: Logger(name=__name__))
    pipeline: Pipeline = Field(default_factory=Pipeline)
    initInfo: Dict = {}
