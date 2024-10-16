from typing import Annotated, Any, Dict
import pandas as pd
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator
from mlv2.utils import Pipeline, logPipeline, FpBaseModel


class DFValidator(BaseModel):
    admin_json: Dict


def checkDataFrame(df: Any) -> Any:
    def rowFN(row):
        DFValidator.model_validate(row.to_dict())

    df.apply(rowFN, axis=1)
    return df


class Adaptor(FpBaseModel):
    data: Annotated[pd.DataFrame, AfterValidator(checkDataFrame)]

    @logPipeline()
    def model_post_init(self, __context) -> None:
        self.run()

    @logPipeline()
    def run(self) -> None:

        def extractDataFromJSON(row):
            data = row["admin_json"]
            return pd.Series(data)

        df = self.data.apply(extractDataFromJSON, axis=1)
        self.data = df.rename(
            columns={"id": "dbRowID", "point": "zoneName", "dataDictAll": "fingerprint"}
        )


def debugCreateAdaptor():

    # filename = "surveys/admin_json_hospital_id_15.json"
    filename = "surveys/admin_json_hospital_id_15_small.json"
    # filename = "surveys/admin_json_hospital_id_15_error.json"

    df = pd.read_json(filename)
    pipeline = Pipeline()
    ada = Adaptor(data=df, pipeline=pipeline)

    print(ada.data)
    return ada, pipeline


if __name__ == "__main__":
    debugCreateAdaptor()
