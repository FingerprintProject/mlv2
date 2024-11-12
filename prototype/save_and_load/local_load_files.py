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

# loader.fitFromModelName(name="S00")
# LE = loader.pick(searches=["e749b814"])

loader.fitFromPath(path="save_V2\\30\\S00_2024-11-13_04-52-02")
LE = loader.pick(searches=["LE_00812ae5"])
pass
