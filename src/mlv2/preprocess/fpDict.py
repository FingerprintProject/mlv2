from typing import Any, List, Optional, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from typing_extensions import Annotated

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
    ignoredBssid: List[str] = []
    dataType: str = Field(pattern=r"^SUPERVISED$|^UNSUPERVISED$|^MIXED$", default="")
    id_leBssid: Optional[str] = None
    id_leZone: Optional[str] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    def fit(self, data: pd.DataFrame, ignoredBssid=[], info={}) -> None:
        checkDF(data)
        self.preventRefit()
        self.data = data
        self.determineDataType()
        self.formatBssid()
        self.formatZoneName()
        self.ignoredBssid = ignoredBssid
        self.removeIgnoredBssid()
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

    def formatBssid(self) -> None:
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

    def removeIgnoredBssid(self):
        self._remove_bssid_from_fp(
            mode="EXCLUDE_FROM_IGNORED_LIST",
            bssidList=self.ignoredBssid,
            operation="removeIgnoredBSSID",
        )

    def _remove_bssid_from_fp(
        self,
        mode: Annotated[
            str, Field(pattern=r"^INCLUDE_FROM_KNOWN_LIST$|^EXCLUDE_FROM_IGNORED_LIST$")
        ],
        bssidList: List[str],
        operation,
    ):
        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            bssid = dft["bssid"]

            # Filter
            if mode == "INCLUDE_FROM_KNOWN_LIST":
                filtRemoved = ~bssid.isin(bssidList)
            elif mode == "EXCLUDE_FROM_IGNORED_LIST":
                filtRemoved = bssid.isin(bssidList)
            else:
                raise Exception("Unknown mode")

            removedWAP = dft[filtRemoved][["bssid", "ssid"]]

            dftNew = dft[~filtRemoved]

            # Check if we need to disregard this fingerprint or not
            isEmpty = True if dftNew.shape[0] == 0 else False

            out = dict(
                fingerprint=dftNew.to_dict(orient="records"),
                isEmpty=isEmpty,
                removedWAP=removedWAP,
            )
            return pd.Series(out)

        res = self.data["fingerprint"].apply(rowFn)

        # Combined all removed WAPs and removing duplicates
        dfRemovedWAP = pd.concat(res["removedWAP"].values)
        filtDup = dfRemovedWAP.duplicated()
        dfRemovedWAP = dfRemovedWAP[~filtDup]

        # Logging
        if dfRemovedWAP.shape[0] > 0:
            self.logger.info(
                f"{operation}: Removed {dfRemovedWAP.shape[0]} WAPs from fingerprints. Ex: {dfRemovedWAP["ssid"].values[:10]}"
            )

        # Remove fingerprints with zero entries
        self._filter(filterRemove=res.isEmpty, operation=operation)

        return dfRemovedWAP

    @logPipeline()
    def _filter(self, filterRemove: pd.Series, operation: str):
        """Filter should be boolean where the True signify removing the corresponding row."""
        # Remove fingerprints with zero entries
        self.data = self.data[~filterRemove]

        nTot = filterRemove.shape[0]
        nRemoved = filterRemove.sum()
        nRemained = (~filterRemove).sum()
        # Logging
        self.logger.info(
            f"{operation}: Remove {nRemoved} out of {nTot} rows. Remaining rows: {nRemained}"
        )

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

    @logPipeline()
    def conform_to_le(self, le: LE):
        """
        1) Make remove bssid not found in "bssid" label encoder
        2) Remove fingerprints with zone not found in "zone" label encoder.
        """
        if le.encoderType == "BSSID":
            if self.id_leBssid:
                raise Exception(f"Already conform to leBSSID {self.id_leBssid}")
            res = self._remove_bssid_from_fp(
                mode="INCLUDE_FROM_KNOWN_LIST",
                bssidList=le.entryList,
                operation="conform_to_leBssid",
            )
            self.id_leBssid = le.uuid
        elif le.encoderType == "ZONE":
            if self.id_leZone:
                raise Exception(f"Already conform to leZone {self.id_leZone}")
            res = self._conform_to_le_zone(le)
            self.id_leZone = le.uuid
        return res

    def _conform_to_le_zone(self, le: LE):
        srZoneName = self.data["zoneName"]

        # Filter fingerprint with known zonenames
        filtRemove = ~srZoneName.isin(le.entryList)

        # Keep track of unknown zone names
        srUnknownZoneName = srZoneName[filtRemove]
        srUnknownZoneName = pd.Series(pd.unique(srUnknownZoneName))

        # Logging
        if srUnknownZoneName.shape[0] > 0:
            self.logger.warning(
                f"Remove {srUnknownZoneName.shape[0]} unknown zones entries. Ex: {srUnknownZoneName.values[:10]}"
            )

        # Filtering fingerprint
        self._filter(filterRemove=filtRemove, operation="conform_to_leZone")

        return srUnknownZoneName
