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


class WAPInfo(TypedDict):
    ssid: str
    bssid: str
    level: int
    frequency: int


class SupV2_Dict(TypedDict):
    id: str
    point: str
    dataDictAll: List[WAPInfo]


class SupV2_Val(BaseModel):
    admin_json: SupV2_Dict


class UnsupV1_Val(BaseModel):
    id: int
    scanIdx: int
    point: str
    site: str
    device: str
    timestamp: int
    building: str
    dataDictAll: List[WAPInfo]


class Loader(FpBaseModel):
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

        print(fileData)
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
        self.isFitted = True

    def checkDf(self, df: pd.DataFrame, Val: Any):
        def rowFN(row):
            Val.model_validate(row.to_dict())

        df.apply(rowFN, axis=1)

    def loadSupV1(self, filename):

        def extractDataFromJSON(row):
            data = row["admin_json"]

            return pd.Series(data)

        dft = pd.read_json(filename)
        self.checkDf(dft, SupV2_Val)
        dft = dft.apply(extractDataFromJSON, axis=1)
        dft = dft.rename(
            columns={"id": "dbRowID", "point": "zoneName", "dataDictAll": "fingerprint"}
        )
        return dft

    def loadUnsupV1(self, filename):

        dft = pd.read_json(filename, convert_dates=False)
        self.checkDf(dft, UnsupV1_Val)
        pass
