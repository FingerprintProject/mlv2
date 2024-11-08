import os
import pathlib

import sqlalchemy as sa
from dotenv import load_dotenv
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector
from sqlalchemy.orm import sessionmaker
from io import StringIO


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

    # TODO: Need to explore the implication of setting expire_on_commit to False.
    return sessionmaker(engine, expire_on_commit=False)


def getGcpDbCredential(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    resource_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
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
    return sessionmaker(engine, expire_on_commit=False)
