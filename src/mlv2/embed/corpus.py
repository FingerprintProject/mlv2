import csv
from typing import Dict, List
from mlv2.utils import logPipeline, FpBaseModel

import numpy as np
from pydantic import Field


class Corpus(FpBaseModel):
    data: List[Dict[str, int]]
    corpusBuildMethod: str = Field(pattern=r"^NR_random$", default="NR_random")
    corpusFilePath: str = "./corpus.txt"
    corpusLineRepeat: int = 1
    corpus: List[str] = []

    @logPipeline()
    def model_post_init(self, __context) -> None:
        self.generate_corpus()
        self.save_corpus()

    def getWapRepeat(self, level: int):
        """Determine the number in which the BSSID is repeated in one corpus line"""

        if self.corpusBuildMethod == "NR_random":
            return np.ceil(level + 100)
        else:
            return int(level)

    @logPipeline()
    def generate_corpus(self):
        corpus = []
        for el in self.data[:]:
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
