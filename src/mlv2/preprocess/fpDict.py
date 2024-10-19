from typing import Any, List, Optional, Union
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from ..utils import FpBaseModel, logPipeline
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
    id_leBssid: Optional[str] = None
    id_leZone: Optional[str] = None

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

    def conform_to_le(self, le: LE):
        """
        1) Make remove bssid not found in "bssid" label encoder
        2) Remove fingerprints with zone not found in "zone" label encoder.
        """
        if le.encoderType == "BSSID":
            if self.id_leBssid:
                raise Exception(f"Already conform to leBSSID {self.id_leBssid}")
            res = self.conform_to_le_bssid(le)
            self.id_leBssid = le.uuid
        elif le.encoderType == "ZONE":
            if self.id_leZone:
                raise Exception(f"Already conform to leZone {self.id_leZone}")
            res = self.conform_to_le_zone(le)
            self.id_leZone = le.uuid
        return res

    def conform_to_le_bssid(self, le: LE):
        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            bssid = dft["bssid"]

            # Filter unseen bssid
            filt = bssid.apply(lambda el: el not in le.entryList)
            dftFiltered = dft[~filt]

            # Check if we need to disregard this fingerprint or not
            isEmpty = True if dftFiltered.shape[0] == 0 else False

            # Keep the unknown WAP for future processing
            unknownWAP = dft.loc[filt.index, ["bssid", "ssid"]]

            out = dict(
                fingerprint=dftFiltered.to_dict(orient="records"),
                isEmpty=isEmpty,
                unknownWAP=unknownWAP,
            )
            return pd.Series(out)

        res = self.data["fingerprint"].apply(rowFn)

        # Combined all unknown WAPs and removing duplicates
        dfUnknownWAP = pd.concat(res["unknownWAP"].values)
        filtDup = dfUnknownWAP.duplicated()
        dfUnknownWAP = dfUnknownWAP[~filtDup]

        # Remove fingerprints with zero entries
        self.data = self.data[~res.isEmpty]

        # Logging
        if dfUnknownWAP.shape[0] > 0:
            self.logger.info(
                f"Found {dfUnknownWAP.shape[0]} unknown WAPs in fingerprints. Ex: {dfUnknownWAP["ssid"].values[:10]}"
            )
        rowTotal = res.isEmpty.shape[0]
        rowRemoved = res.isEmpty[res.isEmpty].shape[0]
        self.logger.info(
            f"Remove {rowRemoved} out of {rowTotal} rows. Remaining rows: {rowTotal-rowRemoved}"
        )

        return dfUnknownWAP

    def conform_to_le_zone(self, le: LE):
        srZoneName = self.data["zoneName"]

        # Filter fingerprint with known zonenames
        filtKeep = srZoneName.isin(le.entryList)
        self.data = self.data[filtKeep]

        # Keep track of unkwonw zone names
        srUnknownZoneName = srZoneName[~filtKeep]
        srUnknownZoneName = pd.Series(pd.unique(srUnknownZoneName))

        # Logging
        if srUnknownZoneName.shape[0] > 0:
            self.logger.warning(
                f"Remove {srUnknownZoneName.shape[0]} unknown zones entries. Ex: {srUnknownZoneName.values[:10]}"
            )
        rowTotal = filtKeep.shape[0]
        rowRemoved = filtKeep[~filtKeep].shape[0]
        if rowRemoved > 0:
            self.logger.info(
                f"Remove {rowRemoved} out of {rowTotal} rows. Remaining rows: {rowTotal-rowRemoved}"
            )
        return srUnknownZoneName
