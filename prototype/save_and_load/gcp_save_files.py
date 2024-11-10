import os
import pathlib

from google.auth import default

from mlv2.db import FpModelRepository, getLocalDbCredential, getLocalSessionFactory
from mlv2.preprocess import LE
from mlv2.utils import Logger, Pipeline, SaverGCP

pl = Pipeline(filenamePrefix="pipeline")
lg = Logger(filenamePrefix="logs", now=pl.now)
credentials, _ = default()
# Saver
curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))
repo = FpModelRepository()
hospitalId = 30
saver = SaverGCP(
    hospitalId=hospitalId,
    folderNamePrefix="S00",
    credentials=credentials,
    Session=Session,
    fpModelRepository=repo,
    now=pl.now,
    logger=lg,
)

leBssid1 = LE(encoderType="BSSID", pipeline=pl, logger=lg)
leBssid2 = LE(encoderType="BSSID", pipeline=pl, logger=lg)
saver.savePickle([leBssid1, leBssid2])

pl.excel()
saver.saveFile(filenameArr=[pl.filename], tempFolderPathLocal=pl.outFolder)
saver.saveFile(filenameArr=[lg.filename], tempFolderPathLocal=lg.outFolder)
