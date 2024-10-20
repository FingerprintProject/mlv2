from mlv2.augment.labelTagger import LabelTagger
import pandas as pd
import numpy as np
import random


def test_labelTagger():
    ncol = 10
    cols = [f"W{i+1}" for i in range(ncol)]
    X = pd.DataFrame(np.random.random(size=(100, ncol)), columns=cols)
    y = [random.randint(0, 9) for i in range(X.shape[0])]
    y = pd.Series(y)
    ltag = LabelTagger()
    ltag.fit(X=X, y=y)
    ltag.calc_obs()
    assert True
