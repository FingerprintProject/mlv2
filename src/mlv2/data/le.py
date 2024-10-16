import pprint
from typing import List, Optional
import pandas as pd
from pydantic import Field, validate_call
from sklearn.preprocessing import LabelEncoder
from ..utils import logPipeline, FpBaseModel


class LE(FpBaseModel):
    encoderType: str = Field(pattern=r"^BSSID$|^NORMAL$", default="NORMAL")
    model: LabelEncoder = Field(default_factory=LabelEncoder)
    bssidPrefix: str = "W"
    surveyId: Optional[str] = None
    nameList: Optional[pd.Series] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call
    def fit(self, data: List[str], surveyId: str):

        if self.surveyId:
            raise Exception(f"Already call fit data from {self.surveyId}.")

        # Create unique list
        sr = pd.Series(data).sort_values()
        self.nameList = pd.unique(sr)
        # Fit
        self.model.fit(self.nameList)
        self.surveyId = surveyId
        self.logger.info(f"Total Item: {len(self.nameList)}")

    # @logPipeline()
    def transform(self, arr: List[str]):
        if self.encoderType == "NORMAL":
            return self.model.transform(arr)
        elif self.encoderType == "BSSID":
            res = self.model.transform(arr)
            sr = pd.Series(res).apply(lambda el: f"{self.bssidPrefix}{el}")
            return sr.values.tolist()


def debugCreateLE():

    strArr = ["A", "A", "B", "B", "C"]
    le1 = LE(data=strArr)
    pprint.pp(le1.data)
    pprint.pp(le1.transform(strArr))

    le2 = LE(data=strArr, encoderType="BSSID")
    pprint.pp(le2.data)
    pprint.pp(le2.transform(strArr))


if __name__ == "__main__":
    debugCreateLE()
