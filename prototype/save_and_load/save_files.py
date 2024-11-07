from pprint import pp

from mlv2.preprocess import LE, FpDict, FpLoader
from mlv2.utils import Pipeline, PkSaverFS, SaverGCP, Logger
from mlv2.vectorize import W2V, CorpusBuilder
from google.auth import default

pl = Pipeline(filenamePrefix="pipeline")
lg = Logger(filenamePrefix="logs", now=pl.now)

credentials, _ = default()
saver = SaverGCP(folderNamePrefix="S00", credentials=credentials, now=pl.now, logger=lg)

leBssid = LE(encoderType="BSSID", pipeline=pl, logger=lg)

saveInfo = saver.savePickle([leBssid])
pl.excel()

saver.saveFile(filenameArr=[pl.filename], tempFolderPathLocal=pl.outFolder)
saver.saveFile(filenameArr=[lg.filename], tempFolderPathLocal=lg.outFolder)
