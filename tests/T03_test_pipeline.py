from pprint import pp

import numpy as np
from pympler import asizeof

from mlv2.utils.pipeline import Pipeline

pl = Pipeline()

pl.log(classInst=None, funcName="func", args=[], kwargs={}, info={})


big = np.random.random((1000, 1000))
pp(asizeof.asizeof(big))

pl.log(classInst=None, funcName="func", args=[big], kwargs={}, info={})

pp(pl.data)
pp(asizeof.asizeof(pl))
