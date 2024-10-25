from typing import Annotated, Any, Dict, Optional, List
from typing_extensions import TypedDict
import pandas as pd
from pydantic import BaseModel, Field, validate_call
from pydantic.functional_validators import AfterValidator
from ..utils import logPipeline, FpBaseModel

pattern = r"SUPV1|^SUPV2$|^UNSUPV1$|^UNSUPV2$"


class FileData(BaseModel):
    filename: str
    fileType: str = Field(pattern=pattern)


class WAPInfoV2(TypedDict):
    ssid: str
    bssid: str
    level: int
    frequency: int


class SupV2_Dict(TypedDict):
    id: str
    point: str
    dataDictAll: List[WAPInfoV2]


class SupV2_Val(BaseModel):
    admin_json: SupV2_Dict


class WAPInfoV1(TypedDict):
    ssid: str
    bssid: str
    level: int
    freq: int


class UnsupV1_Val(BaseModel):
    id: int
    scanIdx: int
    point: str
    site: str
    device: str
    timestamp: int
    building: str
    dataDictAll: List[WAPInfoV1]


class FpLoader(FpBaseModel):
    data: Optional[pd.DataFrame] = None
    fileType: str = Field(pattern=pattern, default="")

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

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
            filename = fd.filename
            fileType = fd.fileType
            match fileType:
                case "SUPV2":
                    df = self.loadSupV1(filename)
                case "UNSUPV1":
                    df = self.loadUnsupV1(filename)
                case _:
                    raise Exception("Unknown filetype")
            dfArr.append(df)
        self.data = pd.concat(dfArr).reset_index(drop=True)

        # Generate unique index
        self.data.index = (
            self.uuid[:4] + "_" + pd.Series(self.data.index.values).astype(str)
        )
        self.isFitted = True

    def checkDf(self, df: pd.DataFrame, Val: Any):
        def rowFN(row):
            Val.model_validate(row.to_dict())

        df.apply(rowFN, axis=1)

    def loadSupV1(self, filename):

        def extractDataFromJSON(row):
            data = row["admin_json"]

            return pd.Series(data)

        dft = pd.read_json(filename, convert_dates=False)
        self.checkDf(dft, SupV2_Val)
        dft = dft.apply(extractDataFromJSON, axis=1)
        dft = dft.rename(columns={"point": "zoneName", "dataDictAll": "fingerprint"})
        dft = dft[["id", "zoneName", "fingerprint"]]
        return dft

    def loadUnsupV1(self, filename):

        dft = pd.read_json(filename, convert_dates=False)
        filtNaN = dft.isna().any(axis=1)
        numNan = filtNaN[filtNaN].shape[0]
        if numNan > 0:
            self.logger.warning(
                f"Dropping {numNan} out of {dft.shape[0]} rows due to NaN detection"
            )
        dft = dft.dropna()
        self.checkDf(dft, UnsupV1_Val)

        # Chagne key "freq" to "frequency"
        def rowFn(fp):
            dft = pd.DataFrame.from_dict(fp)
            dft = dft.rename(columns={"freq": "frequency"})
            return dft.to_dict(orient="records")

        dft["dataDictAll"] = dft["dataDictAll"].apply(rowFn)
        dft = dft.rename(columns={"point": "zoneName", "dataDictAll": "fingerprint"})
        dft["zoneName"] = pd.NA
        dft["id"] = dft["id"].astype(str)
        dft = dft[["id", "zoneName", "fingerprint"]]
        return dft
