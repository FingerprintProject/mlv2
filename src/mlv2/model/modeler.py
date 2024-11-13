from typing import Optional, Any
import numpy as np
import pandas as pd
from pydantic import validate_call
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from mlv2.preprocess import LE
from ..utils import FpBaseModel, logPipeline


class Model(FpBaseModel):
    clf: Optional[Any] = None
    id_vectorizer: Optional[str] = None
    id_leBssid: Optional[str] = None
    id_leZone: Optional[str] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    def calculateMetrices(
        self,
        X_test,
        y_test,
        info={},
    ):
        if self.clf is None:
            raise Exception("No classifier")

        y_pred = self.clf.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        dfReport = pd.DataFrame(report).transpose()

        filt = dfReport.iloc[:-3, :]["f1-score"] < 0.9
        dfProblem = dfReport.iloc[:-3, :][filt].sort_values

        return dfReport, dfProblem

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def predict(self, X: pd.DataFrame, leZone: LE):

        if leZone.uuid != self.id_leZone:
            raise Exception("Wrong leZone id")

        y_prob = self.clf.predict_proba(X)
        dfp = pd.DataFrame({"label": self.clf.classes_, "probability": y_prob[0]})
        dfp = dfp.sort_values(by=["probability"], ascending=False)
        dfp = dfp.iloc[:10, :]
        dfp["probability"] = dfp["probability"].apply(lambda p: round(p * 100, 2))
        dfp["zoneName"] = leZone.inverse_transform(dfp["label"])

        # Append external reference
        if leZone.extRef is not None:
            dfp = dfp.merge(
                leZone.extRef, left_on="zoneName", right_on="entry", how="left"
            ).drop(columns=["entry"])
            pass
        else:
            dfp["ref"] = np.nan
        return dfp

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


class ModelLr(Model):

    clf: Optional[GridSearchCV] = None

    @logPipeline()
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        info={},
    ):
        pipe = Pipeline([("scaler", StandardScaler()), ("lr", LogisticRegression())])
        params_grid = {"lr__C": [0.01, 0.1, 1, 10, 100]}
        gs = GridSearchCV(
            estimator=pipe, param_grid=params_grid, cv=5, scoring="f1_micro"
        )
        gs.fit(X_train, y_train)
        self.clf = gs

        cvResult = pd.DataFrame(gs.cv_results_)
        return cvResult
