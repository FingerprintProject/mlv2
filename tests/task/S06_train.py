from pprint import pp

from mlv2.preprocess import FpLoader, FpDict
from mlv2.utils import PkLoader, Pipeline, PkSaver
from mlv2.vectorize import FpVectUnsupervised, FpVectSupervised
from mlv2.augment import TaggerDistanceSimple
from mlv2.predict import FpTrain

pl = Pipeline(filenamePrefix="pipeline_S06")
saver = PkSaver(folderNamePrefix="S06")


def train():
    # Load fpSupervised
    pkLoader1 = PkLoader()
    folderPath = "./save/S05_2024-10-27_13-19-50"
    pkLoader1.fit(folderPath=folderPath)
    fpVectSup: FpVectSupervised = pkLoader1.get(["FpVectSupervised"])

    # Trainer
    fpTrain = FpTrain()
    X = fpVectSup.getX()
    y = fpVectSup.getLabels()

    fpTrain.fit(
        XArr=[X],
        yArr=[y],
        id_vectorizer=fpVectSup.id_vectorizer,
        id_leBssid=fpVectSup.id_leBssid,
        id_leZone=fpVectSup.id_leZone,
        info=dict(src=fpVectSup.uuid),
    )

    fpTrain.trainTestSplit()
    fpTrain.getLabelStats(mode="ALL")
    fpTrain.getLabelStats(mode="TRAIN")
    fpTrain.getLabelStats(mode="TEST")

    # pl.excel()
    # saver.save([fpVectSupComb])
    pass
