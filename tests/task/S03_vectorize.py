from pprint import pp

from mlv2.preprocess import FpLoader, FpDict
from mlv2.utils import PkLoader, Pipeline
from mlv2.vectorize import FpVectSupervised

pl = Pipeline(filenamePrefix="pipeline_S03")


def vectorize():
    # Load vectorizer
    pkLoader = PkLoader()
    folderPath = "./save/S01_2024-10-25_08-47-00"
    pkLoader.fit(folderPath=folderPath)
    leBssid = pkLoader.get(["LE"])
    w2v = pkLoader.get(["W2V"])

    # Load leZone
    pkLoader = PkLoader()
    folderPath = "./save/S02_2024-10-25_08-52-01"
    pkLoader.fit(folderPath=folderPath)
    leZone = pkLoader.get(["LE"])

    # Supervised data
    folder1 = "data/supervised_survey"
    # filename1 = f"{folder1}/admin_json_hospital_id_15_small.json"
    filename1 = f"{folder1}/admin_json_hospital_id_15.json"
    fileData = [dict(filename=filename1, fileType="SUPV2")]

    # Load data
    loader = FpLoader(pipeline=pl)
    loader.fit(fileData=fileData, info=dict(src=fileData))

    # Preprocess
    fpDict = FpDict(pipeline=pl)
    fpDict.fit(data=loader.data, info=dict(src=loader.uuid))

    # Conformation
    res1 = fpDict.conform_to_le(leBssid)
    res2 = fpDict.conform_to_le(leZone)

    # Vectorize
    fpEncode = leBssid.encode(fpDict.getFp(), fpDict=fpDict)

    X = w2v.vectorize(data=fpEncode, fpDict=fpDict)
    y = leZone.encode(fpDict.getZoneNames(), fpDict=fpDict)

    fpVectSup = FpVectSupervised(pipeline=pl)
    fpVectSup.fit(
        X=X,
        y=y,
        id_vectorizer=w2v.uuid,
        id_leBssid=leBssid.uuid,
        id_leZone=leZone.uuid,
        info=dict(fpDict=fpDict.uuid),
    )
    fpVectSup.calcCentroid()
    # pl.excel()
    pass
