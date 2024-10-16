import pprint
from typing import List
import pandas as pd
from pydantic import Field
from sklearn.preprocessing import LabelEncoder
from mlv2.utils import logPipeline, FpBaseModel


class LE(FpBaseModel):
    data: List[str]
    encoderType: str = Field(pattern=r"^BSSID$|^NORMAL$", default="NORMAL")
    model: LabelEncoder = Field(default_factory=LabelEncoder)
    bssidPrefix: str = "W"

    @logPipeline()
    def model_post_init(self, __context) -> None:
        self.createUniqueSet()
        self.fit()

    @logPipeline()
    def createUniqueSet(self):
        sr = pd.Series(self.data).sort_values()
        self.data = pd.unique(sr)
        self.logger.info(f"Total Item: {len(self.data)}")

    @logPipeline()
    def fit(self):
        self.model.fit(self.data)

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
