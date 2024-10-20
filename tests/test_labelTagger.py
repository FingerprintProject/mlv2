from mlv2.augment.labelTagger import LabelTagger
import pandas as pd
import numpy as np
import random


def test_labelTagger():
    ncol = 20
    nrows = 10
    nZones = 3

    cols = [f"W{i+1}" for i in range(ncol)]
    X = pd.DataFrame(np.random.random(size=(nrows, ncol)), columns=cols)
    y = [random.randint(0, nZones - 1) for i in range(nrows)]
    y = pd.Series(y)

    labelTagger = LabelTagger()
    labelTagger.fit(X=X, y=y)
    labelTagger.calcDmCentroid()
    labelTagger.cal_min_dist_neighbors()
    assert True
