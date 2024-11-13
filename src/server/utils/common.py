import hashlib

PREDEFINED_TOKEN_HASH = (
    "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
)


def hashString(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()
