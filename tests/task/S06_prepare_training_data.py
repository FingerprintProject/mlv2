from pprint import pp

from mlv2.utils import PkLoader, Pipeline, PkSaverFS
from mlv2.vectorize import FpVectSupervised
from mlv2.model import FpVectModel, FpVectModelTrain, FpVectModelTest

pl = Pipeline(filenamePrefix="pipeline_S06")
saver = PkSaverFS(folderNamePrefix="S06")


def prepare_training_data():
    # Load fpSupervised
    pkLoader1 = PkLoader()
    folderPath = "./save/S05_2024-10-28_05-48-58"
    pkLoader1.fit(folderPath=folderPath)
    fpVectSup: FpVectSupervised = pkLoader1.get(["FpVectSupervised"])

    # Trainer
    fpVectModelAll = FpVectModel(pipeline=pl)
    X = fpVectSup.getX()
    y = fpVectSup.getLabels()

    fpVectModelAll.fit(
        XArr=[X],
        yArr=[y],
        mode="ALL",
        **fpVectSup.getIds(),
        info=dict(src=fpVectSup.uuid, mode="ALL"),
    )

    fpVectModelAll.trainTestSplit()
    fpVectModelAll.getLabelStats(queryMode="ALL_DATA")
    fpVectModelAll.getLabelStats(queryMode="TRAIN_DATA")
    fpVectModelAll.getLabelStats(queryMode="TEST_DATA")

    X_train = fpVectModelAll.getX(queryMode="TRAIN_DATA")
    X_test = fpVectModelAll.getX(queryMode="TEST_DATA")
    y_train = fpVectModelAll.getLabels(queryMode="TRAIN_DATA")
    y_test = fpVectModelAll.getLabels(queryMode="TEST_DATA")

    fpVectModelTrain = FpVectModelTrain(pipeline=pl)
    fpVectModelTrain.fit(
        XArr=[X_train],
        yArr=[y_train],
        mode="TRAIN",
        **fpVectModelAll.getIds(),
        info=dict(src=fpVectModelAll.uuid, mode="TRAIN"),
    )

    fpVectModelTest = FpVectModelTest(pipeline=pl)
    fpVectModelTest.fit(
        XArr=[X_test],
        yArr=[y_test],
        mode="TEST",
        **fpVectModelAll.getIds(),
        info=dict(src=fpVectModelAll.uuid, mode="TEST"),
    )

    fpVectModelTrain.SMOTE()
    pl.excel()
    saver.save([fpVectModelTrain, fpVectModelAll, fpVectModelTest])
    pass
