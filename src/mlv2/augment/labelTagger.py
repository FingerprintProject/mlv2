from typing import Any, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from scipy import spatial
from ..utils import FpBaseModel, logPipeline


class LabelTagger(FpBaseModel):

    data: Optional[pd.DataFrame] = None
    colX: Optional[List[str]] = None
    zoneCentroid: Optional[pd.DataFrame] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    def fit(self, X: pd.DataFrame, y: pd.Series):
        # Check if index of X and y is the same
        idxDiff = X.index.difference(y.index).values.shape[0]
        if idxDiff > 0:
            raise Exception("X and y have difference indices")
        y.name = "y"
        self.data = pd.concat([y, X], axis=1)
        self.colX = X.columns.values.tolist()

    def getColX(self):
        if not self.colX:
            raise Exception("No col X")
        return self.colX

    def calcDmCentroid(self, numSample: Optional[int] = None) -> pd.DataFrame:
        """Average over random "numSample" observations per zone names."""

        def rowFn(df: pd.DataFrame, numSample) -> pd.DataFrame:

            dft = df[self.getColX()]
            nTot = dft.shape[0]

            # Figure out the number of samples
            ns = numSample if numSample != None and numSample <= nTot else nTot

            # Sampling
            dft = dft.sample(ns, replace=False)

            # Calculate mean of X columns.
            sr = dft.agg(["mean"]).loc["mean"]
            sr.name = "y"
            return sr

        dm = self.data.groupby(by="y").apply(lambda dft: rowFn(dft, numSample))
        dm = dm.reset_index(drop=True)
        self.zoneCentroid = dm

    def cal_min_dist_neighbors(self, metric: str = "euclidean"):
        colX = self.getColX()
        X = self.zoneCentroid[colX]  # (numZoneName X embSize)
        dists = spatial.distance.cdist(
            X, X, metric=metric
        )  # (numZoneName X numZoneName)

        dft = pd.DataFrame(dists)
        dft = dft.replace(0, pd.NA)  # This is so that min function ignores zero.
        res = dft.agg("min", axis=1)

        return res
