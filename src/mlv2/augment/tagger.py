from typing import List, Optional

import pandas as pd
from pydantic import validate_call
from scipy.spatial import KDTree, distance

from ..utils import FpBaseModel, logPipeline


class TaggerDistanceSimple(FpBaseModel):

    data: Optional[pd.DataFrame] = None
    colsX: Optional[List[str]] = None
    radiusMultipler: Optional[float] = None
    id_fpVectSupervised: Optional[str] = None
    id_fpVectUnsupervised: Optional[str] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def fit(
        self,
        cX: pd.DataFrame,
        cDistNn: pd.Series,
        cy: pd.Series,
        uFp: pd.DataFrame,
        id_fpVectSupervised,
        id_fpVectUnsupervised,
        radiusMultipler: float = 0.5,
        maxTaggedNeighbors: int = 200,
    ):

        self.radiusMultipler = radiusMultipler
        self.id_fpVectSupervised = id_fpVectSupervised
        self.id_fpVectUnsupervised = id_fpVectUnsupervised

        # Make sure that the indices of pandas objects are idential (both value and order)
        if not cX.index.equals(cDistNn.index):
            raise Exception("Index of cX and cDistNn are not identical")
        if not cX.index.equals(cy.index):
            raise Exception("Index of cX and cy are not identical")

        # Make sure that the columns of fingerprints are identical.
        if not cX.columns.equals(uFp.columns):
            raise Exception("Columns of cX and uFp is not identical")
        # Storing
        self.colsX = cX.columns.values.tolist()

        refPts = uFp
        queryPts = cX
        queryRadius = cDistNn * radiusMultipler
        queryLabels = cy

        dfNn = self._calcNn(refPts, queryPts, queryRadius, queryLabels)

        filtZeroNn = dfNn["nnAugK"] == 0
        if filtZeroNn.sum() > 0:
            self.logger.warning(
                f"Found {filtZeroNn.sum()} out of {filtZeroNn.shape[0]} centroid labels with zero neighbors"
            )
        filtMax = dfNn["nnAugK"] > maxTaggedNeighbors
        if filtMax.sum() > 0:
            self.logger.info(
                f"Found {filtMax.sum()} out of {filtZeroNn.shape[0]} centroids with unsupervised FP neighbors larger than {maxTaggedNeighbors}. The number of tagged neighbors will be capped to {maxTaggedNeighbors}"
            )

        # Collecting unsupervised fp and tag them with cy
        def rowFn(row):
            idx = row["nnAugIdx"]
            dfr = refPts.loc[idx]
            dfr["cy"] = row["cy"]
            # Enforce max neightbors
            dfr = dfr.iloc[:maxTaggedNeighbors, :]
            return dfr

        sr = dfNn.apply(rowFn, axis=1)
        dfFp = pd.concat(sr.values)
        self.data = dfFp

    def _calcNn(self, refPts, queryPts, queryRadius, queryLabels):

        def rowFn(row, refTree, refPts):
            radius = row["radius"]
            srIdx = [idx for idx in row.index if idx not in ["radius"]]
            pt = row[srIdx]
            nnIdx = refTree.query_ball_point(pt, radius)

            refPtsSelected = refPts.iloc[nnIdx, :]
            _dists = distance.cdist([pt], refPtsSelected)
            dists = pd.Series(_dists[0], index=refPtsSelected.index, name="nnAugDist")
            dft = pd.concat([refPtsSelected, dists], axis=1)
            dft = dft.sort_values(by="nnAugDist")
            dft = dft[dft["nnAugDist"] != 0]
            res = pd.Series(
                [
                    dft.index.values.tolist(),
                    dft["nnAugDist"].values.tolist(),
                    dft.shape[0],
                ],
                index=["nnAugIdx", "nnAugDist", "nnAugK"],
            )
            return res

        refTree = KDTree(refPts)
        queryRadius.name = "radius"
        dft = pd.concat([queryPts, queryRadius], axis=1)

        if dft.isna().any().any():
            raise Exception(
                "Found NaN after joining pandas dataframes. Check indices of pandas objects"
            )
        zcAug = dft.apply(lambda row: rowFn(row, refTree, refPts), axis=1)
        zcAugLabelled = pd.concat([zcAug, queryLabels], axis=1)
        return zcAugLabelled

    def getColsX(self):
        if self.colsX is None:
            raise Exception("No colsX")
        return self.colsX
