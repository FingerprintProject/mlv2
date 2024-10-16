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
adaptor = Adaptor(pipeline=pipeline)
adaptor.fit(data=df, info={"filename": filename})
survey = Survey(data=adaptor.data, pipeline=pipeline)
leZone = LE(pipeline=pipeline)
leZone.fit(data=survey.getZoneNames(), surveyId=survey.uuid)
leBssid = LE(encoderType="BSSID", pipeline=pipeline)
leBssid.fit(data=survey.getBSSID(), surveyId=survey.uuid)
corpus = Corpus(data=survey.genFP(le=leBssid), corpusLineRepeat=10, pipeline=pipeline)
vector = Vectorizer()
vector.fit(data=survey.genFP(le=leBssid))
pprint.pp(vector.data)
pipeline.excel()
