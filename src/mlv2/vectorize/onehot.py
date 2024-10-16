from typing import Dict, List, Optional

import pandas as pd
from pydantic import validate_call
from sklearn.feature_extraction import DictVectorizer

from mlv2.utils import FpBaseModel, logPipeline


class OneHot(FpBaseModel):
    data: Optional[pd.DataFrame] = None
    model: Optional[DictVectorizer] = None
    sparse: bool = False

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call
    def fit(self, data: List[Dict[str, int]], info={}):
        self.preventRefit()
        self.model = DictVectorizer(sparse=self.sparse)
        self.model.fit(data)
        self.data = pd.DataFrame(
            self.model.transform(data), columns=self.model.get_feature_names_out()
        )
        self.isFitted = True
