import os
import pathlib

import sqlalchemy as sa
from dotenv import load_dotenv, dotenv_values
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector
from sqlalchemy.orm import sessionmaker
from io import StringIO

curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
print(dotEnvPath)


def getLocalDbCredential(dotEnvPath):

    if not os.path.isfile(dotEnvPath):
        raise FileNotFoundError(f"File not found: {dotEnvPath}")

    load_dotenv(dotenv_path=pathlib.Path(dotEnvPath), override=True)

    db_username = os.getenv("PSQL_USERNAME")
    db_password = os.getenv("PSQL_PASSWORD")
    db_database = os.getenv("PSQL_DATABASE")
    db_host = os.getenv("PSQL_HOST")
    db_port = os.getenv("PSQL_PORT")

    return dict(
        db_username=db_username,
        db_password=db_password,
        db_database=db_database,
        db_host=db_host,
        db_port=db_port,
    )


def getLocalSessionFactory(db_username, db_password, db_database, db_host, db_port):
    urlString = f"postgresql+pg8000://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"
    engine = sa.create_engine(urlString)
    return sessionmaker(engine)


LocalSession = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))


# GCP


def getGcpDbCredential(project_number, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    resource_name = (
        f"projects/{project_number}/secrets/{secret_id}/versions/{version_id}"
    )
    response = client.access_secret_version(request={"name": resource_name})
    payload = response.payload.data.decode("UTF-8")
    load_dotenv(stream=StringIO(payload), override=True)

    db_instance = os.getenv("PSQL_INSTANCE")
    db_username = os.getenv("PSQL_USERNAME")
    db_password = os.getenv("PSQL_PASSWORD")
    db_database = os.getenv("PSQL_DATABASE")

    return dict(
        db_instance=db_instance,
        db_username=db_username,
        db_password=db_password,
        db_database=db_database,
    )


def getGcpSessionFactory(db_instance, db_username, db_password, db_database):
    connector = Connector()

    def getConn(connector=connector):
        return connector.connect(
            db_instance,
            "pg8000",
            user=db_username,
            password=db_password,
            db=db_database,
            # ip_type = "private",
        )

    engine = sa.create_engine(
        "postgresql+pg8000://",
        creator=getConn,
    )
    return sessionmaker(engine)


gcpSecretInfo = dict(
    project_number="811358834395", secret_id="python-wifi-api", version_id="1"
)

gcpCredential = getGcpDbCredential(**gcpSecretInfo)
GcpSession = getGcpSessionFactory(**gcpCredential)
