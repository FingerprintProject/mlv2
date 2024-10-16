import json
import logging
import pathlib
import pprint
import sys
from typing import Dict, List, Optional
from uuid import uuid4
import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from pydantic import BaseModel, ConfigDict, Field, validate_call

# https://stackoverflow.com/a/68730946
PACKAGE_PARENT = pathlib.Path(__file__).parent
SCRIPT_DIR = PACKAGE_PARENT / "classes"
sys.path.append(str(SCRIPT_DIR))
from fpUtils import getLogger, initLogging, logPipeline

logger = getLogger(__name__)


class Embed(BaseModel):
    vectorSize: int = 50
    window: int = 5
    minCount: int = 1
    workers: int = 4
    sg: int = 0
    embBuildMethod: str = "weighted"
    model: Optional[Word2Vec] = None
    isTrained: bool = False

    # Config
    model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: str = Field(default_factory=lambda: uuid4().hex)
    pipeline: Dict = {}
    initInfo: Dict = {}
    logger: logging.Logger = logging.getLogger(__name__)

    def pipelineInitInfo(self):
        return json.dumps(dict(vectorSize=self.vectorSize))

    @logPipeline(init=True)
    def model_post_init(self, __context) -> None:
        pass

    @logPipeline(includeArgs=False)
    @validate_call
    def fit(self, corpus: List[List[str]]):
        self.model = Word2Vec(
            sg=self.sg,
            sentences=corpus,
            vector_size=self.vectorSize,
            window=self.window,
            min_count=self.minCount,
            workers=self.workers,
        )
        self.isTrained = True

    @logPipeline(includeArgs=False)
    @validate_call
    def generate_embedding(self, dictArray: List[Dict]):
        w2v = self.model

        vocab = [v for v in w2v.wv.key_to_index.keys()]
        tempArray1 = []
        for el in dictArray:
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
        return rpEmbed


# Testing
from mlv2.embed.corpus import createCorpus

if __name__ == "__main__":

    initLogging()
    corpus, survey = createCorpus()

    embed = Embed()

    embed.fit(corpus.corpus)

    embed.generate_embedding(survey.genFPForCorpusBuilder())

    pprint.pprint(embed.pipeline)
    pass
