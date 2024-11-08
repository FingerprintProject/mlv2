import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .models import FpModel


class FpModelRepository(BaseModel):

    def get(self, Session: Session):
        stmt = sa.select(FpModel)
        with Session() as session, session.begin():
            reses = session.scalars(stmt).fetchall()
        return reses
