from pprint import pp

from mlv2.model import ModelLr
from mlv2.preprocess import FpDict, FpLoader
from mlv2.vectorize import FpVectUnsupervised

from .S00_common import hospitalId, setupTask

data = [
    {
        "SSID": "CRH-Guest",
        "BSSID": "9c:d5:7d:06:57:62",
        "frequency": 2412,
        "level": -40,
    },
    {"SSID": "CRH-IOT", "BSSID": "9c:d5:7d:06:57:63", "frequency": 2412, "level": -40},
    {
        "SSID": ".@ TRUEWIFI",
        "BSSID": "2c:1a:05:02:86:6f",
        "frequency": 5200,
        "level": -43,
    },
    {
        "SSID": ".@ TrueMove H",
        "BSSID": "2c:1a:05:02:86:6e",
        "frequency": 5200,
        "level": -44,
    },
    {"SSID": "CRH-WiFi", "BSSID": "9c:d5:7d:06:57:6f", "frequency": 5180, "level": -46},
    {
        "SSID": "CRH-Guest",
        "BSSID": "9c:d5:7d:06:57:6d",
        "frequency": 5180,
        "level": -46,
    },
    {
        "SSID": "CRH-Staff",
        "BSSID": "9c:d5:7d:06:57:6e",
        "frequency": 5180,
        "level": -46,
    },
    {
        "SSID": "CRH-Guest",
        "BSSID": "9c:d5:7d:06:4d:c2",
        "frequency": 2437,
        "level": -48,
    },
    {"SSID": "CRH-IOT", "BSSID": "9c:d5:7d:06:4d:c3", "frequency": 2437, "level": -48},
    {
        "SSID": "CRH-Staff",
        "BSSID": "9c:d5:7d:06:4d:ce",
        "frequency": 5500,
        "level": -49,
    },
    {"SSID": "CRH-WiFi", "BSSID": "9c:d5:7d:06:4d:cf", "frequency": 5500, "level": -49},
    {
        "SSID": "CRH-Guest",
        "BSSID": "9c:d5:7d:06:4d:cd",
        "frequency": 5500,
        "level": -49,
    },
    {
        "SSID": ".@ TRUEWIFI",
        "BSSID": "34:5d:a8:25:35:af",
        "frequency": 5620,
        "level": -55,
    },
    {
        "SSID": ".@ TrueMove H",
        "BSSID": "34:5d:a8:25:35:ae",
        "frequency": 5620,
        "level": -56,
    },
    {
        "SSID": ".@ TRUEWIFI",
        "BSSID": "00:df:1d:70:94:80",
        "frequency": 2462,
        "level": -67,
    },
    {
        "SSID": ".@ TrueMove H",
        "BSSID": "00:df:1d:70:94:81",
        "frequency": 2462,
        "level": -69,
    },
    {
        "SSID": "CRH-Guest",
        "BSSID": "9c:d5:7d:03:bb:ed",
        "frequency": 5745,
        "level": -70,
    },
    {"SSID": "CRH-WiFi", "BSSID": "9c:d5:7d:03:bb:ef", "frequency": 5745, "level": -71},
    {
        "SSID": "CRH-Staff",
        "BSSID": "9c:d5:7d:03:bb:ee",
        "frequency": 5745,
        "level": -71,
    },
    {"SSID": "CRH-IOT", "BSSID": "9c:d5:7d:03:bb:e3", "frequency": 2412, "level": -75},
    {
        "SSID": "CRH-Guest",
        "BSSID": "9c:d5:7d:03:bb:e2",
        "frequency": 2412,
        "level": -75,
    },
    {"SSID": "CRH-IOT", "BSSID": "9c:d5:7d:05:b1:c3", "frequency": 2437, "level": -79},
    {
        "SSID": "CRH-Guest",
        "BSSID": "9c:d5:7d:05:b1:c2",
        "frequency": 2437,
        "level": -80,
    },
    {
        "SSID": "CRH-Guest",
        "BSSID": "9c:d5:7d:06:64:4d",
        "frequency": 5320,
        "level": -83,
    },
    {
        "SSID": ".@ TRUEWIFI",
        "BSSID": "34:f8:e7:c0:86:0f",
        "frequency": 5320,
        "level": -84,
    },
    {"SSID": "CRH-WiFi", "BSSID": "2c:5d:93:50:67:ec", "frequency": 5320, "level": -84},
    {
        "SSID": "CRH-Staff",
        "BSSID": "9c:d5:7d:06:64:4e",
        "frequency": 5320,
        "level": -84,
    },
    {
        "SSID": ".@ TrueMove H",
        "BSSID": "34:f8:e7:c0:86:0e",
        "frequency": 5320,
        "level": -85,
    },
    {
        "SSID": "BSKCR@Student",
        "BSSID": "26:5a:4c:14:4a:da",
        "frequency": 2437,
        "level": -88,
    },
]


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
