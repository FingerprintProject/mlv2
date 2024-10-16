import csv
from typing import Dict, List, Optional

import numpy as np
from pydantic import Field, validate_call

from mlv2.utils import FpBaseModel, logPipeline


class CorpusBuilder(FpBaseModel):
    corpus: Optional[List[str]] = None
    corpusBuildMethod: str = Field(pattern=r"^NR_random$", default="NR_random")
    corpusFilePath: str = "./corpus.txt"
    corpusLineRepeat: int = 1

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call
    def fit(self, data: List[Dict[str, int]], info={}) -> None:
        self.preventRefit()
        self.generate_corpus(data)
        self.save_corpus()
        self.isFitted = True

    def getWapRepeat(self, level: int):
        """Determine the number in which the BSSID is repeated in one corpus line"""

        if self.corpusBuildMethod == "NR_random":
            return np.ceil(level + 100)
        else:
            return int(level)

    def generate_corpus(self, data):
        corpus = []
        for el in data[:]:
            for _ in np.arange(self.corpusLineRepeat):
                temp = []
                for k, v in el.items():
                    vp = self.getWapRepeat(v)
                    if vp <= 0:
                        temp.append(np.repeat(k, int(1)))
                    else:
                        temp.append(np.repeat(k, int(vp)))
                wordsRow = np.concatenate(temp)

                if self.corpusBuildMethod == "NR_random":
                    np.random.shuffle(wordsRow)

                corpus.append(wordsRow.tolist())
        self.corpus = corpus
        pass

    def save_corpus(self):
        with open(self.corpusFilePath, "w", newline="") as f:
            cw = csv.writer(f, delimiter=" ")
            cw.writerows(self.corpus)


# Testing
def createCorpus():
    pass


if __name__ == "__main__":
    createCorpus()
    pass
