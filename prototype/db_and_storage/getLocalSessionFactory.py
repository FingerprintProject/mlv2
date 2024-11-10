import os
import pathlib

import sqlalchemy as sa
from dotenv import load_dotenv, dotenv_values
from sqlalchemy.orm import sessionmaker

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
