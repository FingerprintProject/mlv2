from pprint import pp

from mlv2.preprocess import LE, FpDict, FpLoader
from mlv2.utils import Pipeline, PkSaver
from mlv2.vectorize import W2V, CorpusBuilder

pl = Pipeline(filenamePrefix="pipeline_S01")
saver = PkSaver(folderNamePrefix="S01")

fpLoader = FpLoader(pipeline=pl)

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
fpDict = FpDict(pipeline=pl)
fpDict.fit(data=fpLoader.data, info=dict(src=fpLoader.uuid))

# Encode BSSID
leBssid = LE(encoderType="BSSID", pipeline=pl)
leBssid.fit(data=fpDict.getUniqueBSSID(), info=dict(src=fpDict.uuid))

# Conform
fpDict.conform_to_le(leBssid)

# Corpus
fpEncoded = leBssid.encode(data=fpDict.getFp(), fpDict=fpDict)
cb = CorpusBuilder(corpusLineRepeat=10, pipeline=pl)
cb.fit(data=fpEncoded, id_leBssid=leBssid.uuid, info=dict(src=fpDict.uuid))

# Embed
w2v = W2V(pipeline=pl)
w2v.fit(corpus=cb.corpus, id_leBssid=leBssid.uuid, info=dict(src=cb.uuid))

# Output
pl.excel()
saver.save([leBssid, w2v])
