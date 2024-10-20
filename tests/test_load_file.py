import pickle


def load_file():
    # Load pickle
    filePath = "save/S01_2024-10-20_07-11-09/W2V_231fe.pickle"
    with open(filePath, "rb") as handle:
        data = pickle.load(handle)

    return data


def test_load_File():
    assert load_file() is not None
