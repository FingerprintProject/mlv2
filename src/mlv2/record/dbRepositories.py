from typing import List, Union

import sqlalchemy as sa
from pydantic import validate_call
from sqlalchemy.orm import Session, sessionmaker
from typing_extensions import TypedDict

from mlv2.utils import FpBaseModel
from .dbModels import FpModel


class JsonSchemaInsert(TypedDict):
    className: str
    path: str
    instanceId: str
    fileName: str


class DtoInsert(TypedDict):
    name: str
    path: str
    hospitalId: int
    contents: List[JsonSchemaInsert]


class FpModelRepository(FpBaseModel):
    Session: Union[Session, sessionmaker]

    def findAll(self):
        stmt = sa.select(FpModel)
        with self.Session() as session:
            results = session.scalars(stmt).fetchall()
        return results

    def findByInstanceId(self, Session, instanceId):
        stmt = sa.select(FpModel).where(FpModel.className == "LE")
        with self.Session() as session:
            results = session.scalars(stmt).fetchall()
        return results

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def insertModelRecord(
        self,
        data: DtoInsert,
    ):
        hospitalId = data["hospitalId"]
        path = data["path"]
        contents = data["contents"]
        stmt = sa.select(FpModel).where(
            (FpModel.hospitalId == hospitalId) & (FpModel.path == path)
        )
        with self.Session() as session, session.begin():
            # Check to see if the record exists
            reses: List[FpModel] = session.scalars(stmt).fetchall()
            if len(reses) == 0:
                # Add new record
                session.add_all([FpModel(**data)])
            elif len(reses) == 1:
                # Update record
                oldContents = reses[0].contents
                newContents = [*oldContents, *contents]
                reses[0].contents = newContents
            else:
                self.logger.warning(
                    "Found duplicated rows with the same path and hospitalId. No update occurs."
                )
