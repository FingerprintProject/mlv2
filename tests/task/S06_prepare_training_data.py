from pprint import pp

from mlv2.utils import PkLoader, Pipeline, PkSaver
from mlv2.vectorize import FpVectSupervised
from mlv2.learn import FpVectTrain

pl = Pipeline(filenamePrefix="pipeline_S06")
saver = PkSaver(folderNamePrefix="S06")


def prepare_training_data():
    # Load fpSupervised
    pkLoader1 = PkLoader()
    folderPath = "./save/S05_2024-10-27_13-19-50"
    pkLoader1.fit(folderPath=folderPath)
    fpVectSup: FpVectSupervised = pkLoader1.get(["FpVectSupervised"])

    # Trainer
    fpTrain = FpVectTrain()
    X = fpVectSup.getX()
    y = fpVectSup.getLabels()

    fpTrain.fit(
        XArr=[X],
        yArr=[y],
        **fpVectSup.getIds(),
        info=dict(src=fpVectSup.uuid),
    )

    fpTrain.trainTestSplit()
    fpTrain.getLabelStats(queryMode="ALL")
    fpTrain.getLabelStats(queryMode="TRAIN")
    fpTrain.getLabelStats(queryMode="TEST")

    # pl.excel()
    # saver.save([fpTrain])
    pass
