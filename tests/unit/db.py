import os
import pathlib

from mlv2.db import FpModelRepository, getLocalDbCredential, getLocalSessionFactory

curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
print(dotEnvPath)

Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))

repo = FpModelRepository()

reses = repo.get(Session=Session)
for res in reses:
    print(res.name)
