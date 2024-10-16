import datetime
import os
import pprint
import time
from functools import wraps
from typing import Any, Dict, List
from uuid import uuid4

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, validate_call


def logPipeline():
    """Log details in self.pipline and measure time"""

    def function_wrapper_1(func):
        @wraps(func)
        def function_wrapper_2(self, *args, **kwargs):

            # Enforce class attribuites
            if not hasattr(self, "pipeline"):
                raise Exception("No pipeline")

            funcName = func.__name__

            # If init function, print class instance.
            if funcName in ["model_post_init", "__init__"]:
                printClassInst = True
            else:
                printClassInst = False

            infoDict = kwargs.get("info")
            if infoDict:
                # Store info into class instance
                if hasattr(self, "addInfo"):
                    self.addInfo(infoDict)
            else:
                infoDict = {}

            # Store additional info
            data = dict(
                classInst=self,
                funcName=func.__name__,
                args=args,
                kwargs=kwargs,
                info=infoDict,
                printClassInst=printClassInst,
            )
            self.pipeline.log(**data)
            start_time = time.perf_counter()
            # Start function run
            result = func(self, *args, **kwargs)
            # End function run
            end_time = time.perf_counter()
            total_time = end_time - start_time

            self.logger.info(
                f"<{type(self).__name__}>.{func.__name__} took {total_time:.4f} seconds"
            )

            return result

        return function_wrapper_2

    return function_wrapper_1


class Pipeline(BaseModel):

    data: List[Dict] = []
    model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: str = Field(default_factory=lambda: uuid4().hex)
    filename: str = "pipeline.xlsx"
    outFolder: str = "./logs"

    def __repr__(self):
        return "Pipeline"

    def __str__(self):
        return self.__repr__()

    def model_post_init(self, __context):
        pass

    @validate_call
    def log(
        self,
        classInst: Any,
        funcName: str,
        args: List = [],
        kwargs: Dict = {},
        info: Dict = {},
        printClassInst=False,
    ):
        now = datetime.datetime.now()
        data = dict(
            datetime=now.strftime("%Y-%m-%d %H:%M:%S"),
            timestamp=datetime.datetime.timestamp(now),
            className=type(classInst).__name__,
            uuid=classInst.uuid,
            classInst=pprint.pformat(classInst, depth=1) if printClassInst else "",
            funcName=funcName,
            args=pprint.saferepr(args),
            kwargs=pprint.saferepr(kwargs),
            info=pprint.saferepr(info),
            pipelineId=self.uuid,
        )
        self.data.append(data)

    def print(self):
        pprint.pp(self.data)

    def excel(self):
        if not os.path.exists(self.outFolder):
            os.mkdir(self.logFolder)
        filepath = os.path.join(self.outFolder, self.filename)
        pd.DataFrame(self.data).to_excel(filepath, index=False)


if __name__ == "__main__":
    pass
