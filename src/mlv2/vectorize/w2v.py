from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from pydantic import validate_call

from ..utils import logPipeline, FpBaseModel


class W2V(FpBaseModel):
    vectorSize: int = 50
    window: int = 5
    minCount: int = 1
    workers: int = 4
    sg: int = 0
    embBuildMethod: str = "weighted"
    model: Optional[Word2Vec] = None
    id_leBssid: Optional[str] = None

    @logPipeline()
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline()
    @validate_call
    def fit(self, corpus: List[List[str]], id_leBssid: str, info={}):
        self.preventRefit()
        self.model = Word2Vec(
            sg=self.sg,
            sentences=corpus,
            vector_size=self.vectorSize,
            window=self.window,
            min_count=self.minCount,
            workers=self.workers,
        )
        self.id_leBssid = id_leBssid
        self.isFitted = True

    @logPipeline()
    @validate_call
    def vectorize(self, data: List[Dict], info={}):
        w2v = self.model

        vocab = [v for v in w2v.wv.key_to_index.keys()]
        tempArray1 = []
        for el in data:
            sr = pd.Series(el, dtype=object)
            # Check whether the WAP is in the vocab or not.
            filtVocab = sr.index.isin(vocab)
            if (~filtVocab).any():
                self.logger.warning(
                    f"Found out of vocab WAP: {sr[~filtVocab].index.values}"
                )
            # Filter out-of-vocab WAP
            sr = sr[filtVocab]
            if self.embBuildMethod == "weighted":
                sr = sr / sr.sum()
            elif self.embBuildMethod == "mean":
                sr.iloc[:] = 1 / sr.shape[0]
            else:
                raise Exception("Unknown emb_build_method.")
            tempArray2 = []
            for k, v in sr.to_dict().items():
                tempArray2.append(np.array(w2v.wv[k]).reshape(1, -1) * v)
            if tempArray2 == []:
                vecArray = tempArray2
            else:
                vecArray = np.concatenate(tempArray2, axis=0).sum(axis=0).reshape(1, -1)
            tempArray1.append(vecArray)
        if tempArray1 == []:
            rpEmbed = []
        else:
            rpEmbed = np.concatenate(tempArray1, axis=0)
        cols = [f"E{i+1}" for i in range(self.vectorSize)]
        dft = pd.DataFrame(data=rpEmbed, columns=cols)
        return dft
