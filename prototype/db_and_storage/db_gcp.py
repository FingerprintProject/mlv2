import sqlalchemy as sa
from getGcpSessionFactory import GcpSession
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class FpModel(Base):
    __tablename__ = "fp_models"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    path = sa.Column(sa.String)


# Read
stmt = sa.select(FpModel).where(FpModel.name.like("%CRH%"))
print(stmt)
with GcpSession() as session, session.begin():
    reses = session.scalars(stmt).fetchall()
    for res in reses:
        print(res.name)
