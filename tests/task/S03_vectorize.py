from pprint import pp

from mlv2.preprocess import FpLoader, FpDict, LE, FpVect
from mlv2.utils import PkLoader, Pipeline

pl = Pipeline(filenamePrefix="pipeline_vectorize")

# Load embed
pkLoader = PkLoader()
folderPath = "./save/embed_2024-10-18_08-55-20"
pkLoader.fit(folderPath=folderPath)
leBssid = pkLoader.get(["LE"])
w2v = pkLoader.get(["W2V"])

# Load leZone
pkLoader = PkLoader()
folderPath = "./save/leZone_2024-10-18_12-02-10"
pkLoader.fit(folderPath=folderPath)
leZone = pkLoader.get(["LE"])

# Supervised data
folder1 = "data/supervised_survey"
filename1 = f"{folder1}/admin_json_hospital_id_15_small.json"
# filename1 = f"{folder1}/admin_json_hospital_id_15.json"
fileData = [dict(filename=filename1, fileType="SUPV2")]

# Load data
loader = FpLoader(pipeline=pl)
loader.fit(fileData=fileData, info=dict(src=fileData))

# Preprocess
fpDict = FpDict(pipeline=pl)
fpDict.fit(data=loader.data, info=dict(src=loader.uuid))

# Vectorize
X = w2v.vectorize(data=fpDict.genFP(le=leBssid))
y = fpDict.getZoneNamesEncoded(le=leZone)

fpVect = FpVect(pipeline=pl)
fpVect.fit(
    X=X,
    y=y,
    id_vectorizer=w2v.uuid,
    id_leBssid=leBssid.uuid,
    id_leZone=leZone.uuid,
    info=dict(fpDict=fpDict.uuid),
)
pp(fpVect.data)
pl.excel()
