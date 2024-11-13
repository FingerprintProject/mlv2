import os
import pathlib

from mlv2.record import (
    FpModelRepository,
    FsRepository,
    Saver,
    Loader,
    getLocalDbCredential,
    getLocalSessionFactory,
    getGcpSessionFactory,
)
from mlv2.utils import Logger, Pipeline

hospitalId = 15


def setupTask(hospitalId, modelName):

    pl = Pipeline(filenamePrefix="pipeline")
    lg = Logger(filenamePrefix="logs", now=pl.now)

    # Storage
    storageRepo = FsRepository(logger=lg)

    # Db
    curPath = os.getcwd()
    parPath = pathlib.Path(curPath)
    dotEnvPath = os.path.join(parPath, ".env.dev")
    Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))
    dbRepo = FpModelRepository(Session=Session, logger=lg)

    # Saver
    saver = Saver(
        hospitalId=hospitalId,
        modelName=modelName,
        fpModelRepository=dbRepo,
        storageRepository=storageRepo,
        now=pl.now,
        logger=lg,
    )

    # Loader
    loader = Loader(
        hospitalId=hospitalId,
        modelName=modelName,
        fpModelRepository=dbRepo,
        storageRepository=storageRepo,
    )

    return pl, lg, saver, loader
