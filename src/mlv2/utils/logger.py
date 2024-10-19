import logging
import os
from logging import handlers
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

STACKLEVEL = 2


class Logger(BaseModel):

    logger: Optional[logging.Logger] = None
    name: str = __name__
    filename: str = "logs.txt"
    logFolder: str = "./logs"
    level: str = Field(pattern=r"debug|info|warning|error|critical", default="debug")
    when: str = "D"
    backCount: int = 3
    fmtFile: str = (
        "%(asctime)s - %(filename)s - [%(filename)s:%(lineno)d] : %(message)s"
    )
    fmtConsole: str = "%(name)s - %(levelname)s - %(message)s"
    levelRelations: Dict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __repr__(self):
        return "Logger"

    def __str__(self):
        return self.__repr__()

    def model_post_init(self, __context):
        if not os.path.exists(self.logFolder):
            os.mkdir(self.logFolder)

        filepath = os.path.join(self.logFolder, self.filename)

        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(
            self.levelRelations.get(self.level)
        )  # Setting the log level
        self.logger.handlers.clear()  # Prevent adding duplicated handler when multiple class instances initialize logger with the same name.

        # Console output
        fmtStrConsole = logging.Formatter(self.fmtConsole)  # Setting the log format
        csh = logging.StreamHandler()  # on-screen output
        csh.setFormatter(fmtStrConsole)  # Setting the format
        self.logger.addHandler(csh)

        # File output
        trfh = handlers.TimedRotatingFileHandler(
            filename=filepath,
            when=self.when,
            backupCount=self.backCount,
            encoding="utf-8",
        )  # automatically generates the file at specified intervals
        fmtStrFile = logging.Formatter(self.fmtFile)  # Setting the log format
        trfh.setFormatter(fmtStrFile)  # Setting the format
        self.logger.addHandler(trfh)  # Add the object to the logger

    def debug(self, msg):
        self.logger.debug(
            msg, **dict(stacklevel=STACKLEVEL)
        )  # Stacklevel is used to display correct location information of the actual caller.

    def info(self, msg):
        self.logger.info(msg, **dict(stacklevel=STACKLEVEL))

    def warning(self, msg):
        self.logger.warning(msg, **dict(stacklevel=STACKLEVEL))

    def error(self, msg):
        self.logger.error(msg, **dict(stacklevel=STACKLEVEL))

    def critical(self, msg):
        self.logger.critical(msg, **dict(stacklevel=STACKLEVEL))


def main():
    log1 = Logger()
    log1.debug("This is a debug message")
    log1.info("This is an info message")
    log1.warning("This is a warning message")
    log1.error("This is an error message")
    log1.critical("This is a critical message")

    log2 = Logger(name=f"{__name__}.error", level="debug")
    log2.debug("This is a debug message")
    log2.info("This is an info message")
    log2.warning("This is a warning message")
    log2.error("This is an error message")
    log2.critical("This is a critical message")


if __name__ == "__main__":
    main()
