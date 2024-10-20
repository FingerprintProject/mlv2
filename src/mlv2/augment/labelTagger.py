from typing import Any, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from scipy import spatial
from ..utils import FpBaseModel, logPipeline


class LabelTagger(FpBaseModel):

    data: Optional[pd.DataFrame] = None
    colX: Optional[List[str]] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    def fit(self, X, y):
        # Check if index of X and y is the same
        idxDiff = X.index.difference(y.index).values.shape[0]
        if idxDiff > 0:
            raise Exception("X and y have difference indices")
        self.data = pd.concat([y, X], axis=1)
        self.data = self.data.rename(columns={y.name: "y"})
        self.colX = X.columns.values.tolist()
        pass

    def calc_obs(
        self, data: pd.DataFrame, numSample: Optional[int] = None
    ) -> pd.DataFrame:
        """Average over random "numSample" observations per zone names."""

        def rowFn(df: pd.DataFrame, numSample) -> pd.DataFrame:
            dft = df.drop(columns=["y"])
            nTot = dft.shape[0]

            # Figure out the number of samples
            ns = numSample if numSample != None and numSample <= nTot else nTot

            # Sampling
            dft = dft.sample(ns, replace=False)

            # Calculate mean of X columns.
            sr = dft.agg(["mean"]).loc["mean"]
            sr.name = "y"
            return sr

        res = data.groupby(by="y").apply(lambda dft: rowFn(dft, numSample))
        res = res.reset_index(drop=True)
        return res


# def cal_min_dist_neighbors(_df: pd.DataFrame, embSize: int, metric: str) -> pd.Series:
#     _colsX = get_cols_X(embSize)

#     X = _df[_colsX]  # ndarray(num_RP, embSize)
#     dists = spatial.distance.cdist(X, X, metric=metric)  # ndarray(num_RP, num_RP)

#     dft = pd.DataFrame(dists)
#     dft = dft.replace(0, np.NaN)  # This is so that min function ignores zero.
#     srOut = dft.agg("min", axis=1)

#     return srOut
