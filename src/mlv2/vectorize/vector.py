from typing import Dict, List, Optional

import pandas as pd
from pydantic import validate_call

from ..utils import logPipeline, FpBaseModel


class Vector(FpBaseModel):

    data: Optional[pd.DataFrame] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def fit(self, X: pd.DataFrame, y: pd.Series, info={}):
        self.preventRefit()
        X.insert(0, "zoneNames", y)
        self.data = X
        self.isFitted = True
