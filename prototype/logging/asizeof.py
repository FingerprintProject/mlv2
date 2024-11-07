import pympler
import numpy as np
from pprint import pp

from pympler import asizeof

pp(f"pympler.__version__: {pympler.__version__}")
pp(f"asizeof.__version__: {asizeof.__version__}")
# This should cause error
try:
    pp(asizeof.asizeof(np.tile(None, (10, 10))))
except:
    print("Error")

from mlv2.utils.asizeof import asizeof

# This should not cause error
pp(asizeof(np.tile(None, (10, 10))))
