import sqlalchemy as sa
from pydantic import BaseModel, validate_call
from sqlalchemy.orm import Session, sessionmaker
from .models import FpModel
from typing_extensions import TypedDict
from typing import List, Union


class FpModelRepositoryInsert(TypedDict):
    name: str
    path: str
    instanceId: str
    className: str
    hospitalId: int


class FpModelRepository(BaseModel):

    def findAll(self, Session: Session):
        stmt = sa.select(FpModel)
        with Session() as session:
            results = session.scalars(stmt).fetchall()
        return results

    def findByInstanceId(self, Session, instanceId):
        stmt = sa.select(FpModel).where(FpModel.className == "LE")
        with Session() as session:
            results = session.scalars(stmt).fetchall()
        return results

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def insert(
        self,
        Session: Union[Session, sessionmaker],
        dataArr: List[FpModelRepositoryInsert],
    ):
        rows = []
        for data in dataArr:
            rows.append(FpModel(**data))

        with Session() as session, session.begin():
            session.add_all(rows)
