from typing import List, Optional

import numpy as np
import pandas as pd
from pydantic import validate_call
from scipy.spatial import KDTree, distance

from ..utils import FpBaseModel, logPipeline


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
    zc: Optional[pd.DataFrame] = None  # Zone centroids
    zcSelfNN: Optional[pd.DataFrame] = None  # Zone centroids self nearest neighbors

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
        dm.columns.name = None  # Get rid of the column name (for cleaner inspection)
        dm = dm.reset_index()
        dm = dm.rename(columns={"y": "cy"})

        # Generate unique index
        dm.index = self.getUniqueIdx(idxList=dm.index.values.tolist())

        self.zc = dm

    def calcZoneCentroidSelfNearestNeighbors(self):
        if self.zc is None:
            raise Exception("Please calculate zone centroid first")

        refPts = self.zc[self.getColsX()]
        refLabels = self.zc["cy"]
        queryPts = self.zc[self.getColsX()]
        k = 10
        res = self._calcKNeighbors(
            refPts=refPts, refLabels=refLabels, queryPts=queryPts, k=k
        )
        self.zcSelfNN = res

    def _calcKNeighbors(
        self, refPts: pd.DataFrame, refLabels: pd.Series, queryPts: pd.DataFrame, k: int
    ):
        refTree = KDTree(refPts)
        distArr, idxArr = refTree.query(queryPts, k=k)

        def rowFn(row, refPts, refLabels):
            k = int(
                row.shape[0] / 2
            )  # The first sets of indices is the "idx" and the second set of indices is distance.
            srIdx = row.iloc[:k].reset_index(drop=True).astype(int)
            nnCy = srIdx.apply(
                lambda idx: refLabels.iloc[idx] if idx < refLabels.shape[0] else None
            )
            nnCyIdx = srIdx.apply(
                lambda idx: refPts.index.values[idx] if idx < refPts.shape[0] else None
            )

            nnCyDist = row.iloc[k:].reset_index(drop=True)
            nnCyDist.replace([np.inf, -np.inf], None, inplace=True)
            dft = pd.DataFrame({"nnCy": nnCy, "nnCyDist": nnCyDist, "nnCyIdx": nnCyIdx})
            dft = dft[dft["nnCyDist"] != 0]  # Drop self point
            dft = dft.dropna()  # Drop invalid entries

            # Output into series
            res = pd.Series(
                [
                    dft["nnCy"].values.tolist(),
                    dft["nnCyDist"].values.tolist(),
                    dft["nnCyIdx"].values.tolist(),
                    dft.shape[0],
                ],
                index=["nnCy", "nnCyDist", "nnCyIdx", "nnCyK"],
            )
            return res

        dft = pd.DataFrame(
            np.concatenate([idxArr, distArr], axis=1), index=queryPts.index
        )
        nn = dft.apply(lambda row: rowFn(row, refPts, refLabels), axis=1)
        return nn
