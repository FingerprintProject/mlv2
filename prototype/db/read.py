import os
import pathlib

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from mlv2.db import FpModel

curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")


print(dotEnvPath)
if not os.path.isfile(dotEnvPath):
    raise FileNotFoundError(f"File not found: {dotEnvPath}")

load_dotenv(dotenv_path=pathlib.Path(dotEnvPath), override=True)


db_username = os.getenv("PSQL_USERNAME")
db_password = os.getenv("PSQL_PASSWORD")
db_database = os.getenv("PSQL_DATABASE")
db_host = os.getenv("PSQL_HOST")
db_port = os.getenv("PSQL_PORT")


urlString = (
    f"postgresql+pg8000://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"
)

print(urlString)

engine = sa.create_engine(urlString)


session = Session(engine)
stmt = sa.select(FpModel).where(FpModel.name.like("%CRH%"))
# stmt = sa.select(FpModel)
print(stmt)
reses = session.scalars(stmt)
print(reses.fetchall())
# for res in reses:
#     print(res.name, res.model_type, type(res.model_type))
