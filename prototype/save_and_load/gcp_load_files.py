from pprint import pp
import os
import pathlib

from mlv2.preprocess import LE, FpDict, FpLoader
from mlv2.utils import Pipeline, SaverFS, SaverGCP, Logger
from google.auth import default
from mlv2.db import FpModelRepository, getLocalDbCredential, getLocalSessionFactory

# Saver
curPath = os.getcwd()
parPath = pathlib.Path(curPath)
dotEnvPath = os.path.join(parPath, ".env.dev")
Session = getLocalSessionFactory(**getLocalDbCredential(dotEnvPath))
repo = FpModelRepository()
hospitalId = 30
