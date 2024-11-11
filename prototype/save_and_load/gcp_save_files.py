import os
import pathlib

from mlv2.record import (
    FpModelRepository,
    getLocalDbCredential,
    getLocalSessionFactory,
    GcpRepository,
    SaverGCP,
)
from mlv2.preprocess import LE
from mlv2.utils import Logger, Pipeline

pl = Pipeline(filenamePrefix="pipeline")
lg = Logger(filenamePrefix="logs", now=pl.now)

# Storage
gcpRepo = GcpRepository()

# Db
curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))
dbRepo = FpModelRepository(Session=Session)

# Saver
hospitalId = 30
saver = SaverGCP(
    hospitalId=hospitalId,
    folderNamePrefix="S00",
    fpModelRepository=dbRepo,
    storageRepository=gcpRepo,
    now=pl.now,
    logger=lg,
)

leBssid1 = LE(encoderType="BSSID", pipeline=pl, logger=lg)
leBssid2 = LE(encoderType="BSSID", pipeline=pl, logger=lg)
saver.savePickle([leBssid1, leBssid2])

pl.excel()
saver.saveFile(fileNameArr=[pl.filename], tempFolderPathLocal=pl.outFolder)
saver.saveFile(fileNameArr=[lg.filename], tempFolderPathLocal=lg.outFolder)
