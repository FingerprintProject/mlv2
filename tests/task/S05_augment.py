from pprint import pp

from mlv2.preprocess import FpLoader, FpDict
from mlv2.utils import PkLoader, Pipeline, PkSaver
from mlv2.vectorize import FpVectUnsupervised, FpVectSupervised
from mlv2.augment import TaggerDistanceSimple

pl = Pipeline(filenamePrefix="pipeline_S05")
saver = PkSaver(folderNamePrefix="S05")


def augment():
    # Load fpSupervised
    pkLoader1 = PkLoader()
    folderPath = "./save/S03_2024-10-26_16-21-17"
    pkLoader1.fit(folderPath=folderPath)
    fpVectSup: FpVectSupervised = pkLoader1.get(["FpVectSupervised"])

    # Load fpUnsupervised
    pkLoader1 = PkLoader()
    folderPath = "./save/S04_2024-10-26_16-21-40"
    pkLoader1.fit(folderPath=folderPath)
    fpVectUnsup: FpVectUnsupervised = pkLoader1.get(["FpVectUnsupervised"])

    # Augment
    cX, cy, cDistNn = fpVectSup.getZoneCentroidInfo()
    uFp = fpVectUnsup.getX()

    tagger = TaggerDistanceSimple(pl=pl)
    tagger.fit(
        cX=cX,
        cDistNn=cDistNn,
        cy=cy,
        uFp=uFp,
        id_fpVectSupervised=fpVectSup.uuid,
        id_fpVectUnsupervised=fpVectUnsup,
    )

    # pl.excel()
    # saver.save([fpVectUnsup])
    pass
