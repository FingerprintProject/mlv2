import os
import pathlib
from mlv2.record import FpModelRepository, getLocalDbCredential, getLocalSessionFactory

curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))


def test_db_read():
    repo = FpModelRepository()
    reses = repo.findAll(Session=Session)
    for res in reses:
        print(res.name)


def test_db_write():
    repo = FpModelRepository()
    dataArr = [
        dict(
            name="TEST",
            path="/TEST/TEST",
            hospitalId=15,
            className="LE",
            instanceId="ID",
        )
    ]
    repo.insert(Session=Session, dataArr=dataArr)


def test_db_write_incorrect():
    repo = FpModelRepository()
    dataArr = [
        dict(
            name="TEST",
            path="/TEST/TEST",
            hospitalId=15,
            className="LE",
            # instanceId="ID",
        )
    ]
    repo.insert(Session=Session, dataArr=dataArr)
