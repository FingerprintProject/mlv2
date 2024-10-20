from typing import Any, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, validate_call
from sklearn.preprocessing import LabelEncoder

from ..utils import FpBaseModel, logPipeline


def checkSeriesFp(sr: Any) -> Any:
    class WAPInfo(BaseModel):
        ssid: str
        bssid: str
        level: int
        frequency: int

    class Val(BaseModel):
        data: List[WAPInfo]

    sr.apply(lambda arr: Val.model_validate({"data": arr}))
    return sr


# There should be an easier way.
def checkSeriesZone(sr: Any) -> Any:
    class Val(BaseModel):
        data: str

    sr.apply(lambda arr: Val.model_validate({"data": arr}))
    return sr


class LE(FpBaseModel):
    encoderType: str = Field(pattern=r"^BSSID$|^ZONE$", default="ZONE")
    model: LabelEncoder = Field(default_factory=LabelEncoder)
    bssidPrefix: str = "W"
    entryList: Optional[List[str]] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call
    def fit(self, data: List[str], info={}):
        self.preventRefit()
        # Create unique list
        sr = pd.Series(data).sort_values()
        self.entryList = pd.unique(sr).tolist()
        # Fit
        self.model.fit(self.entryList)
        self.logger.info(f"Total Item: {len(self.entryList)}")
        self.isFitted = True

    @logPipeline()
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def encode(
        self,
        data: pd.Series,
        fpDict: Any = None,
        ignoreCheck: bool = False,
    ):

        # Validate
        if not ignoreCheck:
            if type(fpDict).__name__ != "FpDict":
                raise Exception("Please use FpDict class instant")

            if self.encoderType == "ZONE":
                checkId = fpDict.id_leZone
                leType = "leZone"
            elif self.encoderType == "BSSID":
                checkId = fpDict.id_leBssid
                leType = "leBssid"

            if checkId != self.uuid:
                raise Exception(
                    f"Please conform FpDict with {leType}-{self.uuid} first to prevent out-of-bag error."
                )

        if self.encoderType == "ZONE":
            checkSeriesZone(data)
            res = self.model.transform(data)
            res = pd.Series(res, index=data.index)  # Return series to maintain index
            return res
        elif self.encoderType == "BSSID":
            checkSeriesFp(data)
            res = self._encodeFp(data)  # Return dataframe
            return res

    def _encodeFp(self, data: pd.DataFrame):

        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            dft = dft[["bssid", "level"]]

            # Change bssid into shorter name
            res = self.model.transform(dft["bssid"])
            sr = pd.Series(res).apply(lambda el: f"{self.bssidPrefix}{el}")
            dft["bssid"] = sr.values.tolist()
            dft = dft.set_index("bssid")
            return dft.to_dict()["level"]

        res = data.apply(rowFn)
        return res
