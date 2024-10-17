from typing import Annotated, Any, Dict, List, Optional, Union
import pandas as pd
from pydantic import BaseModel, validate_call, Field
from pydantic.functional_validators import AfterValidator
from ..utils import logPipeline, FpBaseModel
from .le import LE


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

    def getZoneNamesEncoded(self, le) -> pd.Series:
        if self.dataType != "SUPERVISED":
            raise Exception(
                f"Data is found to be {self.dataType}. getZoneNamesEncoded is only allowed for supervised data"
            )

        sr = self.data["zoneName"]
        srEnc = le.transform(sr)
        return pd.Series(srEnc)

    def getBSSID(self):
        store = []

        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            store.append(dft["bssid"])

        _ = self.data["fingerprint"].apply(rowFn)
        srBssid = pd.concat(store).sort_values().reset_index(drop=True)
        return pd.unique(srBssid).tolist()

    @validate_call
    def genFP(self, le: LE) -> List[Dict[str, int]]:
        """Generate dictionary for corpus builder (key is WX and value is level)"""

        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            dft = dft[["bssid", "level"]]
            # Change bssid into shorter name
            dft["bssid"] = le.transform(dft["bssid"])
            dft = dft.set_index("bssid")
            return dft.to_dict()["level"]

        res = self.data["fingerprint"].apply(rowFn)
        return res.values
