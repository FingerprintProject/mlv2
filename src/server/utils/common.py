import hashlib 
from dotenv import load_dotenv
import os

#load_dotenv()
PREDEFINED_TOKEN_HASH = (
    "ee5050a452bc4b251450ed777ab72d4ebed254a5956d4399eedc1d8d311ab00a"
)

# PREDEFINED_TOKEN_HASH = (
#     os.getenv("PREDEFINED_TOKEN_HASH")
# )


def hashString(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()
