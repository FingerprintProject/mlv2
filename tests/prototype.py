from pprint import pp

from mlv2.preprocess import Loader, FpDict, LE, FpVect
from mlv2.vectorize import CorpusBuilder, W2V
from mlv2.utils import Pipeline

folder = "data/supervised_survey"

# filename = f"{folder}surveys/admin_json_hospital_id_15.json"
filename = f"{folder}/admin_json_hospital_id_15_small.json"
# filename = f"{folder}surveys/admin_json_hospital_id_15_error.json"

pl = Pipeline()
loader = Loader(pipeline=pl)
fileData = [dict(filename=filename, fileType="SUPV2")]
loader.fit(fileData=fileData, info=dict(src=filename))
fpDict = FpDict(pipeline=pl)
fpDict.fit(data=loader.data, info=dict(src=loader.uuid))
leZone = LE(pipeline=pl)
leZone.fit(data=fpDict.getUniqueZoneNames(), info=dict(src=fpDict.uuid))
leBssid = LE(encoderType="BSSID", pipeline=pl)
leBssid.fit(data=fpDict.getBSSID(), info=dict(src=fpDict.uuid))
cb = CorpusBuilder(corpusLineRepeat=10, pipeline=pl)
cb.fit(data=fpDict.genFP(le=leBssid), info=dict(src=fpDict.uuid))
w2v = W2V(pipeline=pl)
w2v.fit(corpus=cb.corpus, info=dict(src=cb.uuid))

X = w2v.generate_embedding(data=fpDict.genFP(le=leBssid))
y = fpDict.getZoneNamesEncoded(le=leZone)

fpVect = FpVect(pipeline=pl)
fpVect.fit(
    X=X,
    y=y,
    info=dict(
        embedder=w2v.uuid, survey=fpDict.uuid, leBssid=leBssid.uuid, leZone=leZone.uuid
    ),
)
pp(fpVect.data)
pl.excel()
