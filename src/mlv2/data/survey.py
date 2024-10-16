from typing import Annotated, Any, Dict, List
import pandas as pd
from pydantic import BaseModel, validate_call
from pydantic.functional_validators import AfterValidator
from mlv2.utils import logPipeline, FpBaseModel
from .adaptor import debugCreateAdaptor
from .le import LE


class WAPInfo(BaseModel):
    ssid: str
    bssid: str
    level: int
    frequency: int


class DFValidator(BaseModel):
    dbRowID: str
    zoneName: str
    fingerprint: List[WAPInfo]


def checkDataFrame(df: Any) -> Any:
    def rowFN(row):
        DFValidator.model_validate(row.to_dict())

    df.apply(rowFN, axis=1)
    return df


class Survey(FpBaseModel):
    data: Annotated[pd.DataFrame, AfterValidator(checkDataFrame)]
    ignoredBSSID: List[str] = []

    @logPipeline()
    def model_post_init(self, __context) -> None:
        self.formatBSSID()
        self.formatZoneName()
        self.removeIgnoredBSSID()
        self.removeDuplicatedEntries()

    @logPipeline()
    def formatBSSID(self) -> None:
        def rowFN(fp):
            dft = pd.DataFrame.from_dict(fp)
            dft["bssid"] = dft["bssid"].str.lower().str.strip()
            return dft.to_dict(orient="records")

        self.data["fingerprint"] = self.data["fingerprint"].apply(rowFN)

    @logPipeline()
    def formatZoneName(self) -> None:
        self.data["zoneName"] = self.data["zoneName"].apply(lambda name: name.strip())

    @logPipeline()
    def removeIgnoredBSSID(self):
        def rowFN(fp):
            dft = pd.DataFrame.from_dict(fp)
            matchIgnored = dft["bssid"].isin(self.ignoredBSSID)
            dft = dft[~matchIgnored]
            return dft.to_dict(orient="records")

        self.data["fingerprint"] = self.data["fingerprint"].apply(rowFN)

    @logPipeline()
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

    @logPipeline()
    def getZoneNames(self):
        sr = self.data["zoneName"].sort_values()
        return pd.unique(sr).tolist()

    @logPipeline()
    def getBSSID(self):
        store = []

        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            store.append(dft["bssid"])

        _ = self.data["fingerprint"].apply(rowFn)
        srBssid = pd.concat(store).sort_values().reset_index(drop=True)
        return pd.unique(srBssid).tolist()

    @logPipeline()
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


def debugCreateSurvey():

    ada, pipeline = debugCreateAdaptor()
    survey = Survey(data=ada.data, pipeline=pipeline)
    survey.pipeline.print()
    return survey


if __name__ == "__main__":
    debugCreateSurvey()
