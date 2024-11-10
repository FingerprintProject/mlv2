import sqlalchemy as sa
from getSessionFactory import LocalSession
from mlv2.db import FpModel

# Read
# stmt = sa.select(FpModel).where(FpModel.name.like("%CRH%"))
# print(stmt)
# with LocalSession() as session, session.begin():
#     reses = session.scalars(stmt).fetchall()
#     for res in reses:
#         print(res.name, res.model_type)


# stmt = sa.select(FpModel).where(FpModel.className == "LE")
# print(stmt)
# with LocalSession() as session, session.begin():
#     reses = session.scalars(stmt).fetchall()
#     for res in reses:
#         print(res.__dict__)
pass


# Write
# newModel = FpModel(name="TEST", hospital_id=16, path="NEW_PATH", model_type="V2")

# with LocalSession() as session, session.begin():
#     session.add_all([newModel])
#     stmt = sa.select(FpModel)
#     reses = session.scalars(stmt).fetchall()
#     for res in reses:
#         print(res.name, res.model_type, type(res.model_type))
