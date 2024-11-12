from typing import List, Union

import sqlalchemy as sa
from pydantic import validate_call
from sqlalchemy.orm import Session, sessionmaker
from typing_extensions import TypedDict

from mlv2.utils import FpBaseModel
from .dbModels import FpModel


class JsonSchemaInsert(TypedDict):
    className: str
    path: str
    instanceId: str
    fileName: str


class DtoInsert(TypedDict):
    name: str
    path: str
    hospitalId: int
    contents: List[JsonSchemaInsert]
    makeActive: bool


class DtoGetRecord(TypedDict):
    name: str
    hospitalId: int


class FpModelRepository(FpBaseModel):
    Session: Union[Session, sessionmaker]

    def findAll(self):
        stmt = sa.select(FpModel)
        with self.Session() as session:
            results = session.scalars(stmt).fetchall()
        return results

    def findByInstanceId(self, Session, instanceId):
        stmt = sa.select(FpModel).where(FpModel.className == "LE")
        with self.Session() as session:
            results = session.scalars(stmt).fetchall()
        return results

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def insertModelRecord(self, data: DtoInsert):
        hospitalId = data["hospitalId"]
        path = data["path"]
        contents = data["contents"]
        name = data["name"]
        makeActive = data["makeActive"]

        if makeActive:
            with self.Session() as session, session.begin():
                # Make every row inactive first
                stmt = sa.select(FpModel).where(
                    (FpModel.hospitalId == hospitalId) & (FpModel.name == name)
                )
                reses: List[FpModel] = session.scalars(stmt).fetchall()
                for res in reses:
                    res.isActive = False

        with self.Session() as session, session.begin():
            # Check to see if the record exists
            stmt = sa.select(FpModel).where(
                (FpModel.hospitalId == hospitalId) & (FpModel.path == path)
            )
            reses: List[FpModel] = session.scalars(stmt).fetchall()
            if len(reses) == 0:
                # Add new record
                session.add(
                    FpModel(
                        hospitalId=hospitalId,
                        path=path,
                        name=name,
                        contents=contents,
                        isActive=makeActive,
                    )
                )
            elif len(reses) == 1:
                # Update record
                oldContents = reses[0].contents
                newContents = [*oldContents, *contents]
                reses[0].contents = newContents
                if makeActive:
                    reses[0].isActive = True
            else:
                self.logger.warning(
                    "Found duplicated rows with the same path and hospitalId. No update occurs."
                )

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def getModelRecord(self, data: DtoGetRecord):
        name = data["name"]
        hospitalId = data["hospitalId"]
        stmtActive = (
            sa.select(FpModel)
            .where(
                (FpModel.hospitalId == hospitalId)
                & (FpModel.name == name)
                & (FpModel.isActive == True)
            )
            .order_by(FpModel.createdAt.asc())
        )

        with self.Session() as session, session.begin():
            resesActive: List[FpModel] = session.scalars(stmtActive).fetchall()
            if len(resesActive) == 0:
                raise Exception("No active model")

            if len(resesActive) > 1:
                self.logger.warning("Found multiple active models. Choose latest model")

            res = resesActive[-1]

            pickleContents = [*filter(lambda x: "pickle" in x["path"], res.contents)]
            return pickleContents
