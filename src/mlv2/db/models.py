from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
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
    createdAt = Column("created_at", DateTime(timezone=True), server_default=func.now())
    contents = Column("contents", JSONB)
