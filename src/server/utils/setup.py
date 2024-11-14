import os
import pathlib

from mlv2.record import (
    FpModelRepository,
    GcsRepository,
    FsRepository,
    Saver,
    Loader,
    getLocalDbCredential,
    getLocalSessionFactory,
    getGcpSessionFactory,
    getGcpDbCredential,
)
from mlv2.utils import Logger, Pipeline

hospitalId = 15

# DB_LOCATION = "LOCAL"
DB_LOCATION = "CLOUD"


def setupTask(hospitalId, modelName, dbLocation=DB_LOCATION):

    pl = Pipeline(filenamePrefix="pipeline")
    # Logger that does not log anything
    lg = Logger(filenamePrefix="logs", now=pl.now, disabled=True)

    if dbLocation == "LOCAL":
        # Storage
        storageRepo = FsRepository(logger=lg)

        # Session
        curPath = os.getcwd()
        parPath = pathlib.Path(curPath)
        dotEnvPath = os.path.join(parPath, ".env.dev")
        Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))
    elif dbLocation == "CLOUD":
        # Storage
        storageRepo = GcsRepository(logger=lg)

        # Session
        gcpSecretInfo = dict(
            project_id="811358834395", secret_id="python-wifi-api", version_id="1"
        )
        gcpCredential = getGcpDbCredential(**gcpSecretInfo)
        Session = getGcpSessionFactory(**gcpCredential)
    else:
        raise Exception("Unknown option")

    # Db repository
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
        logger=lg,
    )

    return pl, lg, saver, loader
