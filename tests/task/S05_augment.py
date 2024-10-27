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

    tagger = TaggerDistanceSimple(pipeline=pl)
    tagger.fit(
        cX=cX,
        cDistNn=cDistNn,
        cy=cy,
        uFp=uFp,
        id_fpVectSupervised=fpVectSup.uuid,
        id_fpVectUnsupervised=fpVectUnsup,
    )

    # Combined
    X1 = fpVectSup.getX()
    y1 = fpVectSup.getLabels()
    X2 = tagger.getX()
    y2 = tagger.getLabels()

    fpVectSupComb = FpVectSupervised(pipeline=pl)
    fpVectSupComb.fit(
        XArr=[X1, X2],
        yArr=[y1, y2],
        id_vectorizer=fpVectSup.id_vectorizer,
        id_leBssid=fpVectSup.id_leBssid,
        id_leZone=fpVectSup.id_leZone,
        info=dict(src=[fpVectSup.uuid, tagger.uuid]),
    )
    fpVectSupComb.getLabelStats()

    pl.excel()
    saver.save([fpVectSupComb])
