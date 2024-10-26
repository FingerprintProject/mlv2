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
        zc: pd.DataFrame,
        zcNnDist: pd.Series,
        cols: List[str],
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

        # Make sure that the index is idential (both value and order)
        if not queryPts.index.equals(queryRadius.index):
            raise Exception("Index pf queryPts and queryRadius are not identical")

        refPts = uFp[cols]
        queryPts = zc[cols]
        queryRadius = zcNnDist
        queryRadius = queryRadius * radiusMultipler

        self._calcNn(refPts, queryPts, queryRadius)

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
        zcAug = dft.apply(lambda row: rowFn(row, refTree, refPts), axis=1)

        return zcAug
