import json
import pickle
from pprint import pp

# Load pickle
filePath = "save/embed_2024-10-18_08-55-20/W2V_8632d.pickle"
with open(filePath, "rb") as handle:
    data = pickle.load(handle)

pp(data)

# with open("data.json", "w") as f:
#     json.dump(data.pipeline.data[9], f)

# with open("pk.pickle", "wb") as handle:
#     pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
# pass
