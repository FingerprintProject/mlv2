from typing import List, Optional
from sklearn.model_selection import train_test_split
import pandas as pd
from pydantic import validate_call, Field
from typing_extensions import Annotated
from ..utils import FpBaseModel, logPipeline

modePattern = r"^ALL$|^TRAIN$|^TEST$"
queryModePatterm = r"^ALL_DATA$|^TRAIN_DATA$|^TEST_DATA$"


class FpVectTrain(FpBaseModel):

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

    def trainTestSplit(self, testSize=0.3, random_state=42):
        if self.mode != "ALL":
            raise Exception("Mode is not ALL")

        X = self.getX(queryMode="ALL")
        y = self.getLabels(queryMode="ALL")
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

    def getX(self, queryMode="ALL"):
        if self.data is None:
            raise Exception("No X")
        data = self.filterTestTrain(queryMode)
        return data[self.getColsX()]

    def getLabels(self, queryMode="ALL"):
        if self.data is None:
            raise Exception("No data")
        data = self.filterTestTrain(queryMode)
        return data["y"]

    def getLabelStats(self, queryMode="ALL"):
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
            raise Exception("Invalid mode")

    def SMOTE(self):
        """TODO add smote"""
        if self.mode != "TRAIN":
            raise Exception("Can only perform SMOTE on the train data")
        pass
