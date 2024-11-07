import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase


class SaBase(DeclarativeBase):
    pass


class FpModel(SaBase):
    __tablename__ = "fp_models"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    path = sa.Column(sa.String)
    hospital_id = sa.Column(sa.Integer)
    model_type = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime)
