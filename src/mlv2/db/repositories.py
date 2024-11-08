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
            name = data["name"]
            hospital_id = data["hospital_id"]
            path = data["path"]
            model_type = data["model_type"]
            rows.append(
                FpModel(
                    name=name, hospital_id=hospital_id, path=path, model_type=model_type
                )
            )

        with Session() as session, session.begin():
            session.add_all(rows)
