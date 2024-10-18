from typing import Any, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field

from ..utils import FpBaseModel, logPipeline


class WAPInfo(BaseModel):
    ssid: str
    bssid: str
    level: int
    frequency: int


class DFValidator(BaseModel):
    id: str
    zoneName: Union[str, float]
    fingerprint: List[WAPInfo]


def checkDF(df: Any) -> Any:
    def rowFN(row):
        DFValidator.model_validate(row.to_dict())

    df.apply(rowFN, axis=1)
    return df


class FpDict(FpBaseModel):
    data: Optional[pd.DataFrame] = None
    ignoredBSSID: List[str] = []
    dataType: str = Field(pattern=r"^SUPERVISED$|^UNSUPERVISED$|^MIXED$", default="")

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    def fit(self, data: pd.DataFrame, info={}) -> None:
        checkDF(data)
        self.preventRefit()
        self.data = data
        self.determineDataType()
        self.formatBSSID()
        self.formatZoneName()
        self.removeIgnoredBSSID()
        self.removeDuplicatedEntries()
        self.isFitted = True

    def determineDataType(self):
        numTot = self.data.shape[0]
        filt = ~self.data["zoneName"].isna()
        numSup = filt[filt].shape[0]
        numUnsup = filt[~filt].shape[0]
        if numSup == numTot:
            self.dataType = "SUPERVISED"
        elif numUnsup == numTot:
            self.dataType = "UNSUPERVISED"
        else:
            self.dataType = "MIXED"

    def formatBSSID(self) -> None:
        def rowFN(fp):
            dft = pd.DataFrame.from_dict(fp)
            dft["bssid"] = dft["bssid"].str.lower().str.strip()
            return dft.to_dict(orient="records")

        self.data["fingerprint"] = self.data["fingerprint"].apply(rowFN)

    def formatZoneName(self) -> None:
        filt = ~self.data["zoneName"].isna()
        idx = filt[filt].index.values
        self.data.loc[idx, "zoneName"] = self.data.loc[idx, "zoneName"].apply(
            lambda name: name.strip()
        )

    def removeIgnoredBSSID(self):
        def rowFN(fp):
            dft = pd.DataFrame.from_dict(fp)
            matchIgnored = dft["bssid"].isin(self.ignoredBSSID)
            dft = dft[~matchIgnored]
            return dft.to_dict(orient="records")

        self.data["fingerprint"] = self.data["fingerprint"].apply(rowFN)

    def removeDuplicatedEntries(self):
        def rowFN(fp):
            dft = pd.DataFrame.from_dict(fp)
            dataDict = dft[["bssid", "level"]].set_index("bssid").sort_index().to_json()
            return dataDict

        dft = self.data[["zoneName", "fingerprint"]].copy()
        dft["fingerprint"] = dft["fingerprint"].apply(rowFN)
        filtDup = dft.duplicated()
        if filtDup.any():
            self.logger.warning(f"Found {filtDup.sum()} duplicated row(s) in data.")

        self.data = self.data[~filtDup]

    def getUniqueZoneNames(self) -> List[str]:
        if self.dataType != "SUPERVISED":
            raise Exception(
                f"Data is found to be {self.dataType}. getUniqueZoneNames is only allowed for supervised data"
            )
        sr = self.data["zoneName"].sort_values()
        return pd.unique(sr).tolist()

    def getZoneNames(self) -> pd.Series:
        if self.dataType != "SUPERVISED":
            raise Exception(
                f"Data is found to be {self.dataType}. getZoneNames is only allowed for supervised data"
            )
        return self.data["zoneName"]

    def getUniqueBSSID(self):
        store = []

        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            store.append(dft["bssid"])

        _ = self.data["fingerprint"].apply(rowFn)
        srBssid = pd.concat(store).sort_values().reset_index(drop=True)
        return pd.unique(srBssid).tolist()

    def getFp(self) -> pd.Series:
        return self.data["fingerprint"]
