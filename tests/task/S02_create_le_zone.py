import pandas as pd
from mlv2.preprocess import LE
from mlv2.utils import Pipeline, PkSaver

pl = Pipeline(filenamePrefix="pipeline_leZone.xlsx")
saver = PkSaver(folderNamePrefix="leZone")

dfML = pd.read_csv("data/other/ml_tags.csv")
dfML["name"] = dfML["name"].apply(lambda el: el.strip())
data = dfML["name"].values.tolist()

leZone = LE(encoderType="NORMAL", pipeline=pl)
leZone.fit(data=data, info=dict(src="ml_tags.csv"))

# Output
pl.excel()
saver.save([leZone])
