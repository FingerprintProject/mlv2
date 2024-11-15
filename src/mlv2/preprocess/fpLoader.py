from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validate_call, ConfigDict
from typing_extensions import TypedDict

from ..utils import FpBaseModel, logPipeline

patternInputType = r"^FILE_SUPERVISED$|^FILE^API$|"
patternDataType = r"^SUPERVISED$|^UNSUPERVISED$"
patternApi = r"^PREDICTV1$"


class FpLoaderBase(FpBaseModel):
    data: Optional[pd.DataFrame] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass


# -----------------------------------------------------------#
patternFileType = r"^BIG_QUERY$|^PHP_SERVER$|"
patternDataType = r"^SUPERVISED$|^UNSUPERVISED$|"


class Val_BigQuery(BaseModel):

    class WAP(TypedDict):
        ssid: str
        bssid: str
        level: int
        frequency: int

    id: str
    point: str
    dataDictAll: List[WAP]


class Val_PhpServer(BaseModel):

    class WAP(TypedDict):
        ssid: str
        bssid: str
        level: int
        freq: int

    model_config = ConfigDict(
        extra="allow",
    )
    id: int
    point: str
    dataDictAll: List[WAP]


class FileData(BaseModel):
    fileName: str
    fileType: str = Field(pattern=patternFileType)
    dataType: str = Field(pattern=patternDataType)


class FpLoaderFile(FpLoaderBase):

    @logPipeline()
    @validate_call
    def fit(
        self,
        fileData: List[FileData],
        info: Dict[str, Any] = {},
    ) -> None:

        self.preventRefit()
        dfArr = []
        for fd in fileData:
            fileName = fd.fileName
            fileType = fd.fileType
            dataType = fd.dataType
            df = self.loadFile(fileName, fileType, dataType)
            dfArr.append(df)
        self.data = pd.concat(dfArr).reset_index(drop=True)

        # Generate unique index
        self.data.index = self.getUniqueIdx(idxList=self.data.index.values.tolist())

        self.isFitted = True

    def loadFile(self, fileName, fileType, dataType):

        dft = pd.read_json(fileName, convert_dates=False)
        filtNaN = dft.isna().any(axis=1)
        numNan = filtNaN[filtNaN].shape[0]
        if numNan > 0:
            self.logger.warning(
                f"Dropping {numNan} out of {dft.shape[0]} rows due to NaN detection"
            )
        dft = dft.dropna()

        if fileType == "BIG_QUERY":
            Validator = Val_BigQuery
        elif fileType == "PHP_SERVER":
            Validator = Val_PhpServer
        dft = self.checkDf(dft, Validator)

        if fileType == "PHP_SERVER":
            # Chagne key "freq" to "frequency"
            def rowFn(fp):
                dft = pd.DataFrame.from_dict(fp)
                dft = dft.rename(columns={"freq": "frequency"})
                return dft.to_dict(orient="records")

            dft["dataDictAll"] = dft["dataDictAll"].apply(rowFn)

        dft = dft.rename(columns={"point": "zoneName", "dataDictAll": "fingerprint"})

        if dataType == "UNSUPERVISED":
            dft["zoneName"] = (
                np.nan
            )  # If I use pd.NA, I will have problem with validation because np.nan is float, but pd.NA is its own type.
        dft["id"] = dft["id"].astype(str)
        dft = dft[["id", "zoneName", "fingerprint"]]
        return dft

    def checkDf(self, df: pd.DataFrame, Validator: Any):
        def rowFN(row):
            try:
                Validator.model_validate(row.to_dict())
                return True
            except:
                return False

        filt = df.apply(rowFN, axis=1)
        numRemoved = (~filt).sum()
        if numRemoved > 0:
            self.logger.warning(
                f"Dropping {numRemoved} out of {df.shape[0]} rows due to invalid data"
            )
        df = df[filt]
        if df.shape[0] == 0:
            raise Exception("No data left after validation")
        return df


class FpLoaderApi(FpLoaderBase):

    class API_Schema(TypedDict):
        SSID: str
        BSSID: str
        frequency: int
        level: int

    @validate_call
    def fit(
        self,
        data: List[API_Schema],
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
