import hashlib


def hashString(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()


print(hashString("1234"))
