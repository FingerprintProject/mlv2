from typing import Optional, Any

import pandas as pd
from pydantic import validate_call
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ..utils import FpBaseModel, logPipeline


class Model(FpBaseModel):
    clf: Optional[Any] = None

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
