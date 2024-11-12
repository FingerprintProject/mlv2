from pprint import pp

from mlv2.preprocess import FpLoader, FpDict
from mlv2.vectorize import FpVectSupervised
from .S00_common import setupTask


def vectorize_sup():
    pl, lg, saver, loader = setupTask(hospitalId=30, modelName="S03")
    # Load vectorizer
    loader.fitFromModelName(name="S01")
    leBssid = loader.pick(["LE"])
    w2v = loader.pick(["W2V"])

    # Load leZone
    loader.fitFromModelName(name="S02")
    leZone = loader.pick(["LE"])

    # Supervised data
    folder1 = "data/supervised_survey"
    # filename1 = f"{folder1}/admin_json_hospital_id_15_small.json"
    filename1 = f"{folder1}/admin_json_hospital_id_15.json"
    fileData = [dict(filename=filename1, fileType="SUPV2")]

    # Load data
    loader = FpLoader(pipeline=pl, logger=lg)
    loader.fit(fileData=fileData, info=dict(src=fileData))

    # Preprocess
    fpDict = FpDict(pipeline=pl, logger=lg)
    fpDict.fit(data=loader.data, info=dict(src=loader.uuid))

    # Conformation
    fpDict.conform_to_le(leBssid)
    fpDict.conform_to_le(leZone)

    # Vectorize (supervised)
    fpEncode = leBssid.encode(fpDict.getFp(), fpDict=fpDict)

    X = w2v.vectorize(data=fpEncode, fpDict=fpDict)
    y = leZone.encode(fpDict.getZoneNames(), fpDict=fpDict)

    fpVectSup = FpVectSupervised(pipeline=pl, logger=lg)
    fpVectSup.fit(
        XArr=[X],
        yArr=[y],
        id_vectorizer=w2v.uuid,
        id_leBssid=leBssid.uuid,
        id_leZone=leZone.uuid,
        info=dict(fpDict=fpDict.uuid),
    )
    fpVectSup.calcCentroid()
    fpVectSup.calcZoneCentroidSelfNearestNeighbors()
    saver.savePickle([fpVectSup], makeActive=True)
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
