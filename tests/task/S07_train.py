from pprint import pp

from mlv2.utils import PkLoader, Pipeline, SaverFS
from mlv2.model import FpVectModel, FpVectModelTrain, FpVectModelTest, ModelLr

pl = Pipeline(filenamePrefix="pipeline_S07")
saver = SaverFS(folderNamePrefix="S07")


def training():
    # Load data
    pkLoader1 = PkLoader()
    folderPath = "./save/S06_2024-10-28_16-02-19"
    pkLoader1.fit(folderPath=folderPath)
    fpVectModel: FpVectModel = pkLoader1.get(["FpVectModel_"])
    fpVectModelTrain: FpVectModelTrain = pkLoader1.get(["FpVectModelTrain_"])
    fpVectModelTest: FpVectModelTest = pkLoader1.get(["FpVectModelTest_"])

    modelLr = ModelLr(pipeline=pl)
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
    saver.save([modelLrFinal])
    pass
