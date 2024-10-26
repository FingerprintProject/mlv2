from typing import List, Optional

import pandas as pd
from pydantic import validate_call
from scipy.spatial import KDTree, distance

from ..utils import FpBaseModel, logPipeline


class TaggerDistanceSimple(FpBaseModel):

    data: Optional[pd.DataFrame] = None
    colX: Optional[List[str]] = None
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
    ):
        """_summary_

        Args:
            zc (pd.DataFrame): zone centroid
            zcNnDist (pd.Series): nearest distance to the nearest neighbor of each controid
            uFp (pd.DataFrame): unsupervised fingerprints
            colsX: list of X column names
            radiusMultipler (float, optional): fraction of radius to the nearest centroid to search "uFp" for. Defaults to 0.5.
        """
        self.radiusMultipler = radiusMultipler
        self.id_fpVectSupervised = id_fpVectSupervised
        self.id_fpVectUnsupervised = id_fpVectUnsupervised

        # Make sure that the indices of pandas objects are idential (both value and order)
        if not cX.index.equals(cDistNn.index):
            raise Exception("Index of cX and cDistNn are not identical")
        if not cX.index.equals(cy.index):
            raise Exception("Index of cX and cy are not identical")

        refPts = uFp
        queryPts = cX
        queryRadius = cDistNn * radiusMultipler

        res = self._calcNn(refPts, queryPts, queryRadius)
        pass

    def _calcNn(self, refPts, queryPts, queryRadius):

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

        return zcAug
