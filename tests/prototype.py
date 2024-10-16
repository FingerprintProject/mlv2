import pandas as pd
import pprint

from mlv2.data import Adaptor, Survey, LE
from mlv2.embed import Corpus, Vectorizer, Embedder
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
leZone.fit(data=survey.getZoneNames(), info=dict(src=survey.uuid))
leBssid = LE(encoderType="BSSID", pipeline=pipeline)
leBssid.fit(data=survey.getBSSID(), info=dict(src=survey.uuid))
corpus = Corpus(corpusLineRepeat=10, pipeline=pipeline)
corpus.fit(data=survey.genFP(le=leBssid), info=dict(src=survey.uuid))
vector = Vectorizer(pipeline=pipeline)
vector.fit(data=survey.genFP(le=leBssid), info=dict(src=survey.uuid))
embed = Embedder(pipeline=pipeline)
embed.fit(corpus=corpus.corpus, info=dict(src=corpus.uuid))
embed.fit(corpus=corpus.corpus, info=dict(src=corpus.uuid))
pipeline.excel()
