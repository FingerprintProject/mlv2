from typing import Annotated, Any, Dict, Optional, List
import pandas as pd
from pydantic import BaseModel, Field, validate_call
from pydantic.functional_validators import AfterValidator
from ..utils import logPipeline, FpBaseModel

pattern = r"SUPV1|^SUPV2$|^UNSUPV1$|^UNSUPV2$"


class FileData(BaseModel):
    filename: str
    fileType: str = Field(pattern=pattern)


class ValSupV2(BaseModel):
    admin_json: Dict


class ValUnsupV1(BaseModel):
    admin_json: Dict


# def checkDf(df: Any, Val: Any) -> Any:
#     def rowFN(row):
#         Val.model_validate(row.to_dict())

#     df.apply(rowFN, axis=1)
#     return df


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
                    pass
                case _:
                    raise Exception("Unknown filetype")
            dfArr.append(df)
        self.data = pd.concat(dfArr).reset_index(drop=True)
        self.isFitted = True

    def checkDf(df: pd.DataFrame, Val: Any):
        def rowFN(row):
            Val.model_validate(row.to_dict())

        df.apply(rowFN, axis=1)

    def loadSupV1(self, filename):

        def extractDataFromJSON(row):
            data = row["admin_json"]
            return pd.Series(data)

        dft = pd.read_json(filename)
        dft = dft.apply(extractDataFromJSON, axis=1)
        dft = dft.rename(
            columns={"id": "dbRowID", "point": "zoneName", "dataDictAll": "fingerprint"}
        )
        return dft
