import os
import pathlib

from mlv2.db import FpModelRepository, getLocalDbCredential, getLocalSessionFactory

curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
print(dotEnvPath)

Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))

repo = FpModelRepository()

reses = repo.findAll(Session=Session)
for res in reses:
    print(res.name)

dataArr = [dict(name="T", path="/", hospital_id=15, model_type="V2")]
repo.insert(Session=Session, dataArr=dataArr)
