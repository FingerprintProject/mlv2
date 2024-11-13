from pprint import pp

from mlv2.vectorize import FpVectUnsupervised, FpVectSupervised
from mlv2.augment import TaggerDistanceSimple

from .S00_common import setupTask, hospitalId


def augment():
    pl, lg, saver, loader = setupTask(hospitalId=hospitalId, modelName="S05")
    # Load fpSupervised
    loader.fitFromModelName(name="S03")
    fpVectSup: FpVectSupervised = loader.pick(["FpVectSupervised"])

    # Load fpUnsupervised
    loader.fitFromModelName(name="S04")
    fpVectUnsup: FpVectUnsupervised = loader.pick(["FpVectUnsupervised"])

    # Augment
    cX, cy, cDistNn = fpVectSup.getZoneCentroidInfo()
    uFp = fpVectUnsup.getX()

    tagger = TaggerDistanceSimple(pipeline=pl, logger=lg)
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

    fpVectSupComb = FpVectSupervised(pipeline=pl, logger=lg)
    fpVectSupComb.fit(XArr=[X1, X2], yArr=[y1, y2], **fpVectSup.getIds())
    fpVectSupComb.getLabelStats()

    saver.savePickle([fpVectSupComb], makeActive=True)
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
