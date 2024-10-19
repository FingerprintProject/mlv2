from typing import Any, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, validate_call
from sklearn.preprocessing import LabelEncoder

from ..utils import FpBaseModel, logPipeline


class WAPInfo(BaseModel):
    ssid: str
    bssid: str
    level: int
    frequency: int


class SeriesValidator(BaseModel):
    fingerprint: List[WAPInfo]


def checkSeries(sr: Any) -> Any:
    sr.apply(lambda arr: SeriesValidator.model_validate({"fingerprint": arr}))
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
    def encode(self, data: Union[List[str], pd.Series]):

        # Validate
        if isinstance(data, str) and self.encoderType != "ZONE":
            raise Exception("Data input should be dataFrame")
        elif isinstance(data, pd.Series) and self.encoderType != "BSSID":
            raise Exception("Data input should be list of string")

        # Make sure pandas series is of the right shape
        if isinstance(data, pd.Series):
            checkSeries(data)

        if self.encoderType == "ZONE":
            return self.encodeZone(data)
        elif self.encoderType == "BSSID":
            return self.encodeFp(data)

    def encodeZone(self, data: str):
        sr = pd.Series(data)
        srEnc = self.transform(sr)
        return srEnc

    def encodeFp(self, data: pd.DataFrame):
        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            dft = dft[["bssid", "level"]]

            # Filter unseen bssid
            filt = dft["bssid"].apply(lambda el: el not in self.entryList)
            num = filt[filt].shape[0]
            filtBssids = dft["bssid"][filt].values.tolist()
            filtBssidsStr = ", ".join(filtBssids)
            if num > 0:
                self.logger.warning(f"Detect unknown BSSID: {filtBssidsStr}")
            dft = dft[~filt]

            # Check if the dataframe is empty after filtering
            if dft.shape[0] == 0:
                raise Exception("Empty dataframe after filtering")

            # Change bssid into shorter name
            res = self.model.transform(dft["bssid"])
            sr = pd.Series(res).apply(lambda el: f"{self.bssidPrefix}{el}")
            dft["bssid"] = sr.values.tolist()
            dft = dft.set_index("bssid")
            return dft.to_dict()["level"]

        res = data.apply(rowFn)
        return res.values
