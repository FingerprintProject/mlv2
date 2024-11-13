import pandas as pd
from mlv2.preprocess import LE
from .S00_common import setupTask, hospitalId


def createLeZone():
    pl, lg, saver, _ = setupTask(hospitalId=hospitalId, modelName="S02")
    dfML = pd.read_csv("data/other/ml_tags.csv")
    dfML = dfML.rename(columns={"id": "ref", "name": "entry"})
    dfML["entry"] = dfML["entry"].apply(lambda el: el.strip())
    data = dfML["entry"].values.tolist()

    leZone = LE(encoderType="ZONE", pipeline=pl, logger=lg)
    leZone.fit(data=data, info=dict(src="ml_tags.csv"), extRef=dfML)

    # Save class instances and output
    saver.savePickle([leZone], makeActive=True)
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
