""" Still need some work"""

from typing import Optional, List

import pandas as pd
from pydantic import validate_call

from ..utils import logPipeline, FpBaseModel


class FpVectBase(FpBaseModel):

    data: Optional[pd.DataFrame] = None
    id_vectorizer: Optional[str] = None
    id_leBssid: Optional[str] = None
    colsX: Optional[List[str]] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    def getColsX(self):
        if not self.colsX:
            raise Exception("No cols X yet")
        return self.colsX


class FpVectSupervised(FpVectBase):
    id_leZone: Optional[str] = None
    zoneCentroid: Optional[pd.DataFrame] = None

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
        self.colsX = X.columns.tolist()
        X.insert(0, "y", y)
        self.data = X
        self.id_leBssid = id_leBssid
        self.id_vectorizer = id_vectorizer
        self.id_leZone = id_leZone
        self.isFitted = True

    def calcCentroid(self, numSample: Optional[int] = None) -> pd.DataFrame:
        """Average over random "numSample" observations per zone names."""

        def rowFn(df: pd.DataFrame, numSample) -> pd.DataFrame:

            dft = df[self.getColsX()]
            nTot = dft.shape[0]

            # Figure out the number of samples
            ns = numSample if numSample != None and numSample <= nTot else nTot

            # Sampling
            dft = dft.sample(ns, replace=False)

            # Calculate mean of X columns.
            sr = dft.agg(["mean"]).loc["mean"]
            sr.name = "mean"
            return sr

        dm = self.data.groupby(by="y").apply(lambda dft: rowFn(dft, numSample))
        dm.columns.name = None  # Get rid of the column name (for clean visualization)
        dm = dm.reset_index()
        dm = dm.rename(columns={"y": "cy"})

        # Generate unique index
        dm.index = self.getUniqueIdx(idxList=dm.index.values.tolist())

        self.zoneCentroid = dm
