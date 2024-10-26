import pandas as pd


def fit(self, X: pd.DataFrame, y: pd.Series):
    # Check if index of X and y is the same
    idxDiff = X.index.difference(y.index).values.shape[0]
    if idxDiff > 0:
        raise Exception("X and y have difference indices")
    y.name = "y"
    self.data = pd.concat([y, X], axis=1)
    self.colX = X.columns.values.tolist()
