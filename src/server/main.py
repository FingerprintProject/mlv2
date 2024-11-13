import datetime
from typing import List
from functools import lru_cache
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict

from mlv2.model import ModelLr
from mlv2.preprocess import FpDict, FpLoader
from mlv2.vectorize import FpVectUnsupervised
from server.utils.common import PREDEFINED_TOKEN_HASH, hashString
from server.utils.setup import setupTask


class WifiRadiation(BaseModel):
    SSID: str
    BSSID: str
    frequency: int
    level: int


class Fingerprint(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat()},  # Ensures RFC 3339 format
    )
    timestamp: datetime.datetime
    wifiRadiations: List[WifiRadiation]


class FingerprintStruct(BaseModel):
    hospitalID: int
    fingerprint: Fingerprint
    # point_expected: str
    # is_excluded: bool
    # save_data: bool
    # environment: str  # "production" or "development"
    # fingerprint_id: str
    # remark: Optional[str] = None  # Nullable (in normal case) or "DUPLICATED_FP"
    # fp_key_alter: bool


@lru_cache
def serverLoadModel(hospitalId):

    pl, lg, _, loader = setupTask(hospitalId=hospitalId, modelName="S07")

    # Load models
    loader.fitFromModelName(name="S07")
    modelLr: ModelLr = loader.pick(["ModelLr_"])
    leBssid = loader.pick([modelLr.id_leBssid])
    w2v = loader.pick([modelLr.id_vectorizer])
    leZone = loader.pick([modelLr.id_leZone])

    return pl, lg, leBssid, w2v, leZone, modelLr


app = FastAPI()


@app.get("/")
def home():
    return {"Hello": "World"}


@app.post("/prediction")
def prediction(
    request: Request, payload: FingerprintStruct, Authorization: str = Header(...)
):
    # Token validation
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid token format")

    token = Authorization.split("Bearer ")[1]
    hashed_token = hashString(token)

    if hashed_token != PREDEFINED_TOKEN_HASH:
        raise HTTPException(status_code=401, detail="Invalid token")

    dataArr = payload.fingerprint.wifiRadiations
    data = [d.__dict__ for d in dataArr]
    hospitalId = payload.hospitalID

    pl, lg, leBssid, w2v, leZone, modelLr = serverLoadModel(hospitalId)

    # Load API data
    fpLoader = FpLoader(pipeline=pl, logger=lg)
    fpLoader.fitFromApi(data=data)

    # Preprocess
    fpDict = FpDict(pipeline=pl, logger=lg)
    fpDict.fit(data=fpLoader.data, info=dict(src=fpLoader.uuid))

    # Conformation
    fpDict.conform_to_le(leBssid)

    # Vectorize (supervised)
    fpEncode = leBssid.encode(fpDict.getFp(), fpDict=fpDict)

    X = w2v.vectorize(data=fpEncode, fpDict=fpDict)

    fpVectUnsup = FpVectUnsupervised(pipeline=pl, logger=lg)
    fpVectUnsup.fit(
        XArr=[X],
        id_vectorizer=w2v.uuid,
        id_leBssid=leBssid.uuid,
        info=dict(fpDict=fpDict.uuid),
    )

    res = modelLr.predict(X=fpVectUnsup.data, leZone=leZone)

    resOut = res.rename(
        columns={"zoneName": "hospitalZoneName", "ref": "hospitalZoneID"}
    )
    resOut = resOut.drop(columns="label")
    output = dict(
        predictions=resOut.to_dict(orient="records"),
        error=None,
        warning=None,
        modelId=modelLr.uuid,
    )
    return output


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
