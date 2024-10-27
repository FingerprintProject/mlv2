from typing import List, Optional
from sklearn.model_selection import train_test_split
import pandas as pd
from pydantic import validate_call, Field
from typing_extensions import Annotated
from ..utils import FpBaseModel, logPipeline


class FpTrain(FpBaseModel):

    data: Optional[pd.DataFrame] = None
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
        id_vectorizer: str,
        id_leBssid: str,
        id_leZone: str,
        info={},
    ):
        self.preventRefit()

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
        X = self.getX(mode="ALL")
        y = self.getLabels(mode="ALL")
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

    def getX(self, mode="ALL"):
        if self.data is None:
            raise Exception("No X")
        data = self.filterTestTrain(mode)
        return data[self.getColsX()]

    def getLabels(self, mode="ALL"):
        if self.data is None:
            raise Exception("No data")
        data = self.filterTestTrain(mode)
        return data["y"]

    def getLabelStats(self, mode="ALL"):
        if self.data is None:
            raise Exception("No data")
        data = self.filterTestTrain(mode)

        stats = data["y"].value_counts().describe().to_dict()
        self.logger.info(f"Stats for y label in {self.uuid} ({mode}): {stats}")
        return stats

    def filterTestTrain(
        self, mode: Annotated[str, Field(pattern=r"^ALL$|^TRAIN$|^TEST$")]
    ):
        if mode == "ALL":
            return self.data
        elif mode == "TRAIN":
            return self.data.loc[self.idxTrain, :]
        elif mode == "TEST":
            return self.data.loc[self.idxTest, :]
        else:
            raise Exception("Invalid mode")
