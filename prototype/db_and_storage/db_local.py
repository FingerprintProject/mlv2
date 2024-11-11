import sqlalchemy as sa
from getLocalSessionFactory import LocalSession
from mlv2.record import FpModel

# Read
# stmt = sa.select(FpModel).where(FpModel.name.like("%CRH%"))
# print(stmt)
# with LocalSession() as session, session.begin():
#     reses = session.scalars(stmt).fetchall()
#     for res in reses:
#         print(res.__dict__)
pass


# Write
newModel = FpModel(name="TEST", hospitalId=16, path="NEW_PATH", contents=[dict(a=10)])

with LocalSession() as session, session.begin():
    session.add_all([newModel])
    stmt = sa.select(FpModel)
    reses = session.scalars(stmt).fetchall()
    for res in reses:
        print(res.__dict__)
    # print(reses[-1].contents[0])
