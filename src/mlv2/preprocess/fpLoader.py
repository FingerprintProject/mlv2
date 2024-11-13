from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validate_call
from typing_extensions import TypedDict

from ..utils import FpBaseModel, logPipeline

patternFile = r"^SUPV1$|^SUPV2$|^UNSUPV1$|^UNSUPV2$|"
patternApi = r"^PREDICTV1$"


class FileData(BaseModel):
    filename: str
    fileType: str = Field(pattern=patternFile)


class File_WAPInfoV2(TypedDict):
    ssid: str
    bssid: str
    level: int
    frequency: int


class File_SupV2_Dict(TypedDict):
    id: str
    point: str
    dataDictAll: List[File_WAPInfoV2]


class File_SupV2_Val(BaseModel):
    admin_json: File_SupV2_Dict


class File_WAPInfoV1(TypedDict):
    ssid: str
    bssid: str
    level: int
    freq: int


class File_UnsupV1_Val(BaseModel):
    id: int
    scanIdx: int
    point: str
    site: str
    device: str
    timestamp: int
    building: str
    dataDictAll: List[File_WAPInfoV1]


class Api_PredictV1(TypedDict):
    SSID: str
    BSSID: str
    frequency: int
    level: int


class FpLoader(FpBaseModel):
    data: Optional[pd.DataFrame] = None
    fileType: str = Field(pattern=patternFile, default="")

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call
    def fitFromFile(
        self,
        fileData: List[FileData],
        info: Dict[str, Any] = {},
    ) -> None:

        self.preventRefit()
        dfArr = []
        for fd in fileData:
            filename = fd.filename
            fileType = fd.fileType
            match fileType:
                case "SUPV2":
                    df = self.loadFileSupV1(filename)
                case "UNSUPV1":
                    df = self.loadFileUnsupV1(filename)
                case _:
                    raise Exception("Unknown filetype")
            dfArr.append(df)
        self.data = pd.concat(dfArr).reset_index(drop=True)

        # Generate unique index
        self.data.index = self.getUniqueIdx(idxList=self.data.index.values.tolist())

        self.isFitted = True

    @validate_call
    def fitFromApi(
        self,
        data: List[Api_PredictV1],
        info: Dict[str, Any] = {},
    ):
        dft = pd.DataFrame.from_dict(data)
        dft = dft.rename(columns={"SSID": "ssid", "BSSID": "bssid"})

        dataTmp = dict(
            id="api", zoneName=np.nan, fingerprint=dft.to_dict(orient="records")
        )
        dftOut = pd.DataFrame.from_dict([dataTmp])
        self.data = dftOut
        self.data.index = self.getUniqueIdx(idxList=self.data.index.values.tolist())
        self.isFitted = True

    def checkDf(self, df: pd.DataFrame, Val: Any):
        def rowFN(row):
            Val.model_validate(row.to_dict())

        df.apply(rowFN, axis=1)

    def loadFileSupV1(self, filename):

        def extractDataFromJSON(row):
            data = row["admin_json"]

            return pd.Series(data)

        dft = pd.read_json(filename, convert_dates=False)
        self.checkDf(dft, File_SupV2_Val)
        dft = dft.apply(extractDataFromJSON, axis=1)
        dft = dft.rename(columns={"point": "zoneName", "dataDictAll": "fingerprint"})
        dft = dft[["id", "zoneName", "fingerprint"]]
        return dft

    def loadFileUnsupV1(self, filename):

        dft = pd.read_json(filename, convert_dates=False)
        filtNaN = dft.isna().any(axis=1)
        numNan = filtNaN[filtNaN].shape[0]
        if numNan > 0:
            self.logger.warning(
                f"Dropping {numNan} out of {dft.shape[0]} rows due to NaN detection"
            )
        dft = dft.dropna()
        self.checkDf(dft, File_UnsupV1_Val)

        # Chagne key "freq" to "frequency"
        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            dft = dft.rename(columns={"freq": "frequency"})
            return dft.to_dict(orient="records")

        dft["dataDictAll"] = dft["dataDictAll"].apply(rowFn)
        dft = dft.rename(columns={"point": "zoneName", "dataDictAll": "fingerprint"})
        dft["zoneName"] = (
            np.nan
        )  # If I use pd.NA, I will have problem with validation because np.nan is float, but pd.NA is its own type.
        dft["id"] = dft["id"].astype(str)
        dft = dft[["id", "zoneName", "fingerprint"]]
        return dft
