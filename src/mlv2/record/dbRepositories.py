from typing import List, Union

import sqlalchemy as sa
from pydantic import validate_call
from sqlalchemy.orm import Session, sessionmaker
from typing_extensions import TypedDict

from mlv2.utils import FpBaseModel

from .dbModels import FpModel


class FpModelJsonSchema(TypedDict):
    className: str
    path: str
    instanceId: str
    filename: str


class FpModelRepositoryInsert(TypedDict):
    name: str
    path: str
    hospitalId: int
    contents: List[FpModelJsonSchema]


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

    def findByInstanceId(self, Session, instanceId):
        stmt = sa.select(FpModel).where(FpModel.className == "LE")
        with self.Session() as session:
            results = session.scalars(stmt).fetchall()
        return results

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def insert(
        self,
        dataArr: List[FpModelRepositoryInsert],
    ):
        rows = []
        for data in dataArr:
            rows.append(FpModel(**data))

        with self.Session() as session, session.begin():
            session.add_all(rows)
