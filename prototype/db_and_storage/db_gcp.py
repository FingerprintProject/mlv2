import sqlalchemy as sa
from getSessionFactory import GcpSession
from mlv2.db import FpModel

# Read
stmt = sa.select(FpModel).where(FpModel.name.like("%CRH%"))
print(stmt)
with GcpSession() as session, session.begin():
    reses = session.scalars(stmt).fetchall()
    for res in reses:
        print(res.name, res.model_type)
