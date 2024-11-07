from pprint import pp

from mlv2.preprocess import LE
from mlv2.utils import Pipeline, PkSaverFS, SaverGCP
from mlv2.utils import Logger
from mlv2.vectorize import W2V, CorpusBuilder

pl = Pipeline(filenamePrefix="pipeline")
lg = Logger()

leBssid = LE(encoderType="BSSID", pipeline=pl, logger=lg)
leBssid = LE(encoderType="BSSID", pipeline=pl, logger=lg)
leBssid = LE(encoderType="BSSID", pipeline=pl, logger=lg)
leBssid = LE(encoderType="BSSID", pipeline=pl, logger=lg)

# leBssid = LE(encoderType="BSSID", pipeline=pl)
# leBssid = LE(encoderType="BSSID", pipeline=pl)
# leBssid = LE(encoderType="BSSID", pipeline=pl)
# leBssid = LE(encoderType="BSSID", pipeline=pl)
# leBssid = LE(encoderType="BSSID", pipeline=pl)
