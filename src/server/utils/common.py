import hashlib
import os
import pathlib

from dotenv import load_dotenv

ENVIRONMENT = os.getenv("ENVIRONMENT")
if ENVIRONMENT != "CLOUD_RUN":
    curPath = os.getcwd()
    parPath = pathlib.Path(curPath)
    dotEnvPath = os.path.join(parPath, ".env.dev")
    load_dotenv(dotEnvPath, override=True)
    print("LOCAL")

PREDEFINED_TOKEN_HASH = os.getenv("PREDEFINED_TOKEN_HASH")
print(dict(PREDEFINED_TOKEN_HASH=PREDEFINED_TOKEN_HASH))


def hashString(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()
