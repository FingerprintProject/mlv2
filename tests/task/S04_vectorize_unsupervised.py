from pprint import pp

from mlv2.preprocess import FpLoader, FpDict
from mlv2.utils import PkLoader, Pipeline, PkSaver
from mlv2.vectorize import FpVectSupervised, FpVectUnSupervised

pl = Pipeline(filenamePrefix="pipeline_S04")
saver = PkSaver(folderNamePrefix="S04")


def vectorize_unsup():
    # Load vectorizer
    pkLoader = PkLoader()
    folderPath = "./save/S01_2024-10-25_08-47-00"
    pkLoader.fit(folderPath=folderPath)
    leBssid = pkLoader.get(["LE"])
    w2v = pkLoader.get(["W2V"])

    # Unsupervised Date
    folder2 = "data/unsupervised_survey"
    # filename2 = f"{folder2}/CRH_PROD_unsupervised_1729116590_small.json"
    filename2 = f"{folder2}/CRH_PROD_unsupervised_1729116590.json"

    # Load data
    loader = FpLoader(pipeline=pl)
    loader.fit(fileData=fileData, info=dict(src=fileData))

    # Preprocess
    fpDict = FpDict(pipeline=pl)
    fpDict.fit(data=loader.data, info=dict(src=loader.uuid))

    # Conformation
    res1 = fpDict.conform_to_le(leBssid)
    res2 = fpDict.conform_to_le(leZone)

    # Vectorize (supervised)
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
    fpVectSup.calcZoneCentroidSelfNearestNeighbors()
    pl.excel()
    saver.save([fpVectSup])
