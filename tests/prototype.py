import pandas as pd
from pprint import pp

from mlv2.preprocess import Adaptor, Survey, LE
from mlv2.vectorize import CorpusBuilder, OneHot, W2V, Vector
from mlv2.utils import Pipeline

# filename = "surveys/admin_json_hospital_id_15.json"
filename = "surveys/admin_json_hospital_id_15_small.json"
# filename = "surveys/admin_json_hospital_id_15_error.json"

df = pd.read_json(filename)
pipeline = Pipeline()
adaptor = Adaptor(pipeline=pipeline)
adaptor.fit(data=df, info=dict(src=filename))
survey = Survey(pipeline=pipeline)
survey.fit(data=adaptor.data, info=dict(src=adaptor.uuid))
leZone = LE(pipeline=pipeline)
leZone.fit(data=survey.getUniqueZoneNames(), info=dict(src=survey.uuid))
leBssid = LE(encoderType="BSSID", pipeline=pipeline)
leBssid.fit(data=survey.getBSSID(), info=dict(src=survey.uuid))
corpus = CorpusBuilder(corpusLineRepeat=10, pipeline=pipeline)
corpus.fit(data=survey.genFP(le=leBssid), info=dict(src=survey.uuid))
vector = OneHot(pipeline=pipeline)
vector.fit(data=survey.genFP(le=leBssid), info=dict(src=survey.uuid))
w2v = W2V(pipeline=pipeline)
w2v.fit(corpus=corpus.corpus, info=dict(src=corpus.uuid))

X = w2v.generate_embedding(data=survey.genFP(le=leBssid))
y = survey.getZoneNamesEncoded(le=leZone)

vector = Vector(pipeline=pipeline)
vector.fit(
    X=X,
    y=y,
    info=dict(
        embedder=w2v.uuid, survey=survey.uuid, leBssid=leBssid.uuid, leZone=leZone.uuid
    ),
)
pp(vector.data)
pipeline.excel()
