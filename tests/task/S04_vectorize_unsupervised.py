from pprint import pp

from mlv2.preprocess import FpLoader, FpDict
from mlv2.utils import PkLoader, Pipeline, PkSaverFS
from mlv2.vectorize import FpVectUnsupervised

pl = Pipeline(filenamePrefix="pipeline_S04")
saver = PkSaverFS(folderNamePrefix="S04")


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
    fileData = [dict(filename=filename2, fileType="UNSUPV1")]

    # Load data
    loader = FpLoader(pipeline=pl)
    loader.fit(fileData=fileData, info=dict(src=fileData))

    # Preprocess
    fpDict = FpDict(pipeline=pl)
    fpDict.fit(data=loader.data, info=dict(src=loader.uuid))

    # Conformation
    res1 = fpDict.conform_to_le(leBssid)

    # Vectorize (supervised)
    fpEncode = leBssid.encode(fpDict.getFp(), fpDict=fpDict)

    X = w2v.vectorize(data=fpEncode, fpDict=fpDict)

    fpVectUnsup = FpVectUnsupervised(pipeline=pl)
    fpVectUnsup.fit(
        XArr=[X],
        id_vectorizer=w2v.uuid,
        id_leBssid=leBssid.uuid,
        info=dict(fpDict=fpDict.uuid),
    )
    pl.excel()
    saver.save([fpVectUnsup])
    pass
