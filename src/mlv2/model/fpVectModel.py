from typing import List, Optional

import numpy as np
import pandas as pd
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import ClusterCentroids
from pydantic import Field, validate_call
from sklearn.cluster import MiniBatchKMeans
from sklearn.model_selection import train_test_split
from typing_extensions import Annotated

from ..utils import FpBaseModel, logPipeline

modePattern = r"^ALL$|^TRAIN$|^TEST$"
queryModePatterm = r"^ALL_DATA$|^TRAIN_DATA$|^TEST_DATA$"


class FpVectModel(FpBaseModel):

    data: Optional[pd.DataFrame] = None
    mode: Optional[str] = Field(pattern=modePattern, default=None)
    idxTrain: Optional[str] = None
    idxTest: Optional[str] = None
    testSize: Optional[float] = None
    id_vectorizer: Optional[str] = None
    id_leBssid: Optional[str] = None
    id_leZone: Optional[str] = None
    colsX: Optional[List[str]] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def fit(
        self,
        XArr: List[pd.DataFrame],
        yArr: List[pd.Series],
        mode: Annotated[str, Field(pattern=r"^ALL$|^TRAIN$|^TEST$")],
        id_vectorizer: str,
        id_leBssid: str,
        id_leZone: str,
        info={},
    ):
        self.preventRefit()
        self.mode = mode

        if len(XArr) != len(yArr):
            raise Exception("Unequal length for XArr and yArr")

        X = pd.concat(XArr, axis=0)
        y = pd.concat(yArr)
        self.colsX = X.columns.tolist()
        X.insert(0, "y", y)

        if X.isna().any().any():
            raise Exception(
                "Error in joining dataframe. Check column names and row indices of dataframe/series"
            )

        if X.index.duplicated().any():
            raise Exception("Found duplicated index.")

        self.data = X
        self.id_leBssid = id_leBssid
        self.id_vectorizer = id_vectorizer
        self.id_leZone = id_leZone
        self.isFitted = True

    def trainTestSplit(self, testSize=0.3, random_state=1):
        if self.mode != "ALL":
            raise Exception("Mode is not ALL")

        X = self.getX(queryMode="ALL_DATA")
        y = self.getLabels(queryMode="ALL_DATA")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=testSize, random_state=random_state, stratify=y
        )
        self.idxTrain = X_train.index.values.tolist()
        self.idxTest = X_test.index.values.tolist()
        self.testSize = testSize
        pass

    def getColsX(self):
        if not self.colsX:
            raise Exception("No cols X yet")
        return self.colsX

    def getX(self, queryMode="ALL_DATA"):
        if self.data is None:
            raise Exception("No X")
        data = self.filterTestTrain(queryMode)
        return data[self.getColsX()]

    def getLabels(self, queryMode="ALL_DATA"):
        if self.data is None:
            raise Exception("No data")
        data = self.filterTestTrain(queryMode)
        return data["y"]

    def getLabelStats(self, queryMode="ALL_DATA"):
        if self.data is None:
            raise Exception("No data")
        data = self.filterTestTrain(queryMode)

        stats = data["y"].value_counts().describe().to_dict()
        self.logger.info(f"Stats for y label in {self.uuid} ({queryMode}): {stats}")
        return stats

    def filterTestTrain(self, queryMode: Annotated[str, Field(pattern=modePattern)]):
        # If the mode of the instance is not ALL, return all data.
        if self.mode != "ALL":
            if queryMode != "ALL_DATA":
                self.logger.info("Returning ALL data due to self.mode != ALL_DATA")
            return self.data

        if queryMode == "ALL_DATA":
            return self.data
        elif queryMode == "TRAIN_DATA":
            return self.data.loc[self.idxTrain, :]
        elif queryMode == "TEST_DATA":
            return self.data.loc[self.idxTest, :]
        else:
            raise Exception(f"Invalid mode. Receive {queryMode}")

    def SMOTE(self):
        if self.mode != "TRAIN":
            raise Exception("Can only perform SMOTE on the train data")

        X = self.getX()
        y = self.getLabels()

        # Oversampling
        statsOver = y.value_counts().describe()
        targetOver = int(np.ceil(statsOver["75%"]))

        def rowFnOver(row):
            y = row["y"]
            _count = row["count"]
            if _count < targetOver:
                count = targetOver
            else:
                count = _count
            return pd.Series([y, count], index=["y", "count"])

        dfOver = y.value_counts().reset_index().apply(rowFnOver, axis=1)
        overSamplingStrategy = dfOver.set_index("y", drop=True).to_dict()["count"]

        # Take care of the case where class samples are less than 5
        kNeighborsMax = 6
        minNumSample = y.value_counts().min() - 1
        kNeightbors = minNumSample if minNumSample <= kNeighborsMax else kNeighborsMax

        oversampler = SMOTEENN(
            sampling_strategy=overSamplingStrategy,
            random_state=42,
            smote=SMOTE(
                sampling_strategy=overSamplingStrategy, k_neighbors=kNeightbors
            ),
        )
        X_over, y_over = oversampler.fit_resample(X, y)
        self.logger.info(f"Oversampling: {y_over.value_counts().to_dict()}")

        # Undersampling
        statsUnder = y_over.value_counts().describe()
        targetUnder = int(np.ceil(statsUnder["75%"]))

        def rowFnUnder(row):
            y = row["y"]
            _count = row["count"]
            if _count > targetUnder:
                count = targetUnder
            else:
                count = _count
            return pd.Series([y, count], index=["y", "count"])

        dftUnder = y_over.value_counts().reset_index().apply(rowFnUnder, axis=1)
        underSamplingStrategy = dftUnder.set_index("y", drop=True).to_dict()["count"]
        underSampler = ClusterCentroids(
            sampling_strategy=underSamplingStrategy,
            estimator=MiniBatchKMeans(n_init=1, random_state=0),
            random_state=42,
        )
        X_over_under, y_over_under = underSampler.fit_resample(X_over, y_over)
        self.logger.info(f"Undersampling: {y_over_under.value_counts().to_dict()}")

        # Store result back to data
        res = X_over_under
        res.insert(0, "y", y_over_under)
        self.data = res
        pass

    def getIds(self):
        if (
            (self.id_leZone is None)
            or (self.id_leBssid is None)
            or (self.id_vectorizer is None)
        ):
            raise Exception("No ids")
        return dict(
            id_leZone=self.id_leZone,
            id_leBssid=self.id_leBssid,
            id_vectorizer=self.id_vectorizer,
        )


class FpVectModelTrain(FpVectModel):
    pass


class FpVectModelTest(FpVectModel):
    pass
