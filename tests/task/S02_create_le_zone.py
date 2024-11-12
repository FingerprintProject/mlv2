import pandas as pd
from mlv2.preprocess import LE
from .S00_common import setupTask


def createLeZone():
    pl, lg, saver, _ = setupTask(hospitalId=30, modelName="S02")
    dfML = pd.read_csv("data/other/ml_tags.csv")
    dfML["name"] = dfML["name"].apply(lambda el: el.strip())
    data = dfML["name"].values.tolist()

    leZone = LE(encoderType="ZONE", pipeline=pl)
    leZone.fit(data=data, info=dict(src="ml_tags.csv"))

    # Save class instances and output
    saver.savePickle([leZone], makeActive=True)
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
