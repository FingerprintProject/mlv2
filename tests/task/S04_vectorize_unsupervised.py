from pprint import pp

from mlv2.preprocess import FpLoader, FpDict
from mlv2.vectorize import FpVectUnsupervised
from .S00_common import setupTask


def vectorize_unsup():

    pl, lg, saver, loader = setupTask(hospitalId=30, modelName="S04")

    # Load vectorizer
    loader.fitFromModelName(name="S01")
    leBssid = loader.pick(["LE"])
    w2v = loader.pick(["W2V"])

    # Unsupervised Date
    folder2 = "data/unsupervised_survey"
    # filename2 = f"{folder2}/CRH_PROD_unsupervised_1729116590_small.json"
    filename2 = f"{folder2}/CRH_PROD_unsupervised_1729116590.json"
    fileData = [dict(filename=filename2, fileType="UNSUPV1")]

    # Load data
    loader = FpLoader(pipeline=pl, logger=lg)
    loader.fit(fileData=fileData, info=dict(src=fileData))

    # Preprocess
    fpDict = FpDict(pipeline=pl, logger=lg)
    fpDict.fit(data=loader.data, info=dict(src=loader.uuid))

    # Conformation
    res1 = fpDict.conform_to_le(leBssid)

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

    saver.savePickle([fpVectUnsup], makeActive=True)
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
