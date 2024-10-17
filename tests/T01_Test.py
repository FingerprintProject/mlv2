import pickle
from pympler import asizeof
from mlv2.utils.pipeline import CustomPrint
import json
import reprlib
import numpy as np

obj1 = {
    "key_1": [
        "EG8XYD9FVN",
        "S2WARDCVAO",
        "J00YCU55DP",
        "R07BUIF2F7",
        "VGPS1JD0UM",
        "WL3TWSDP8E",
        "LD8QY7DMJ3",
        "J36U3Z9KOQ",
        "KU2FUGYB2U",
        "JF3RQ315BY",
    ],
    "key_2": [
        "162LO154PM",
        "3ROAV881V2",
        "I4T79LP18J",
        "WBD36EM6QL",
        "DEIODVQU46",
        "KWSJA5WDKQ",
        "WX9SVRFO0G",
        "6UN63WU64G",
        "3Z89U7XM60",
        "167CYON6YN",
    ],
    # Test case to make sure we didn't break handling of recursive structures
    "key_3": [
        "162LO154PM",
        "3ROAV881V2",
        [1, 2, ["a", "b", "c"], 3, 4, 5, 6, 7],
        "KWSJA5WDKQ",
        "WX9SVRFO0G",
        "6UN63WU64G",
        "3Z89U7XM60",
        "167CYON6YN",
    ],
}

obj2 = np.random.random(size=(100, 100))


aRepr = reprlib.Repr(indent=1, maxlevel=3)
data = aRepr.repr(obj1)
with open("data.txt", "w") as f:
    f.write(data)


# # Load pickle
# filePath = "C:/Users/nnnpo/Coding/fingerprint/mlv2/save/embed_2024-10-17_17-59-16/LE_d1d8c.pickle"
# with open(filePath, "rb") as handle:
#     data = pickle.load(handle)

# print(asizeof.asizeof(data))

# import json

# with open("data.json", "w") as f:
#     json.dump(data.pipeline.data[9], f)


# with open("pk.pickle", "wb") as handle:
#     pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
# pass
