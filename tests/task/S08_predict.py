from pprint import pp

from mlv2.model import ModelLr
from mlv2.preprocess import FpDict, FpLoader
from mlv2.vectorize import FpVectUnsupervised

from .S00_common import hospitalId, setupTask
from .S00_data import data_normal_1, data_outside


# data = data_outside
data = data_normal_1


def predict():
    pl, lg, saver, loader = setupTask(hospitalId=hospitalId, modelName="S07")

    # Load models
    loader.fitFromModelName(name="S07")
    modelLr: ModelLr = loader.pick(["ModelLr_"])
    leBssid = loader.pick([modelLr.id_leBssid])
    w2v = loader.pick([modelLr.id_vectorizer])
    leZone = loader.pick([modelLr.id_leZone])

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
    pp(output)

    pass
