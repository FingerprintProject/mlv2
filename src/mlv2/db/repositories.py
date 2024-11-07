from typing import Any, Optional

import sqlalchemy as sa
from google.cloud.sql.connector import Connector
from pydantic import Field
from sqlalchemy.orm import Session

from mlv2.utils import FpBaseModel


class RepositoryBase(FpBaseModel):

    session: Optional[Any] = None
    connectionMode: str = Field(pattern=r"^GCP$|^LOCAL$|", default="LOCAL")
    db_username: str
    db_password: str
    db_database: str
    db_instance: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[str] = None
    cloudSqlConnector: Optional[Connector] = None

    def model_post_init(self, __context):

        if self.connectionMode == "LOCAL":

            if self.db_host is None or self.db_port is None:
                raise Exception("Mising db_host or db_port")

            urlString = f"postgresql+pg8000://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{db_database}"
            engine = sa.create_engine(urlString)

        elif self.connectionMode == "GCP":

            if self.db_instance is None or self.cloudSqlConnector is None:
                raise Exception("Mising db_instance or cloud_sql_connector")

            def getConn():
                return self.cloudSqlConnector.connect(
                    self.db_instance,
                    "pg8000",
                    user=self.db_username,
                    password=self.db_password,
                    db=self.db_database,
                    # ip_type = "private",
                )

            engine = sa.create_engine(
                "postgresql+pg8000://",
                creator=getConn,
            )

        self.session = Session(engine)


class FpModel(RepositoryBase):

    pass
