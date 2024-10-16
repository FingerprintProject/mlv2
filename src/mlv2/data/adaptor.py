from typing import Annotated, Any, Dict, Optional
import pandas as pd
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator
from ..utils import logPipeline, FpBaseModel
import pprint


class DFValidator(BaseModel):
    admin_json: Dict


def checkDataFrame(df: Any) -> Any:
    def rowFN(row):
        DFValidator.model_validate(row.to_dict())

    df.apply(rowFN, axis=1)
    return df


class Adaptor(FpBaseModel):
    data: Optional[pd.DataFrame] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    def fit(
        self, data: Annotated[pd.DataFrame, AfterValidator(checkDataFrame)], info={}
    ) -> None:
        self.addInfo(info)

        def extractDataFromJSON(row):
            data = row["admin_json"]
            return pd.Series(data)

        df = data.apply(extractDataFromJSON, axis=1)
        self.data = df.rename(
            columns={"id": "dbRowID", "point": "zoneName", "dataDictAll": "fingerprint"}
        )
