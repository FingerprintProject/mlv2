from typing import List, Optional
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from pydantic import validate_call, Field
from typing_extensions import Annotated
from ..utils import FpBaseModel, logPipeline


class PredictorLR(FpBaseModel):

    data: Optional[pd.DataFrame] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def fit(
        self,
        info={},
    ):
        pass
