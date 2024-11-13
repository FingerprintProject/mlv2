import datetime
import os
import pprint
import reprlib
import time
from functools import wraps
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, validate_call

# from pympler.asizeof import asizeof
from .asizeof import (
    asizeof,
)  # Need the patched version due to this issue https://github.com/pympler/pympler/issues/151#issuecomment-2302230861

UUID_TRUNCATE = 8


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

            # Logging
            # size = asizeof(data) / 1e6
            # self.logger.info(
            #     f"<{type(self).__name__}>.{func.__name__} took {total_time:.4f} seconds. [Size: {size:.2f} MB]"
            # )

            self.logger.info(
                f"<{type(self).__name__}>.{func.__name__} took {total_time:.4f} seconds."
            )

            return result

        return function_wrapper_2

    return function_wrapper_1


class Pipeline(BaseModel):

    data: List[Dict] = []
    model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: str = Field(default_factory=lambda: uuid4().hex[:UUID_TRUNCATE])
    filename: Optional[str] = None
    filenamePrefix: str = "pipeline"
    outFolder: str = "./tmp"
    now: datetime.datetime = Field(default_factory=datetime.datetime.now)
    # This provides a means for producing object representations with limits on the size of the resulting strings.
    printer: Optional[reprlib.Repr] = None
    indent: int = 1
    maxlevel: int = 3

    def __repr__(self):
        return "Pipeline"

    def __str__(self):
        return self.__repr__()

    def model_post_init(self, __context):
        self.printer = reprlib.Repr(indent=self.indent, maxlevel=self.maxlevel)
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

        # Take care of class without uuid attribute.
        uuid = classInst.uuid if hasattr(classInst, "uuid") else ""

        data = dict(
            datetime=now.strftime("%Y-%m-%d %H:%M:%S"),
            timestamp=datetime.datetime.timestamp(now),
            className=type(classInst).__name__,
            uuid=uuid,
            classInst=self.stringify(classInst) if printClassInst else "",
            funcName=funcName,
            args=self.stringify(args),
            kwargs=self.stringify(kwargs),
            info=self.stringify(info),
            pipelineId=self.uuid,
        )
        self.data.append(data)

    def stringify(self, obj):
        size = asizeof(obj) / 1e6  # Mb
        if size > 0.5:
            return self.printer.repr(obj)
        else:
            return pprint.pformat(obj)

    def print(self):
        pprint.pp(self.data)

    def excel(self):
        if not os.path.exists(self.outFolder):
            os.mkdir(self.outFolder)
        suffix = self.now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.filenamePrefix}_{suffix}.xlsx"
        self.filename = filename
        filepath = os.path.join(self.outFolder, filename)
        pd.DataFrame(self.data).to_excel(filepath, index=False)
