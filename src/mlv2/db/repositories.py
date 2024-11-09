import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .models import FpModel


class FpModelRepository(BaseModel):

    def findAll(self, Session: Session):
        stmt = sa.select(FpModel)
        with Session() as session, session.begin():
            reses = session.scalars(stmt).fetchall()
        return reses

    def insert(self, Session: Session, dataArr):

        rows = []

        for data in dataArr:
            rows.append(FpModel(**data))

        with Session() as session, session.begin():
            session.add_all(rows)
