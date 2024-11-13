from pprint import pp
from mlv2.model import FpVectModel, FpVectModelTest, FpVectModelTrain, ModelLr
from .S00_common import setupTask, hospitalId


def training():
    pl, lg, saver, loader = setupTask(hospitalId=hospitalId, modelName="S07")

    # Load data
    loader.fitFromModelName(name="S06")
    fpVectModel: FpVectModel = loader.pick(["FpVectModel_"])
    fpVectModelTrain: FpVectModelTrain = loader.pick(["FpVectModelTrain_"])
    fpVectModelTest: FpVectModelTest = loader.pick(["FpVectModelTest_"])

    modelLr = ModelLr(pipeline=pl, logger=lg)
    modelLr.fit(
        X_train=fpVectModelTrain.getX(),
        y_train=fpVectModelTrain.getLabels(),
        info=dict(src=fpVectModelTrain.uuid),
    )

    dfReport, dfProblem = modelLr.calculateMetrices(
        X_test=fpVectModelTest.getX(),
        y_test=fpVectModelTest.getLabels(),
        info=dict(src=fpVectModelTest.uuid),
    )

    # Final model
    modelLrFinal = ModelLr(pipeline=pl, logger=lg, **fpVectModel.getIds())
    modelLrFinal.fit(
        X_train=fpVectModel.getX(),
        y_train=fpVectModel.getLabels(),
        info=dict(src=fpVectModel.uuid),
    )

    # Load additional class instance for prediction
    # path = "save_V2\\15\\S01_2024-11-13_10-09-12"
    # loader.fitFromPath(path=path)
    loader.fitFromModelName(name="S01")
    leBssid = loader.pick(["LE"])
    w2v = loader.pick(["W2V"])

    # path = "save_V2\\15\\S02_2024-11-13_12-38-37"
    # loader.fitFromPath(path=path)
    loader.fitFromModelName(name="S02")
    leZone = loader.pick(["LE"])

    pl.excel()
    saver.savePickle([modelLrFinal, leBssid, leZone, w2v], makeActive=True)
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
