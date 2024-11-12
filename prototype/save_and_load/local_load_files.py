import os
import pathlib

from mlv2.record import (
    FpModelRepository,
    getLocalDbCredential,
    getLocalSessionFactory,
    FsRepository,
    Loader,
)


# Storage
storageRepo = FsRepository()

# Db
curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))
dbRepo = FpModelRepository(Session=Session)


# Loader
hospitalId = 30
loader = Loader(
    hospitalId=hospitalId,
    modelName="S00",
    fpModelRepository=dbRepo,
    storageRepository=storageRepo,
)

loader.fitFromModelName(name="S00")
LE = loader.pick(searches=["e749b814"])

pass
