from pprint import pp

from mlv2.preprocess import FpLoader, FpDict
from mlv2.utils import PkLoader, Pipeline, PkSaver
from mlv2.vectorize import FpVectUnsupervised

pl = Pipeline(filenamePrefix="pipeline_S05")
saver = PkSaver(folderNamePrefix="S05")


def augment():
    # Load fpSupervised
    pkLoader1 = PkLoader()
    folderPath = "./save/S03_2024-10-25_15-26-04"
    pkLoader1.fit(folderPath=folderPath)
    fpVectSupervised = pkLoader1.get(["FpVectSupervised"])

    # Load fpUnsupervised
    pkLoader1 = PkLoader()
    folderPath = "./save/S04_2024-10-26_07-03-00"
    pkLoader1.fit(folderPath=folderPath)
    fpVectSupervised = pkLoader1.get(["FpVectUnsupervised"])

    # pl.excel()
    # saver.save([fpVectUnsup])
    pass
