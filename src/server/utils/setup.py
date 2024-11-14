import os
import pathlib

from dotenv import load_dotenv

from mlv2.record import (
    FpModelRepository,
    FsRepository,
    GcsRepository,
    Loader,
    Saver,
    getGcpDbCredential,
    getGcpSessionFactory,
    getLocalDbCredential,
    getLocalSessionFactory,
)
from mlv2.utils import Logger, Pipeline

hospitalId = 15

# DB_LOCATION = "LOCAL"
DB_LOCATION = "CLOUD"


ENVIRONMENT = os.getenv("ENVIRONMENT")

if ENVIRONMENT != "CLOUD_RUN":
    curPath = os.getcwd()
    parPath = pathlib.Path(curPath)
    dotEnvPath = os.path.join(parPath, ".env.dev")
    load_dotenv("./env.dev", override=True)

# Env
PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_NAME = os.getenv("PROJECT_NAME")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")
SECRET_ID = os.getenv("SECRET_ID")
VERSION_ID = os.getenv("VERSION_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")

print(
    dict(
        PROJECT_ID=PROJECT_ID,
        PROJECT_NUMBER=PROJECT_NUMBER,
        PROJECT_NAME=PROJECT_NAME,
        SECRET_ID=SECRET_ID,
        VERSION_ID=VERSION_ID,
        BUCKET_NAME=BUCKET_NAME,
    )
)


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
        storageRepo = GcsRepository(
            logger=lg, projectId=PROJECT_NAME, bucketName=BUCKET_NAME
        )

        # Session
        gcpSecretInfo = dict(
            project_number=PROJECT_NUMBER, secret_id=SECRET_ID, version_id=VERSION_ID
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
