from pprint import pp

from mlv2.preprocess import LE, FpDict, FpLoader
from mlv2.vectorize import W2V, CorpusBuilder

from .S00_common import setupTask


def createVectorizer():
    pl, lg, saver, _ = setupTask(hospitalId=30, modelName="S01")

    fpLoader = FpLoader(pipeline=pl, logger=lg)

    folder1 = "data/supervised_survey"
    # filename1 = f"{folder1}/admin_json_hospital_id_15_small.json"
    filename1 = f"{folder1}/admin_json_hospital_id_15.json"
    # filename1 = f"{folder1}/admin_json_hospital_id_15_error.json"

    folder2 = "data/unsupervised_survey"
    # filename2 = f"{folder2}/CRH_PROD_unsupervised_1729116590_small.json"
    filename2 = f"{folder2}/CRH_PROD_unsupervised_1729116590.json"

    fileData1 = dict(filename=filename1, fileType="SUPV2")
    fileData2 = dict(filename=filename2, fileType="UNSUPV1")
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
