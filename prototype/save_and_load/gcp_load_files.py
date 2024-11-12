import os
import pathlib

from mlv2.record import (
    FpModelRepository,
    getLocalDbCredential,
    getLocalSessionFactory,
    GcsRepository,
    LoaderGcp,
)
from mlv2.preprocess import LE
from mlv2.utils import Logger, Pipeline


# Storage
gcpRepo = GcsRepository()

# Db
curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))
dbRepo = FpModelRepository(Session=Session)


# Loader
hospitalId = 30
loader = LoaderGcp(
    hospitalId=hospitalId,
    modelName="S00",
    fpModelRepository=dbRepo,
    storageRepository=gcpRepo,
)

loader.fit(name="S00")
loader.pick(searches=["LE"])
