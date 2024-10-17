from pprint import pp

from mlv2.preprocess import FpLoader, FpDict, LE, FpVect
from mlv2.vectorize import CorpusBuilder, W2V
from mlv2.utils import PkLoader, Pipeline

pl = Pipeline()

# Load pickle
pkLoader = PkLoader()
folderPath = "./save/embed_2024-10-17_14-20-15"
pkLoader.fit(folderPath=folderPath)
leBssid = pkLoader.get(["LE"])
w2v = pkLoader.get(["W2V"])

# Load supervised data
folder1 = "data/supervised_survey"
filename1 = f"{folder1}/admin_json_hospital_id_15_small.json"
# filename1 = f"{folder1}/admin_json_hospital_id_15.json"
fileData = [dict(filename=filename1, fileType="SUPV2")]

loader = FpLoader(pipeline=pl)
loader.fit(fileData=fileData, info=dict(src=fileData))
fpDict = FpDict(pipeline=pl)
fpDict.fit(data=loader.data, info=dict(src=loader.uuid))

# Zone encoding (Should come from ml_tags)
leZone = LE(pipeline=pl)
leZone.fit(data=fpDict.getUniqueZoneNames(), info=dict(src=fpDict.uuid))

# Generate embeddding
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
