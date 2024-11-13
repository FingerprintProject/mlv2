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
    modelLrFinal = ModelLr(pipeline=pl)
    modelLrFinal.fit(
        X_train=fpVectModel.getX(),
        y_train=fpVectModel.getLabels(),
        info=dict(src=fpVectModel.uuid),
    )

    pl.excel()
    saver.savePickle([modelLrFinal], makeActive=True)
    pl.excel()
    saver.saveFile(
        fileNameArr=[pl.filename, lg.filename], tempFolderPathSource=pl.outFolder
    )
