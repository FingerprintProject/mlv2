from pprint import pp

from mlv2.preprocess import LE, FpDict, FpLoaderFile
from mlv2.vectorize import W2V, CorpusBuilder

from .S00_common import setupTask, hospitalId


def createVectorizer():
    pl, lg, saver, _ = setupTask(hospitalId=hospitalId, modelName="S01")

    fpLoader = FpLoaderFile(pipeline=pl, logger=lg)

    folder1 = "data/supervised_survey"
    if hospitalId == 15:
        # filename1 = f"{folder1}/HID_15_sup_small.json"
        filename1 = f"{folder1}/HID_15_sup.json"
        fileData1 = dict(
            fileName=filename1, fileType="BIG_QUERY", dataType="SUPERVISED"
        )

    elif hospitalId == 41:
        filename1 = f"{folder1}/HID_41_sup.json"
        fileData1 = dict(
            fileName=filename1, fileType="BIG_QUERY", dataType="SUPERVISED"
        )

    folder2 = "data/unsupervised_survey"
    if hospitalId == 15:
        # filename2 = f"{folder2}/CRH_PROD_unsupervised_1729116590_small.json"
        filename2 = f"{folder2}/CRH_PROD_unsupervised_1729116590.json"
        fileData2 = dict(
            fileName=filename2, fileType="PHP_SERVER", dataType="UNSUPERVISED"
        )
    elif hospitalId == 41:
        filename2 = f"{folder2}/HID_41_unsup.json"
        fileData2 = dict(
            fileName=filename2, fileType="BIG_QUERY", dataType="UNSUPERVISED"
        )

    fileData = [fileData1, fileData2]

    # Load
    fpLoader.fit(fileData=fileData, info=dict(src=fileData))

    # Dict data
    fpDict = FpDict(pipeline=pl, logger=lg)
    fpDict.fit(data=fpLoader.data, info=dict(src=fpLoader.uuid))

    # Encode BSSID
    leBssid = LE(encoderType="BSSID", pipeline=pl, logger=lg)
    leBssid.fit(data=fpDict.getUniqueBSSID(), info=dict(src=fpDict.uuid))

    # Conform
    fpDict.conform_to_le(leBssid)

    # Corpus
    fpEncoded = leBssid.encode(data=fpDict.getFp(), fpDict=fpDict)
    cb = CorpusBuilder(corpusLineRepeat=10, pipeline=pl)
    cb.fit(data=fpEncoded, id_leBssid=leBssid.uuid, info=dict(src=fpDict.uuid))

    # Embed
    w2v = W2V(pipeline=pl, logger=lg)
    w2v.fit(corpus=cb.corpus, id_leBssid=leBssid.uuid, info=dict(src=cb.uuid))

    # Save class instances and output
    saver.savePickle([leBssid, w2v], makeActive=True)
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
