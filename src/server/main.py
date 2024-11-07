from typing import Union
from mlv2.utils import Pipeline, PkSaverFS
from mlv2.preprocess import LE, FpDict, FpLoader
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test")
def read_test():

    pl = Pipeline(filenamePrefix="pipeline_S01")
    saver = PkSaverFS(folderNamePrefix="S01")
    fpLoader = FpLoader(pipeline=pl)
    return {"result": True}
