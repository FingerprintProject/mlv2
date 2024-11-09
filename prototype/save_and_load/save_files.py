from pprint import pp
import os
import pathlib

from mlv2.preprocess import LE, FpDict, FpLoader
from mlv2.utils import Pipeline, SaverFS, SaverGCP, Logger
from mlv2.vectorize import W2V, CorpusBuilder
from google.auth import default
from mlv2.db import FpModelRepository, getLocalDbCredential, getLocalSessionFactory

pl = Pipeline(filenamePrefix="pipeline")
lg = Logger(filenamePrefix="logs", now=pl.now)

credentials, _ = default()
saver = SaverGCP(folderNamePrefix="S00", credentials=credentials, now=pl.now, logger=lg)

leBssid = LE(encoderType="BSSID", pipeline=pl, logger=lg)

pl.excel()
saver.saveFile(filenameArr=[pl.filename], tempFolderPathLocal=pl.outFolder)
saver.saveFile(filenameArr=[lg.filename], tempFolderPathLocal=lg.outFolder)

saveInfo = saver.savePickle([leBssid])

curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))

repo = FpModelRepository()
dataArr = [dict(**saveInfo, hospitalId=15)]
repo.insert(Session=Session, dataArr=dataArr)
