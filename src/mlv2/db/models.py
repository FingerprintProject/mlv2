from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class SaBase(DeclarativeBase):
    pass


class FpModel(SaBase):
    __tablename__ = "fp_models"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    hospitalId = Column("hospital_id", Integer)
    className = Column("class_name", String)
    instanceId = Column("instance_id", String)
    createdAt = Column("created_at", DateTime(timezone=True), server_default=func.now())
