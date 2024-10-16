import pandas as pd
import pprint

from mlv2.data import Adaptor, Survey, LE
from mlv2.embed import Corpus, Vectorizer
from mlv2.utils import Pipeline

# filename = "surveys/admin_json_hospital_id_15.json"
filename = "surveys/admin_json_hospital_id_15_small.json"
# filename = "surveys/admin_json_hospital_id_15_error.json"

df = pd.read_json(filename)
pipeline = Pipeline()
adapter = Adaptor(data=df, pipeline=pipeline)
survey = Survey(data=adapter.data, pipeline=pipeline)
leZone = LE(data=survey.getZoneNames(), pipeline=pipeline)
leBssid = LE(data=survey.getBSSID(), encoderType="BSSID", pipeline=pipeline)
corpus = Corpus(data=survey.genFP(le=leBssid), corpusLineRepeat=10, pipeline=pipeline)
vector = Vectorizer()
vector.fit(data=survey.genFP(le=leBssid))
pprint.pp(vector.data)
pipeline.excel()
