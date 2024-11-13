from pprint import pp

from mlv2.vectorize import FpVectSupervised
from mlv2.model import FpVectModel, FpVectModelTrain, FpVectModelTest
from .S00_common import setupTask


def prepare_training_data():
    pl, lg, saver, loader = setupTask(hospitalId=30, modelName="S06")

    # Load fpSupervised
    loader.fitFromModelName(name="S05")
    fpVectSup: FpVectSupervised = loader.pick(["FpVectSupervised"])

    # Trainer
    fpVectModelAll = FpVectModel(pipeline=pl, logger=lg)
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

    fpVectModelTest = FpVectModelTest(pipeline=pl, logger=lg)
    fpVectModelTest.fit(
        XArr=[X_test],
        yArr=[y_test],
        mode="TEST",
        **fpVectModelAll.getIds(),
        info=dict(src=fpVectModelAll.uuid, mode="TEST"),
    )

    fpVectModelTrain.SMOTE()
    saver.savePickle(
        [fpVectModelTrain, fpVectModelAll, fpVectModelTest], makeActive=True
    )
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
