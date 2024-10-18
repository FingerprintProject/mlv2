""" Still need some work"""

from typing import Optional

import pandas as pd
from pydantic import validate_call

from ..utils import logPipeline, FpBaseModel


class FpVect(FpBaseModel):

    data: Optional[pd.DataFrame] = None
    id_vectorizer: Optional[str] = None
    id_leBssid: Optional[str] = None
    id_leZone: Optional[str] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        id_vectorizer: str,
        id_leBssid: str,
        id_leZone: str,
        info={},
    ):
        self.preventRefit()
        X.insert(0, "zoneNames", y)
        self.data = X
        self.id_leBssid = id_leBssid
        self.id_vectorizer = id_vectorizer
        self.id_leZone = id_leZone
        self.isFitted = True
