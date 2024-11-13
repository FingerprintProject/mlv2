import sqlalchemy as sa
from getGcpSessionFactory import GcpSession
from mlv2.record import FpModel

# Read
stmt = sa.select(FpModel).where(FpModel.name.like("%CRH%"))
print(stmt)
with GcpSession() as session, session.begin():
    reses = session.scalars(stmt).fetchall()
    for res in reses:
        print(res.name)
