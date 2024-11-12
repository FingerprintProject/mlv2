import sqlalchemy as sa
from getLocalSessionFactory import LocalSession
from mlv2.record import FpModel

# Read
# stmt = sa.select(FpModel).where(FpModel.name.like("%CRH%"))
# print(stmt)
# with LocalSession() as session:
#     reses = session.scalars(stmt).fetchall()
#     for res in reses:
#         print(res.__dict__)


# hospitalId = 30
# path = "V2_HID_30/S00_2024-11-12_05-18-15"
# stmt = sa.select(FpModel).where(
#     (FpModel.hospitalId == hospitalId) & (FpModel.path == path)
# )
# print(stmt)
# print("----------")
# with LocalSession() as session:
#     reses = session.scalars(stmt).fetchall()
#     for res in reses:
#         print(res.__dict__)
#         print("----------")
# pass


# Write
# newModel = FpModel(name="TEST", hospitalId=16, path="NEW_PATH", contents=[dict(a=10)])

# with LocalSession() as session, session.begin():
#     session.add_all([newModel])
#     stmt = sa.select(FpModel)
#     reses = session.scalars(stmt).fetchall()
#     for res in reses:
#         print(res.__dict__)
#     # print(reses[-1].contents[0])

# Update


# hospitalId = 30
# path = "V2_HID_30/S00_2024-11-12_05-18-15"
# stmt = sa.select(FpModel).where(
#     (FpModel.hospitalId == hospitalId) & (FpModel.path == path)
# )
# print(stmt)
# print("----------")
# with LocalSession() as session, session.begin():
#     reses = session.scalars(stmt).fetchall()
#     reses[0].contents = dict(a=10)
# pass


# Active
hospitalId = 30
path = "V2_HID_30/S00_2024-11-12_05-18-15"
name = "S00"

stmt = (
    sa.select(FpModel)
    .where(
        (FpModel.hospitalId == hospitalId)
        & (FpModel.name == name)
        & (FpModel.isActive == False)
    )
    .order_by(FpModel.createdAt.asc())
)

print(stmt)
print("----------")
with LocalSession() as session, session.begin():
    reses = session.scalars(stmt).fetchall()
    for res in reses:
        print(res.createdAt)
        res.isActive = True
pass
